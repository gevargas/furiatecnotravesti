from __future__ import annotations

from pathlib import Path
from typing import Any
import yaml

def load_knowledge(path: str | Path = "data/knowledge_base.yml") -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def context_for_intent(kb: dict, intent: str, max_items: int = 16) -> str:
    items = []
    for x in kb.get("care_principles", []):
        items.append(f"- {x}")
    for x in kb.get("ecuador_context", []):
        items.append(f"- {x}")
    for x in kb.get("intent_guidance", {}).get(intent, []):
        items.append(f"- {x}")
    return "\n".join(items[:max_items])
