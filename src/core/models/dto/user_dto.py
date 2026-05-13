from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class UserDTO:
    user_inv_id: Optional[int]
    first_name: str
    middle_name: Optional[str]
    last_name: str
    rut: str
    password: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
