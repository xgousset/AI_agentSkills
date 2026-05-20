---
name: secure-comms
description: Manages low-bandwidth and offline communication strategies (mesh networks, AX.25 packet radio, aggressive message compression) for when the grid fails or cellular/internet are down. Use when the user reports network failure, asks about offline communication, ham radio, mesh, or how to send critical messages without internet.
---

# Secure Comms Manager

Manages low-bandwidth and offline communication strategies when the grid fails.

## Workflow
1. **Network Audit**: Detects if standard HTTPS/JSON APIs are available; falls back to low-packet modes if connectivity is poor.
2. **Mesh Protocol**: Simulates communication over localized mesh networks or packet radio (AX.25).
3. **Message Compression**: Uses aggressive compression for critical survival packets.

## Resources
- `scripts/network_check.py`: Tests latency and packet loss to determine comms mode.
- `assets/offline_buffer.json`: Local cache of the most critical survival data.
