---
name: token-optimizer
description: Optimizes token usage and context efficiency for the agent. Use when performing complex tasks to minimize costs and prevent context bloat.
---

# Token Optimizer

Expert guidance for maximizing token efficiency. High-performance, low-cost operation.

## Mandates

- **Surgical Actions**: Never read whole files when lines suffice. Use `grep_search` to target before `read_file`.
- **Parallelism**: Group independent tool calls in a single turn. 
- **Zero Filler**: Eliminate all conversational fluff. Every word must carry technical signal.
- **Context Pruning**: Avoid re-reading recently accessed files. Rely on short-term memory.
- **Sub-Agent Delegation**: Delegate high-volume or repetitive tasks to sub-agents to keep the main history lean.

## Workflow

1.  **Analyze Request**: Identify minimal data needed.
2.  **Surgical Research**:
    - Use `glob` + `grep_search` (parallel) to find symbols.
    - `read_file` with `start_line` / `end_line` ONLY.
3.  **Compressed Execution**:
    - Batch edits to different files in one turn.
    - Use `replace` with minimal context while ensuring uniqueness.
4.  **Verification**:
    - Run targeted tests/commands. Capture ONLY relevant output (tail logs).

## Compression Level: Ultra
- Abbreviate prose.
- Use symbols (->, =, !, ?).
- Drop articles and conjunctions.
