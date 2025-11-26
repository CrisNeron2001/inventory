from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from core.models.dto.cart_dto import CartDTO

@dataclass
class SaleDTO:
    sale_id: Optional[int]
    cart_id: Optional[int] = None
    unit_price: int = 0
    total_price: int = 0
    sale_date: Optional[datetime] = None
    notes: Optional[str] = None
    amount_price: int = 0
    cart: Optional[CartDTO] = None
