from dataclasses import dataclass
from typing import Optional

@dataclass
class RoleDTO:
    role_inv_id: Optional[int | None]
    name: str