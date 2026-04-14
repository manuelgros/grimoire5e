from dataclasses import dataclass
from typing import Any, List, Optional

from .base import BaseModel


@dataclass
class ClassFeature(BaseModel):
    entries: List[Any]
    class_name: str
    class_source: str
    level: int
    is_subclass: bool = False
    subclass_short_name: Optional[str] = None
    subclass_source: Optional[str] = None
    subclass_name: Optional[str] = None
    is_variant: bool = False
    header: Optional[int] = None

    @property
    def subclass_display(self) -> Optional[str]:
        return self.subclass_name or self.subclass_short_name
