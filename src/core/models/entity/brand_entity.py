from datetime import datetime
from dataclasses import dataclass
from typing import Optional

@dataclass
class Brand:
    brand_id: Optional[int | None]
    name: str
    created_at: datetime
    updated_at: datetime