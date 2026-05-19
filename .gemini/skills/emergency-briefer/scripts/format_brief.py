import sys
import json

def format_brief(data, mode="standard"):
    """
    Formats raw emergency data into a readable brief.
    """
    if mode == "flash":
        return f"### **IMMEDIATE ACTION REQUIRED**\n- **{data.get('primary_action', 'SHELTER IN PLACE')}**\n- Threat: {data.get('threat', 'Nuclear Detonation')}\n- Location: {data.get('location', 'Unknown')}"
    
    brief = []
    brief.append(f"### **BOTTOM LINE UP FRONT: {data.get('status', 'CRITICAL ALERT')}**")
    brief.append(f"**{data.get('summary_action', 'Seek substantial shelter immediately.')}**\n")
    
    if data.get('top_3_actions'):
        brief.append("### **TOP 3 SURVIVAL STEPS**")
        for i, action in enumerate(data['top_3_actions'][:3], 1):
            brief.append(f"{i}. **{action}**")
        brief.append("")

    if data.get('threat_details'):
        brief.append("### **SITUATIONAL AWARENESS**")
        for detail in data['threat_details']:
            brief.append(f"- {detail}")
        brief.append("")

    brief.append("---")
    brief.append("*Monitor emergency broadcasts for further updates.*")
    
    return "\n".join(brief)

if __name__ == "__main__":
    # Example usage
    sample_data = {
        "status": "DETONATION CONFIRMED",
        "primary_action": "DROP AND COVER",
        "summary_action": "Move to the core of a stone or concrete building now.",
        "location": "Vesoul",
        "threat": "10kt Airburst",
        "top_3_actions": [
            "Stay away from windows and exterior walls.",
            "Move to the lowest level of the building.",
            "Cover your nose and mouth with a clean cloth."
        ],
        "threat_details": [
            "Thermal flash has passed; blast wave arriving shortly.",
            "Radioactive dust (fallout) expected in 20 minutes.",
            "Winds moving North-East toward Lure."
        ]
    }
    print(format_brief(sample_data))
