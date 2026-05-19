---
name: emergency-briefer
description: Synthesizes complex technical data into concise, readable, and actionable emergency briefs.
---

# Emergency Briefer

This skill ensures that critical information is delivered effectively under high-stress conditions.

## Workflow

1.  **Synthesize**: Collect outputs from `fallout-predictor`, `risk-analyst`, and `survival-strategist`.
2.  **Prioritize (BLUF)**: Place the most life-saving information at the very top (Bottom Line Up Front).
3.  **Simplify**: Convert technical jargon (rem, Gy, mach stem) into plain, actionable language.
4.  **Mode Selection**:
    - **Flash Brief**: < 50 words for immediate action.
    - **Standard Brief**: Structured summary with prioritized checklists.
    - **Technical Addendum**: For deep-dive data (hidden by default).

## Style Principles

- **Urgency without Panic**: Maintain a calm, authoritative tone.
- **Visual Hierarchy**: Use bolding and bullet points to guide the eye to key actions.
- **Rule of Three**: Focus on the top three critical survival steps.

## Resources

- **Style Guide**: [references/style_guide.md](references/style_guide.md)
- **Templates**: [assets/templates.json](assets/templates.json)
