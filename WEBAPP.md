# Web Chatbot — Flask + Ollama

A local web chat that wraps the project's emergency skills as LangChain tools and runs them
through a **local LLM via [Ollama](https://ollama.com/)**. It streams answers token-by-token over
WebSockets, grounds medical/panic answers in vetted protocols, and runs a lightweight verification
pass on every reply.

This is **separate** from the Gemini CLI skills documented in [`README.md`](./README.md). The web
app lives in `app.py`, `emergency_chatbot.py`, `extra_tools.py` and `templates/`.

---

## Requirements

- **Python 3.10+**
- **[Ollama](https://ollama.com/)** — running natively *or* in Docker (both covered below).
- At least one model pulled. Default is `qwen2.5:3b` (~2 GB, fits a 4 GB GPU). The model dropdown
  also offers `qwen2.5:7b-instruct`, `qwen3:4b` and `mistral:latest` — pull whichever you select.

---

## 1. Install the app (any OS)

> ⚠️ The committed `NuclearAgent/` folder is a **Windows** virtualenv — do **not** reuse it on
> Linux/macOS. Always recreate the venv from `requirements.txt`.

```bash
git clone <repo-url>
cd AI_agentSkills

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Configuration (`.env`, optional)

| Variable | Default | Purpose |
|---|---|---|
| `OLLAMA_MODEL` | `qwen2.5:3b` | Default model for the "Qwen 2.5 3B" dropdown slot. |
| `OLLAMA_HOST` | *(unset → `http://127.0.0.1:11434`)* | Where Ollama listens. Only set it for a **remote/other-host** daemon. |
| `VERIFIER_MODEL` | `qwen2.5:3b` | Small model used for the verification pass (kept cheap on purpose). |
| `CHAT_DB` | `instance/checkpoint.db` | SQLite file holding chats + conversation memory. |
| `FLASK_HOST` | `127.0.0.1` | Set to `0.0.0.0` to expose the app on the LAN. |

All paths are cross-platform; nothing here is Windows-specific.

---

## 2. Run Ollama

### Option A — Ollama installed natively

```bash
ollama serve            # if not already running as a service
ollama pull qwen2.5:3b  # or any model you'll select in the dropdown
```

### Option B — Ollama in Docker  ✅ (this is the Arch-Linux-with-Docker case)

The Flask app runs on the **host** and reaches the container at `localhost:11434`, so as long as
the port is mapped, **no app configuration is needed**.

```bash
# NVIDIA GPU
docker run -d --gpus=all -v ollama:/root/.ollama \
  -p 11434:11434 --name ollama ollama/ollama

# Pull a model INTO the container
docker exec -it ollama ollama pull qwen2.5:3b
```

- **CPU-only:** drop `--gpus=all`.
- **AMD GPU:** use the image `ollama/ollama:rocm` instead of `ollama/ollama`.
- **NVIDIA GPU on Arch Linux:** install the toolkit so Docker can see the GPU:
  ```bash
  sudo pacman -S nvidia-container-toolkit
  sudo nvidia-ctk runtime configure --runtime=docker
  sudo systemctl restart docker
  ```
  (You also need the NVIDIA driver installed on the host.)

Or use the bundled compose file (equivalent to the `docker run` above):

```bash
docker compose up -d
docker compose exec ollama ollama pull qwen2.5:3b
```

See [`docker-compose.yml`](./docker-compose.yml) — it's CPU-only by default; uncomment its
`deploy:` block for an NVIDIA GPU.

---

## 3. Start the app

```bash
python app.py
# -> http://127.0.0.1:5001
```

Open the URL, create a conversation, and chat. Useful bits:

- **Model dropdown** — pick the model per message (pull it first, or you'll get
  *"L'assistant IA est indisponible"*).
- **`/coords <lat> <lon>`** — pin your location manually (e.g. `/coords 47.24 6.02`) instead of
  IP geolocation. `/help` lists commands.

---

## Special cases

**Ollama on another machine or a non-default port**
No code change — just point the app at it:
```bash
export OLLAMA_HOST=http://192.168.1.50:11434   # Windows: $env:OLLAMA_HOST="http://..."
python app.py
```

**Running the Flask app *itself* in Docker too**
Then `localhost` inside the app container no longer means the Ollama container. Put both on a
shared Docker network and set `OLLAMA_HOST` to the service name:
```bash
OLLAMA_HOST=http://ollama:11434
```

---

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| *"L'assistant IA est indisponible"* | Model not pulled, or Ollama not reachable. Check `ollama list` / `docker exec ollama ollama list`, and that `OLLAMA_HOST` (if set) is correct. |
| `Connection refused` to `11434` | Ollama not running, or (Docker) the port isn't mapped (`-p 11434:11434`). |
| App starts but answers are very slow | Model too big for your VRAM → partial CPU offload. Use `qwen2.5:3b` / `qwen3:4b`, or a smaller quant. |
| `database disk image is malformed` | `instance/checkpoint.db` got corrupted (e.g. committed + merged as a binary blob). The chats/messages can be salvaged into a fresh DB; the `checkpoints`/`writes` tables are regenerated on next run. |
