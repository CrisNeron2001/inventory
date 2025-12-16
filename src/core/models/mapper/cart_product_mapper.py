from core.models.entity.cart_product_entity import CartProduct
from core.models.dto.cart_product_dto import CartProductDTO
from core.models.dto.cart_dto import CartDTO
from core.models.dto.product_dto import ProductDTO
from core.models.mapper.cart_mapper import cart_dto_to_entity, cart_entity_to_dto
from core.models.mapper.product_mapper import product_dto_to_entity, product_entity_to_dto
from typing import Any, List


def dto_to_entity(dto: CartProductDTO) -> CartProduct:
	return CartProduct(
		cart_product_id=dto.cart_product_id,
		cart_id=dto.cart_id,
		product_id=dto.product_id,
		quantity=dto.quantity,
		cart=cart_dto_to_entity(dto.cart) if dto.cart else None,
		product=product_dto_to_entity(dto.product) if dto.product else None
	)

def entity_to_dto(entity: CartProduct) -> CartProductDTO:
	if isinstance(entity, CartProduct):
		cart_field = getattr(entity, 'cart', None)
		if isinstance(cart_field, int):
			cart_dto = CartDTO(cart_id=entity.cart_id, user_inv_id=None, user_inv=None)
		else:
			cart_dto = cart_entity_to_dto(cart_field) if cart_field else None

		product_field = getattr(entity, 'product', None)
		if isinstance(product_field, str):
			p_dto = ProductDTO(
				product_id=None,
				name=product_field,
				description="",
				stock=0,
				price=0,
				sku=None,
				is_available=False,
				category=None,
				brand=None
			)
		else:
			p_dto = product_entity_to_dto(product_field) if product_field else None

		return CartProductDTO(
			cart_product_id=entity.cart_product_id,
			cart_id=entity.cart_id,
			product_id=entity.product_id,
			quantity=entity.quantity,
			cart=cart_dto,
			product=p_dto
		)

def row_to_entity(row: List[Any]) -> CartProduct:
	cart_product_id = row[0] if len(row) > 0 else None
	cart_id = row[1] if len(row) > 1 else None
	user_inv_id = row[2] if len(row) > 2 else None
	product_id = row[3] if len(row) > 3 else None
	product_name = row[4] if len(row) > 4 else ""
	product_price = row[5] if len(row) > 5 else 0
	quantity = row[6] if len(row) > 6 else None
	cart = None
	product = None

	if product_id is not None and product_name:
		product_dto = ProductDTO(
			product_id=product_id,
			name=str(product_name),
			description="",
			stock=0,
			price=int(product_price) if product_price else 0,
			sku=None,
			is_available=False,
			category=None,
			brand=None
		)
		product = product_dto_to_entity(product_dto)

	return CartProduct(
		cart_product_id=cart_product_id,
		cart_id=cart_id,
		product_id=product_id,
		quantity=int(quantity) if quantity else 0,
		cart=cart,
		product=product
	)

def cart_product_dto_to_entity(dto: CartProductDTO):
	return dto_to_entity(dto)

def cart_product_entity_to_entity(entity: CartProduct):
	return entity_to_dto(entity)