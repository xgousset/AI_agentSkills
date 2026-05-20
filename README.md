# Nuclear Attack Emergency Agent — Gemini CLI Skills

An autonomous agent for the **Gemini CLI** that delivers survival intelligence during a nuclear attack emergency. The agent transforms raw geographic, meteorological, and geopolitical data into actionable instructions: where to shelter, when to evacuate, how to decontaminate, what to expect next.

The agent contract — tone, safety priority, data requirements, operational workflow — is defined in [`GEMINI.md`](./GEMINI.md). This repository implements that contract as a set of **12 specialized skills** under `.gemini/skills/`.

---

## How it works

Gemini CLI auto-loads every skill it finds under `.gemini/skills/<skill-name>/SKILL.md`. There is **no install step**: clone the repo, open the project with Gemini CLI, and the skills are available immediately. The CLI routes user prompts to skills by matching the prompt against each skill's `description:` frontmatter, so trigger wording in the description matters.

```bash
git clone <repo-url>
cd AI_agentSkills
gemini            # opens the CLI with all 12 skills auto-loaded
```

---

## Repository layout

```
AI_agentSkills/
├── GEMINI.md                    # Agent system prompt + operational contract
├── README.md                    # This file
├── package.json                 # Node toolchain (used by api-auditor only)
└── .gemini/
    └── skills/
        ├── api-auditor/         # (generic HTTP QA — pending repurpose)
        ├── comms-monitor/       # Polls official emergency feeds
        ├── emergency-briefer/   # Synthesizes outputs into BLUF briefs
        ├── fallout-predictor/   # Plume + contamination zones from wind data
        ├── health-advisor/      # Decontamination + radiation symptom triage
        ├── location-provider/   # User geolocation via IP
        ├── resource-inventory/  # Supply tracking + POI search
        ├── risk-analyst/        # Target-proximity risk scoring
        ├── skill-optimizer/     # Meta: audits existing skills
        ├── skill-proposer/      # Meta: suggests new skills
        ├── strike-predictor/    # Predicts next likely target
        └── survival-strategist/ # Shelter-in-place vs evacuate decisions
```

Each skill folder may contain:
- `SKILL.md` — required. Frontmatter (`name`, `description`) + workflow.
- `scripts/` — executable helpers (Python or Node) the skill calls.
- `references/` — long-form domain reference material.
- `assets/` — static data (JSON, CSV).

---

## Prerequisites

