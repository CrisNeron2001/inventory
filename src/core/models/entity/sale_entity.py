from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Sale:
    sale_id: Optional[int]
    cart_id: int
    sale_date: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    product_name: Optional[str] = None
    quantity: Optional[int] = None
    unit_price: Optional[int] = None
    total_price: Optional[int] = None
