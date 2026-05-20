---
name: comms-monitor
description: Monitors emergency frequencies, government alerts, and verified news feeds. Use when the user asks for the latest alerts, official broadcasts, news updates, or wants to verify a rumor against authoritative sources.
---

# Comms Monitor

Ensures continuous situational awareness when standard internet or cellular services fail.

## Workflow

1.  **Poll Feeds**: Check RSS feeds, emergency broadcast summaries, and local official social media (simulated via `scripts/poll_broadcasts.py`).
2.  **Filter Noise**: Prioritize alerts from government sources (e.g., Prefectures, Ministère de l'Intérieur).
3.  **Alert**: Push critical updates to the `emergency-briefer`.

## Resources
- **Verified Sources**: [assets/sources.json](assets/sources.json)
