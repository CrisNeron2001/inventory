from core.models.entity.cart_product_entity import CartProduct
from core.models.dto.cart_product_dto import CartProductDTO
from core.models.dto.cart_dto import CartDTO
from core.models.dto.product_dto import ProductDTO
from core.models.mapper.cart_mapper import cart_dto_to_entity, cart_entity_to_dto
from core.models.mapper.product_mapper import product_dto_to_entity, product_entity_to_dto
from typing import Any, List


def dto_to_entity(dto: CartProductDTO) -> CartProduct:
	return CartProduct(
		cart_id=dto.cart_id,
		product_id=dto.product_id,
		quantity=dto.quantity,
		cart=cart_dto_to_entity(dto.cart) if dto.cart else None,
		product=product_dto_to_entity(dto.product) if dto.product else None
	)

def entity_to_dto(entity: CartProduct) -> CartProductDTO:
	if entity.cart and isinstance(entity.cart, int):
		cart_dto = CartDTO(cart_id=entity.cart_id, user_inv_id=None, user_inv=None)
	else:
		cart_dto = cart_entity_to_dto(entity.cart) if entity.cart else None
	if entity.product and isinstance(entity.product, str):
		p_dto = ProductDTO(
			product_id=None,
			name=entity.product,
			description="",
			stock=0,
			price=0,
			sku=None,
			is_available=False,
			category=None,
			brand=None
		)
	else:
		p_dto = product_entity_to_dto(entity.product) if entity.product else None

	return CartProductDTO(
		cart_id=entity.cart_id,
		product_id=entity.product_id,
		quantity=entity.quantity,
		cart=cart_dto,
		product=p_dto
	)

def row_to_entity(row: List[Any]) -> CartProduct:
	cart_id = row[0] if len(row) > 0 else None
	product_id = row[1] if len(row) > 1 else None
	quantity = row[2] if len(row) > 2 else None
	cart = None
	product = None

	if len(row) == 3:
		pass
	elif len(row) >= 6:
		cart = None
		product_dto = ProductDTO(
			product_id=row[2],
			name=str(row[3]) if len(row) > 3 and row[3] is not None else "",
			description="",
			stock=0,
			price=int(row[4]) if len(row) > 4 else 0,
			sku=None,
			is_available=False,
			category=None,
			brand=None
		)
		product = product_dto_to_entity(product_dto)
		quantity = row[5]
		product_id = row[2]
	else:
		if len(row) > 3:
			cart = row[3]
		if len(row) > 4:
			raw_product = row[4]
			if isinstance(raw_product, dict):
				product_dto = ProductDTO(
					product_id=raw_product.get('product_id'),
					name=str(raw_product.get('name')),
					description=raw_product.get('description', ""),
					stock=raw_product.get('stock', 0),
					price=int(raw_product.get('price', 0)),
					sku=raw_product.get('sku'),
					is_available=raw_product.get('is_available', False),
					category=raw_product.get('category'),
					brand=raw_product.get('brand')
				)
				product = product_dto_to_entity(product_dto)
			else:
				product = raw_product

	return CartProduct(
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