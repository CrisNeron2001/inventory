from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from core.models.entity.cart_entity import Cart

@dataclass
class Sale:
    sale_id: Optional[int]
    cart_id: Optional[int]
    unit_price: int
    total_price: int
    sale_date: Optional[datetime]
    notes: Optional[str]
    amount_price: int
    created_at: datetime
    updated_at: datetime
    cart: Optional[Cart]
