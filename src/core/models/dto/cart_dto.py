from dataclasses import dataclass
from typing import Optional
from core.models.dto.user_dto import UserDTO

@dataclass
class CartDTO:
    cart_id: Optional[int | None]
    user_inv_id: Optional[int | None]
    user_inv: Optional[UserDTO]