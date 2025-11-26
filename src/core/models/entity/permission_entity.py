from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Permission:
    permission_key: str
    description: Optional[str]
    created_at: Optional[datetime]
