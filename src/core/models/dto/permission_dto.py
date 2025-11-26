from dataclasses import dataclass
from typing import Optional

@dataclass
class PermissionDTO:
    permission_key: str
    description: Optional[str] = None
