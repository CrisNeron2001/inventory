from dataclasses import dataclass
from core.models.dto.cart_dto import CartDTO
from core.models.dto.product_dto import ProductDTO
from typing import Optional

@dataclass
class CartProductDTO:
	cart_product_id: Optional[int | None]
	cart_id: Optional[int | None]
	product_id: Optional[int | None]
	quantity: int
	cart: Optional[CartDTO | None]
	product: Optional[ProductDTO | None]