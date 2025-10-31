from dataclasses import dataclass
from typing import Optional
from core.models.dto.category_dto import CategoryDTO
from core.models.dto.brand_dto import BrandDTO

@dataclass
class ProductDTO:
    product_id: Optional[int]
    name: str
    description: str
    quantity: int
    price: int
    sku: Optional[str]
    is_available: bool
    category: Optional[CategoryDTO]
    brand: Optional[BrandDTO]