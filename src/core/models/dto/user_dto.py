from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from core.models.dto.role_dto import RoleDTO


@dataclass
class UserDTO:
    user_inv_id: Optional[int]
    role_inv_id: Optional[int]
    first_name: str
    last_name: Optional[str]
    username: str
    password: str
    role_inv: Optional[RoleDTO]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None