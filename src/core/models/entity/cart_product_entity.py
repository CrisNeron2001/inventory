from dataclasses import dataclass
from core.models.entity.cart_entity import Cart
from core.models.entity.product_entity import Product
from typing import Optional

@dataclass
class CartProduct:
	cart_id: Optional[int | None]
	product_id: Optional[int | None]
	quantity: int
	cart: Optional[Cart | None]
	product: Optional[Product | None]