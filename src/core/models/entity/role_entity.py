from datetime import datetime
from dataclasses import dataclass
from typing import Optional

@dataclass
class Role:
    role_inv_id: Optional[int]
    name: str
    created_at: datetime
    updated_at: datetime