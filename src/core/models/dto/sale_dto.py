from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class SaleDTO:
    sale_id: Optional[int] = None
    cart_id: Optional[int] = None
    sale_date: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    product_name: Optional[str] = None
    quantity: Optional[int] = None
    unit_price: Optional[int] = None
    total_price: Optional[int] = None
