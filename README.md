# Nuclear Attack Emergency Agent — Gemini CLI Skills

An autonomous agent for the **Gemini CLI** that delivers survival intelligence during a nuclear attack emergency. The agent transforms raw geographic, meteorological, radiological, demographic, and geopolitical data into actionable instructions: where to shelter, when to evacuate, how to decontaminate, how to stay psychologically grounded, and what to expect next.

The agent contract — tone, safety priority, data requirements, operational workflow — is defined in [`GEMINI.md`](./GEMINI.md). This repository implements that contract as a set of **23 specialized skills** under `.gemini/skills/`.

> **Web chatbot (Flask + Ollama):** besides the Gemini CLI skills, this repo includes a local web chat that wraps the skills as tools and runs them through a local LLM. To install and run it (Linux/Windows, Ollama native or in Docker), see **[`WEBAPP.md`](./WEBAPP.md)**.

---

## How it works

Gemini CLI auto-loads every skill it finds under `.gemini/skills/<skill-name>/SKILL.md`. There is **no install step**: clone the repo, open the project with Gemini CLI, and the skills are available immediately. The CLI routes user prompts to skills by matching the prompt against each skill's `description:` frontmatter, so trigger wording in the description matters — every skill in this repo includes an explicit **"Use when..."** clause.

```bash
git clone <repo-url>
cd AI_agentSkills
gemini            # opens the CLI with all 23 skills auto-loaded
```

---

## Repository layout

```
AI_agentSkills/
├── GEMINI.md                       # Agent system prompt + operational contract
├── README.md                       # This file
├── plan.md                         # Audit & remediation plan
├── package.json                    # Node toolchain (used by api-auditor only)
└── .gemini/
    └── skills/
        ├── api-auditor/            # HTTP endpoint health check
        ├── comms-monitor/          # Polls official emergency feeds
        ├── data-visualizer/        # Heatmaps, blast radii, dashboards
        ├── demographic-analyst/    # 🚧 Population density & vulnerable groups
        ├── emergency-briefer/      # BLUF briefs (Flash/Standard/Technical)
        ├── fallout-predictor/      # Multi-altitude plume + contamination zones
        ├── geo-analyst/            # 🚧 Terrain barriers, bridges, accessibility
        ├── health-advisor/         # Decontamination + radiation symptom triage
        ├── health-monitor/         # 🚧 Water safety, disease surveillance
        ├── infra-monitor/          # 🚧 Water/power/gas/telecom status
        ├── location-provider/      # User geolocation via IP
        ├── logistics-navigator/    # 🚧 Cross-wind evacuation routing
        ├── pdf-generator/          # 🚧 Offline-ready PDF brief (mock impl.)
        ├── psych-counselor/        # Psychological First Aid (PFA)
        ├── rad-recon/              # Real-time radiation sensors (IRSN Teleray)
        ├── resource-inventory/     # Supply tracking + POI search
        ├── risk-analyst/           # Target-proximity risk scoring
        ├── secure-comms/           # 🚧 Mesh/AX.25 offline fallback
        ├── skill-optimizer/        # Meta: audits existing skills
        ├── skill-proposer/         # Meta: identifies missing domains
        ├── strike-predictor/       # Predicts next likely target
        ├── survival-strategist/    # Shelter-in-place vs evacuate
        └── token-optimizer/        # Meta: minimizes context / cost
```

🚧 = work-in-progress — SKILL.md is documented and will route, but the supporting script is still planned.

Each skill folder may contain:
- `SKILL.md` — required. Frontmatter (`name`, `description` with "Use when..." trigger) + workflow.
- `scripts/` — executable helpers (Python or Node) the skill calls.
- `references/` — long-form domain reference material.
- `assets/` — static data (JSON, CSV).

---

## Prerequisites

