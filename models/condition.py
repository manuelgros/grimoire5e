from dataclasses import dataclass
from typing import Any, List

from .base import BaseModel


@dataclass
class Condition(BaseModel):
    entries: List[Any]

