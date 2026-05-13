# AI_agentSkills

A collection of custom Agent Skills for Gemini CLI.

## Installation

To install a skill from this repository:

1. Clone the repository:
   ```bash
   git clone <repo-url>
   ```
2. Build/Package the skill you want (if not already packaged).
3. Install it using Gemini CLI:
   ```bash
   gemini skills install ./path/to/skill.skill --scope workspace
   ```

## Repository Structure

- `skills/`: Contains the source code for each skill.
  - `skill-name/`:
    - `SKILL.md`: Instructions and metadata.
    - `scripts/`: Custom scripts.
    - `references/`: Reference documentation.
    - `assets/`: Templates and static assets.
