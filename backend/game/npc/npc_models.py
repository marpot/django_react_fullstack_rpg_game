from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class NPC:
    id: str
    name: str
    dialog: List[str] = field(default_factory=list)
    state: str = "idle"
    quest_state: Optional[str] = None
    personality: str = "neutral"