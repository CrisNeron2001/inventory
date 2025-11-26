from datetime import datetime
from dataclasses import dataclass
from typing import Optional
from core.models.entity.user_entity import User

@dataclass
class Cart:
    cart_id: Optional[int | None]
    user_inv_id: Optional[int | None]
    created_at: datetime
    updated_at: datetime
    user_inv: Optional[User]