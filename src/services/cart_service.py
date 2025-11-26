from core.models.dao.cart_dao import CartDAO
from core.models.dto.cart_dto import CartDTO
from core.models.dto.cart_product_dto import CartProductDTO
from core.models.mapper.cart_mapper import dto_to_entity as cart_dto_to_entity, entity_to_dto as cart_entity_to_dto
from core.models.mapper.cart_product_mapper import dto_to_entity as cp_dto_to_entity, entity_to_dto as cp_entity_to_dto
from typing import List
from config.settings import log

class CartService:
	def __init__(self):
		self.dao = CartDAO()

	def create_cart(self, cart_dto: CartDTO) -> CartDTO | None:
		# Validate presence of user_inv_id to avoid DB NOT NULL violations
		uid = getattr(cart_dto, 'user_inv_id', None)
		if uid is None:
			log.error(f"create_cart called without user_inv_id in CartDTO: {cart_dto}")
			return None
		cart = cart_dto_to_entity(cart_dto)
		new_cart = self.dao.create_cart(cart)
		log.info(f"Nuevo carrito creado: {new_cart}")
		return cart_entity_to_dto(new_cart) if new_cart else None
	
	def create_cart_product(self, cart_dto: CartProductDTO) -> CartProductDTO | None:
		cart = cp_dto_to_entity(cart_dto)
		new_cart = self.dao.create_cart_product(cart)
		log.info(f"Nuevo cart_product creado: {new_cart}")
		return cp_entity_to_dto(new_cart) if new_cart else None

	def create_cart_product_with_decrement(self, cart_dto: CartProductDTO) -> CartProductDTO | None:
		# Diagnostic: log incoming DTO and mapped entity to detect missing ids
		log.info(f"create_cart_product_with_decrement called with DTO: {cart_dto}")
		cart = cp_dto_to_entity(cart_dto)
		log.info(f"Mapped CartProduct entity before DAO call: cart_id={getattr(cart, 'cart_id', None)}, product_id={getattr(cart, 'product_id', None)}, cart_obj={getattr(cart, 'cart', None)}, product_obj={getattr(cart, 'product', None)}, quantity={getattr(cart, 'quantity', None)}")
		new_cart = self.dao.create_cart_product_with_decrement(cart)
		log.info(f"Nuevo cart_product creado (with decrement): {new_cart}")
		return cp_entity_to_dto(new_cart) if new_cart else None
	
	def get_cart_by_id(self, cart_id: int) -> list[CartProductDTO]:
		carts = self.dao.get_cart_by_id(cart_id) or []
		log.info(f"Carrito obtenido por id: {cart_id}, items={len(carts)}")
		return [cp_entity_to_dto(cart) for cart in carts]
	
	def get_all_carts(self) -> List[CartProductDTO]:
		carts = self.dao.get_all_carts()
		log.info(f"Obtenido todos los carritos: {carts}")
		return [cp_entity_to_dto(cart) for cart in carts]
	
	def remove_products_by_cart(self, cart_dto: CartProductDTO) -> CartProductDTO | None:
		cart = cp_dto_to_entity(cart_dto)
		remove_product = self.dao.remove_products_by_cart(cart)
		log.info(f"Producto removido desde el carrito: {remove_product}")
		return cp_entity_to_dto(remove_product) if remove_product else None