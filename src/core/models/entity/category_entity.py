from datetime import datetime
from dataclasses import dataclass
from typing import Optional

@dataclass
class Category:
    category_id: Optional[int]
    name: str
    created_at: datetime
    updated_at: datetime