from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Tag:
    id: Optional[int]
    name: str
    description: Optional[str] = None


@dataclass
class Meme:
    id: Optional[int]
    title: str
    description: str
    image_path: str
    date_added: Optional[str] = None
    tags: List[Tag] = field(default_factory=list)

    def __post_init__(self):
        if self.date_added is None:
            self.date_added = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
