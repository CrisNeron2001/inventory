from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from core.models.entity.role_entity import Role

@dataclass
class User:
    user_inv_id: Optional[int]
    role_inv_id: int
    first_name: str
    last_name: Optional[str]
    username: str
    password: str
    created_at: datetime
    updated_at: datetime
    role_inv: Optional[Role]