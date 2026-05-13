from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from core.models.entity.category_entity import Category
from core.models.entity.brand_entity import Brand


@dataclass
class Product:
    product_id: Optional[int]
    name: str
    description: str
    stock: int
    price: int
    sku: Optional[str]
    category: Optional[Category]
    brand: Optional[Brand]
    created_at: datetime
    updated_at: datetime