- **Gemini CLI** — installed and authenticated.
- **Python 3.9+** — used by 11 of 12 skills (scripts under `scripts/`).
- **Node.js 18+** — used only by `api-auditor/scripts/audit.js`.
- **Internet access** — the agent calls these public APIs (no keys required):
  - [Open-Meteo](https://open-meteo.com/) — real-time wind data at multiple altitudes (`fallout-predictor`).
  - [Overpass / OpenStreetMap](https://overpass-api.de/) — military bases, power plants, shelters, pharmacies (`risk-analyst`, `survival-strategist`, `resource-inventory`).
  - [IP-API.com](http://ip-api.com/) — IP-based geolocation (`location-provider`).

---

## Skill catalog

### Sensing — situational awareness
| Skill | Purpose | Trigger words |
|---|---|---|
| [`location-provider`](./.gemini/skills/location-provider/SKILL.md) | Resolve user coordinates via IP | "where am I", "my location" |
| [`comms-monitor`](./.gemini/skills/comms-monitor/SKILL.md) | Poll government / emergency broadcast feeds | "alerts", "broadcasts", "official news" |
| [`fallout-predictor`](./.gemini/skills/fallout-predictor/SKILL.md) | Plume trajectory + contamination zones from wind | "fallout", "where will radiation settle" |
| [`risk-analyst`](./.gemini/skills/risk-analyst/SKILL.md) | Score location vs strategic targets (bases, plants) | "is it safe", "high-risk zone" |
| [`strike-predictor`](./.gemini/skills/strike-predictor/SKILL.md) | Predict next target from doctrine + proximity | "next strike", "what's next" |

### Action — life-saving decisions
| Skill | Purpose | Trigger words |
|---|---|---|
| [`survival-strategist`](./.gemini/skills/survival-strategist/SKILL.md) | Shelter-in-place vs evacuate; shelter lookup | "where do I go", "what do I do", "evacuate" |
| [`health-advisor`](./.gemini/skills/health-advisor/SKILL.md) | Decontamination + radiation sickness triage | "exposed", "symptoms", "decontaminate" |
| [`resource-inventory`](./.gemini/skills/resource-inventory/SKILL.md) | Supplies tracking + POI search (pharmacy, water) | "supplies", "where to get", "inventory" |

### Synthesis — delivery
| Skill | Purpose | Trigger words |
|---|---|---|
| [`emergency-briefer`](./.gemini/skills/emergency-briefer/SKILL.md) | BLUF brief (Flash / Standard / Technical) | "brief me", "summary", "tl;dr" |

### Meta — tooling
| Skill | Purpose | Trigger words |
|---|---|---|
| [`api-auditor`](./.gemini/skills/api-auditor/SKILL.md) | HTTP endpoint health check (status, latency) | "check", "test", "audit URL" |
| [`skill-optimizer`](./.gemini/skills/skill-optimizer/SKILL.md) | Audit existing skills, propose improvements | "improve skill", "optimize skill" |
| [`skill-proposer`](./.gemini/skills/skill-proposer/SKILL.md) | Identify missing domains, propose new skills | "what's missing", "new skill idea" |
| [`token-optimizer`](./.gemini/skills/token-optimizer/SKILL.md) | Maximize context efficiency + minimize costs | "tokens", "cost", "efficiency" |

---

## Use cases — example prompts

The following prompts have been designed to exercise realistic emergency scenarios end-to-end. The "Skills activated" column shows the expected routing order under the agent's operational workflow.

| # | User prompt | Skills activated (in order) |
|---|---|---|
| 1 | "There's been a detonation 30 km north of me, where do I go?" | `location-provider` → `fallout-predictor` → `survival-strategist` → `emergency-briefer` |
| 2 | "Am I living in a high-risk zone?" | `location-provider` → `risk-analyst` → `emergency-briefer` |
| 3 | "I was outside when the fallout hit — what do I do now?" | `health-advisor` → `emergency-briefer` |
| 4 | "Predict where the next strike will land near me." | `location-provider` → `strike-predictor` → `emergency-briefer` |
| 5 | "What supplies do I have left and where can I get more?" | `resource-inventory` → `location-provider` |
| 6 | "Get me the latest official emergency broadcasts." | `comms-monitor` → `emergency-briefer` |
| 7 | "150 kt detonation in Strasbourg, wind from the west — who's in the plume?" | `fallout-predictor` → `survival-strategist` |
| 8 | "Give me a 30-second flash brief on my current situation." | `location-provider` → `risk-analyst` → `fallout-predictor` → `emergency-briefer` (Flash mode) |
| 9 | "How do I take potassium iodide safely?" | `health-advisor` |
| 10 | "Find the closest nuclear shelter and a cross-wind evacuation route." | `location-provider` → `fallout-predictor` → `survival-strategist` |
| 11 | "Are the Open-Meteo and Overpass endpoints still responding?" | `api-auditor` |
| 12 | "Audit the fallout-predictor skill — anything we can improve?" | `skill-optimizer` |
| 13 | "What critical survival domain are we still missing?" | `skill-proposer` |

---

## Testing each skill manually

Pick a prompt from the table above (or one of the per-skill prompts below), send it to the agent in Gemini CLI, and verify three things:

1. **The skill activates** — Gemini CLI announces the skill name or visibly uses its script.
2. **The script runs without error** — for skills that call into `scripts/`, the API call succeeds (Open-Meteo, Overpass, IP-API are all free and reachable without keys).
3. **The output respects `GEMINI.md`** — calm, factual, authoritative tone; safety prioritized; technical jargon converted to plain language when the user is a non-expert.

Per-skill smoke prompts:

- **location-provider** — "What's my approximate location right now?"
- **comms-monitor** — "Check for new emergency broadcasts."
- **fallout-predictor** — "Simulate a 150 kt detonation over Lyon with current weather."
- **risk-analyst** — "How close am I to a military base or nuclear plant?"
- **strike-predictor** — "If the first strike hit Luxeuil, what's the next likely target within 200 km?"
- **survival-strategist** — "Should I shelter in place or evacuate? Fallout is 20 minutes out."
- **health-advisor** — "I came in from the rain after a detonation, what now?"
- **resource-inventory** — "Find pharmacies and drinking-water points near me."
- **emergency-briefer** — "Give me a Flash Brief on my situation."
- **api-auditor** — "Audit `https://api.open-meteo.com/v1/forecast`."
- **skill-optimizer** — "Audit the `risk-analyst` skill."
- **skill-proposer** — "Propose a skill for restoring communications after an EMP."

---
