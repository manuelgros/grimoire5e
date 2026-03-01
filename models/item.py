from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from .base import BaseModel


@dataclass
class Item(BaseModel):
    type: str
    rarity: str
    entries: List[Any]

    tier: Optional[str] = None
    reqAttune: Optional[Union[bool, str]] = None
    weight: Optional[float] = None
    value: Optional[int] = None
    weapon: Optional[bool] = False
    armor: Optional[bool] = False
    wondrous: Optional[bool] = False

    @property
    def rarity_display(self) -> str:
        rarity_map = {
            "none": "Common Item",
            "common": "Common",
            "uncommon": "Uncommon",
            "rare": "Rare",
            "very rare": "Very Rare",
            "legendary": "Legendary",
            "artifact": "Artifact",
            "varies": "Varies",
        }
        return rarity_map.get(self.rarity, self.rarity.title())

    @property
    def requires_attunement(self) -> bool:
        return self.reqAttune is not None