- **Gemini CLI** — installed and authenticated.
- **Python 3.9+** — used by most skills with executable scripts.
- **Node.js 18+** — used by `api-auditor/scripts/audit.js` and by the three optional helpers `fallout-predictor/scripts/{geocoding,get_map,get_weather}.js` (see [`fallout-predictor/scripts/README.md`](./.gemini/skills/fallout-predictor/scripts/README.md)). The canonical Python pipeline still drives the skill; the JS scripts are convenience CLIs.
- **Internet access** — the agent calls these public APIs (no keys required):
  - [Open-Meteo](https://open-meteo.com/) — multi-altitude wind data (`fallout-predictor`).
  - [Overpass / OpenStreetMap](https://overpass-api.de/) — military bases, power plants, shelters, pharmacies, transit nodes (`risk-analyst`, `survival-strategist`, `resource-inventory`, `geo-analyst`, `infra-monitor`).
  - [IP-API.com](http://ip-api.com/) (with `ipapi.co` fallback) — geolocation (`location-provider`).
  - [NWS Alerts](https://api.weather.gov/) — verified emergency feed (`comms-monitor`).
  - [IRSN Teleray](https://teleray.irsn.fr/) — radiation sensor network, FR. Mock data used when endpoint is unreachable (`rad-recon`).

Optional Python packages (only for WIP visual skills): `matplotlib`, `plotly`, `folium`.

---

## Skill catalog

🚧 = work-in-progress (description routes correctly, but script is still planned).

### Sensing & Reconnaissance — situational awareness
| Skill | Purpose | Trigger words |
|---|---|---|
| [`location-provider`](./.gemini/skills/location-provider/SKILL.md) | Resolve user coordinates via IP | "where am I", "my location" |
| [`comms-monitor`](./.gemini/skills/comms-monitor/SKILL.md) | Poll government & emergency broadcast feeds | "alerts", "broadcasts", "official news" |
| [`fallout-predictor`](./.gemini/skills/fallout-predictor/SKILL.md) | Multi-altitude plume + contamination zones from wind | "fallout", "where will radiation settle" |
| [`rad-recon`](./.gemini/skills/rad-recon/SKILL.md) | Real-time radiation sensor readings vs models | "radiation reading", "hot zone", "Teleray" |
| [`risk-analyst`](./.gemini/skills/risk-analyst/SKILL.md) | Score location vs strategic targets | "is it safe", "high-risk zone" |
| [`strike-predictor`](./.gemini/skills/strike-predictor/SKILL.md) | Predict next target from doctrine + proximity | "next strike", "what's next" |
| [`demographic-analyst`](./.gemini/skills/demographic-analyst/SKILL.md) 🚧 | Population density & vulnerable groups | "population", "hospitals", "elderly" |
| [`geo-analyst`](./.gemini/skills/geo-analyst/SKILL.md) 🚧 | Terrain, bridges/tunnels, accessibility | "routes", "bridges", "wheelchair" |
| [`infra-monitor`](./.gemini/skills/infra-monitor/SKILL.md) 🚧 | Water / power / gas / telecom status | "utilities", "power outage", "water pump" |

### Action & Response — life-saving decisions
| Skill | Purpose | Trigger words |
|---|---|---|
| [`survival-strategist`](./.gemini/skills/survival-strategist/SKILL.md) | Shelter-in-place vs evacuate; shelter lookup | "where do I go", "evacuate" |
| [`health-advisor`](./.gemini/skills/health-advisor/SKILL.md) | Decontamination + radiation sickness triage | "exposed", "symptoms", "decontaminate" |
| [`resource-inventory`](./.gemini/skills/resource-inventory/SKILL.md) | Supplies tracking + POI search | "supplies", "pharmacy", "water points" |
| [`psych-counselor`](./.gemini/skills/psych-counselor/SKILL.md) | Psychological First Aid (4-7-8, 5-4-3-2-1) | "panic", "calm", "breathe" |
| [`logistics-navigator`](./.gemini/skills/logistics-navigator/SKILL.md) 🚧 | Cross-wind evacuation routing | "evacuation route", "safe-exit" |
| [`health-monitor`](./.gemini/skills/health-monitor/SKILL.md) 🚧 | Water safety, epidemics, sanitation | "epidemic", "contaminated water" |

### Communication & Delivery
| Skill | Purpose | Trigger words |
|---|---|---|
| [`emergency-briefer`](./.gemini/skills/emergency-briefer/SKILL.md) | BLUF briefs (Flash / Standard / Technical) | "brief", "summary", "tl;dr" |
| [`pdf-generator`](./.gemini/skills/pdf-generator/SKILL.md) 🚧 | Aggregates briefs + maps into offline PDF | "PDF", "printable", "download", "offline brief" |
| [`data-visualizer`](./.gemini/skills/data-visualizer/SKILL.md) | Heatmaps, blast radii overlays, dashboards | "plot", "map", "visualize" |
| [`secure-comms`](./.gemini/skills/secure-comms/SKILL.md) 🚧 | Mesh / AX.25 / compression offline fallback | "no internet", "ham radio", "mesh" |

### Meta — tooling
| Skill | Purpose | Trigger words |
|---|---|---|
| [`api-auditor`](./.gemini/skills/api-auditor/SKILL.md) | HTTP endpoint health check | "check", "test", "audit URL" |
| [`skill-optimizer`](./.gemini/skills/skill-optimizer/SKILL.md) | Audit existing skills, propose improvements | "improve skill", "optimize skill" |
| [`skill-proposer`](./.gemini/skills/skill-proposer/SKILL.md) | Identify missing domains, propose new skills | "what's missing", "new skill idea" |
| [`token-optimizer`](./.gemini/skills/token-optimizer/SKILL.md) | Minimize context / cost in agent operations | "tokens", "cost", "efficiency" |

---

## Use cases — example prompts

End-to-end scenarios designed to exercise the catalog. The "Skills activated" column shows the expected routing order under the agent's operational workflow. Prompts marked 🚧 depend on a WIP skill — they will route correctly but the supporting script is still planned.

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
| 14 | "I'm panicking, the sirens just went off — help me calm down." | `psych-counselor` |
| 15 | "What's the actual radiation reading near me right now?" | `location-provider` → `rad-recon` → `emergency-briefer` |
| 16 | "Map nearby vulnerable people — hospitals, schools, nursing homes." 🚧 | `location-provider` → `demographic-analyst` |
| 17 | "Which bridges and tunnels can I still use to leave the city?" 🚧 | `location-provider` → `geo-analyst` |
| 18 | "Is the water from my tap safe to drink right now?" 🚧 | `health-monitor` → `health-advisor` |
| 19 | "Plot a fallout heatmap over my region." | `location-provider` → `fallout-predictor` → `data-visualizer` |
| 20 | "Cell network is down — how do I send a message?" 🚧 | `secure-comms` |
| 21 | "Give me a turn-by-turn route out of the danger zone." 🚧 | `location-provider` → `fallout-predictor` → `logistics-navigator` |
| 22 | "Generate me a printable PDF brief I can take offline." 🚧 | `location-provider` → `fallout-predictor` → `risk-analyst` → `pdf-generator` |
| 23 | "Geocode the city 'Vesoul' and show me the wind there." | `fallout-predictor` (via `geocoding.js` + `get_weather.js`) |

---

## Testing each skill manually

Pick a prompt from the table above (or one of the per-skill smoke prompts below), send it to the agent in Gemini CLI, and verify three things:

1. **The skill activates** — Gemini CLI announces the skill name or visibly uses its script.
2. **The script runs without error** — for skills with a `scripts/` folder, the API call succeeds (Open-Meteo, Overpass, IP-API, NWS, IRSN are all free / mock-backed).
3. **The output respects `GEMINI.md`** — calm, factual, authoritative tone; safety prioritized; technical jargon converted to plain language when the user is a non-expert.

Per-skill smoke prompts (functional skills):

- **location-provider** — "What's my approximate location right now?"
- **comms-monitor** — "Check for new emergency broadcasts."
- **fallout-predictor** — "Simulate a 150 kt detonation over Lyon with current weather."
- **rad-recon** — "What does the nearest radiation sensor say?"
- **risk-analyst** — "How close am I to a military base or nuclear plant?"
- **strike-predictor** — "If the first strike hit Luxeuil, what's the next likely target within 200 km?"
- **survival-strategist** — "Should I shelter in place or evacuate? Fallout is 20 minutes out."
- **health-advisor** — "I came in from the rain after a detonation, what now?"
- **resource-inventory** — "Find pharmacies and drinking-water points near me."
- **psych-counselor** — "Walk me through a 4-7-8 breathing exercise."
- **emergency-briefer** — "Give me a Flash Brief on my situation."
- **api-auditor** — "Audit `https://api.open-meteo.com/v1/forecast`."
- **skill-optimizer** — "Audit the `risk-analyst` skill."
- **skill-proposer** — "Propose a skill for restoring communications after an EMP."
- **token-optimizer** — "Apply token-efficient mode for the next investigation."
- **data-visualizer** — "Plot the blast radius for a 150 kt detonation over Lyon."
- **pdf-generator** — "Generate a PDF emergency brief from the current situation."

WIP skills (route correctly, scripts pending): `demographic-analyst`, `geo-analyst`, `health-monitor`, `infra-monitor`, `logistics-navigator`, `secure-comms`. The `pdf-generator` script runs but only emits a `.meta.json` mock — real PDF rendering (fpdf2 / ReportLab) is still TODO.

---

## Project conventions

All skills must respect the rules from [`GEMINI.md`](./GEMINI.md):

- **Tone** — calm, factual, authoritative. No panic, no hedging.
- **Safety first** — human life preservation overrides all other considerations.
- **Analytical rigor** — recommendations correlate location + atmosphere + sensors + known target sites; never speculate without data.
- **Information integrity** — prioritize official government data and verified sensor networks; filter misinformation.

When writing or modifying a skill, the `description:` frontmatter must include an explicit **"Use when..."** clause. This is what Gemini CLI's router matches on; without it, auto-routing is weaker.

---
