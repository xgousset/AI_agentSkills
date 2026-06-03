from functools import lru_cache
from uuid import uuid4

from dotenv import load_dotenv
from flask import Flask, abort, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_socketio import SocketIO, emit, join_room

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///checkpoint.db'

db.init_app(app)
socketio = SocketIO(app, async_mode='threading', cors_allowed_origins='*')

load_dotenv()

class Chat(db.Model):
    __tablename__ = 'chats'

    id: Mapped[int] = mapped_column(primary_key=True)
    thread_id: Mapped[str] = mapped_column(unique=True, nullable=False)
    messages: Mapped[list['Message']] = relationship(
        back_populates='chat',
        cascade='all, delete-orphan',
        order_by='Message.id',
    )


class Message(db.Model):
    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey('chats.id'), nullable=False)
    role: Mapped[str] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    chat: Mapped[Chat] = relationship(back_populates='messages')


with app.app_context():
    db.create_all()


def get_all_chats():
    return Chat.query.order_by(Chat.id.desc()).all()


def get_chat_by_thread_id(thread_id):
    return Chat.query.filter_by(thread_id=thread_id).first()


def create_chat():
    chat = Chat(thread_id=str(uuid4()))
    db.session.add(chat)
    db.session.commit()
    return chat


def get_chat_messages(chat):
    return Message.query.filter_by(chat_id=chat.id).order_by(Message.id.asc()).all()


@lru_cache(maxsize=1)
def get_llm():
    backend = (app.config.get('LLM_BACKEND') or 'ollama').strip().lower()
    if backend != 'ollama':
        raise ValueError(f'Unknown backend: {backend}')

    return ChatOllama(
        model=app.config.get('OLLAMA_MODEL') or 'qwen2.5:3b',
        temperature=0,
    )


def build_messages(chat_messages):
    messages = [
        SystemMessage(content='Tu es un assistant utile et concis. Réponds en français.'),
    ]

    for message in chat_messages:
        if message.role == 'user':
            messages.append(HumanMessage(content=message.content))
        else:
            messages.append(AIMessage(content=message.content))

    return messages


def generate_ai_reply(chat):
    try:
        llm = get_llm()
        response = llm.invoke(build_messages(get_chat_messages(chat)))
        content = getattr(response, 'content', '') or ''
        return content.strip() or 'Je n\'ai pas de réponse pour le moment.'
    except Exception as exc:
        return f"L'assistant IA est indisponible pour le moment ({type(exc).__name__})."


def stream_ai_reply(chat):
    reply_parts = []

    try:
        llm = get_llm()
        for chunk in llm.stream(build_messages(get_chat_messages(chat))):
            chunk_text = getattr(chunk, 'content', '') or ''
            if not chunk_text:
                continue

            reply_parts.append(chunk_text)
            emit('assistant_delta', {'content': chunk_text}, room=chat.thread_id)

        reply_text = ''.join(reply_parts).strip() or 'Je n\'ai pas de réponse pour le moment.'
    except Exception as exc:
        reply_text = f"L'assistant IA est indisponible pour le moment ({type(exc).__name__})."

    db.session.add(Message(chat_id=chat.id, role='assistant', content=reply_text))
    db.session.commit()
    emit('assistant_done', {'content': reply_text}, room=chat.thread_id)


@socketio.on('join_chat')
def handle_join_chat(data):
    chat_id = (data or {}).get('chat_id', '').strip()
    active_chat = get_chat_by_thread_id(chat_id)

    if active_chat is None:
        emit('chat_error', {'message': 'Conversation introuvable.'})
        return

    join_room(active_chat.thread_id)
    emit('chat_joined', {'chat_id': active_chat.thread_id})


@socketio.on('send_message')
def handle_send_message(data):
    chat_id = (data or {}).get('chat_id', '').strip()
    content = (data or {}).get('message', '').strip()

    if not chat_id or not content:
        emit('chat_error', {'message': 'Message vide ou conversation manquante.'})
        return

    active_chat = get_chat_by_thread_id(chat_id)
    if active_chat is None:
        emit('chat_error', {'message': 'Conversation introuvable.'})
        return

    join_room(active_chat.thread_id)

    db.session.add(Message(chat_id=active_chat.id, role='user', content=content))
    db.session.commit()

    emit('user_message', {'content': content}, room=active_chat.thread_id)
    emit('assistant_start', room=active_chat.thread_id)
    stream_ai_reply(active_chat)

@app.route('/')
def hello():
    return redirect(url_for('chat_overview'))


@app.route('/chat')
def chat_overview():
    return render_template('chats/chat_overview.html', chat_list=get_all_chats())


@app.route('/chat/new')
def new_chat():
    chat = create_chat()
    return redirect(url_for('chat', chat_id=chat.thread_id))


@app.route('/chat/<chat_id>')
def chat(chat_id):
    active_chat = get_chat_by_thread_id(chat_id)

    if active_chat is None:
        abort(404)

    return render_template(
        'chats/chat.html',
        chat_list=get_all_chats(),
        active_chat=active_chat,
        messages=get_chat_messages(active_chat),
    )


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)