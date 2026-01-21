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
		uid = getattr(cart_dto, 'user_inv_id', None)
		if uid is None:
			log.error(f"[CartService.create_cart] No se encontró id de usuario: {cart_dto}")
			return None
		cart = cart_dto_to_entity(cart_dto)
		new_cart = self.dao.create_cart(cart)
		log.info(f"[CartService.create_cart] Creando un nuevo carrito: {new_cart}")
		return cart_entity_to_dto(new_cart) if new_cart else None
	
	def create_cart_product(self, cart_dto: CartProductDTO) -> CartProductDTO | None:
		cart = cp_dto_to_entity(cart_dto)
		new_cart = self.dao.create_cart_product(cart)
		log.info(f"[CartService.create_cart_product] Creando un nuevo cart_product: {new_cart}")
		return cp_entity_to_dto(new_cart) if new_cart else None

	def create_cart_product_with_decrement(self, cart_dto: CartProductDTO) -> CartProductDTO | None:
		cart = cp_dto_to_entity(cart_dto)
		new_cart = self.dao.create_cart_product_with_decrement(cart)
		log.info(f"[CartService.create_cart_product_with_decrement] Creando un nuevo cart_product con decremento: {new_cart}")
		return cp_entity_to_dto(new_cart) if new_cart else None
	  
	def get_cart_by_id(self, cart_id: int) -> list[CartProductDTO]:
		carts = self.dao.get_cart_by_id(cart_id) or []
		log.info(f"[CartService.get_cart_by_id] Obteniendo un carrito por id: {cart_id}, items={len(carts)}")
		return [cp_entity_to_dto(cart) for cart in carts]
	
	def get_all_carts(self) -> List[CartProductDTO]:
		carts = self.dao.get_all_carts()
		log.info(f"[CartService.get_all_carts] Obteniendo todos los carritos: {carts}")
		return [cp_entity_to_dto(cart) for cart in carts]
	
	def remove_products_by_cart(self, cart_dto: CartProductDTO) -> CartProductDTO | None:
		cart = cp_dto_to_entity(cart_dto)
		remove_product = self.dao.remove_products_by_cart(cart)
		log.info(f"[CartService.remove_products_by_cart] Removiendo producto desde el carrito: {remove_product}")
		return cp_entity_to_dto(remove_product) if remove_product else None