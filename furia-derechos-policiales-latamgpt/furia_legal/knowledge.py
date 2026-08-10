import yaml

def load_knowledge(path="data/legal_knowledge.yml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def context_for(kb, intent):
    parts = []
    for x in kb.get("core_rights", []):
        parts.append(f"- {x}")
    for x in kb.get("safe_actions", []):
        parts.append(f"- {x}")
    for x in kb.get("intent_guidance", {}).get(intent, []):
        parts.append(f"- {x}")
    return "\n".join(parts[:18])
