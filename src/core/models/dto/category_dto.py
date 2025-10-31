from dataclasses import dataclass
from typing import Optional

@dataclass
class CategoryDTO:
    category_id: Optional[int | None]
    name: str