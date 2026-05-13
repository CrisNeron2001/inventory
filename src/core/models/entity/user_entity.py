from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    user_inv_id: Optional[int]
    first_name: str
    middle_name: Optional[str]
    last_name: str
    rut: str
    password: str
    created_at: datetime
    updated_at: datetime
