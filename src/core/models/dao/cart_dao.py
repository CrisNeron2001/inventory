from typing import Any, List, Optional
from core.database.connections import DatabaseConnection
from core.database.queries import (
	insert_cart,
	select_all_carts,
	select_cart_by_id,
	insert_cart_product,
	remove_product_from_cart
)
from core.database.queries import update_product_decrease_if_enough
from core.models.mapper.cart_mapper import row_to_entity as c_r_t
from core.models.mapper.cart_product_mapper import row_to_entity as cp_r_t
from core.models.entity.cart_entity import Cart
from core.models.entity.cart_product_entity import CartProduct
from config.settings import log

class CartDAO:
	def __init__(self):
		self.db_conn = DatabaseConnection.get_connection_db()
		self.cursor = self.db_conn.cursor() if self.db_conn else None

	def create_cart(self, cart: Cart) -> Optional[Cart]:
		user_inv_id = getattr(cart, 'user_inv_id', None)
		if user_inv_id is None:
			temp_user = getattr(cart, 'user_inv', None)
			if temp_user is not None:
				user_inv_id = getattr(temp_user, 'user_inv_id', None)

		params = (user_inv_id,)
		if user_inv_id is None:
			log.error(f"[CartDAO.create_cart] No se ha podido crear un carrito: {cart}.")
			return None
		if self.cursor and self.db_conn:
			log.info("[CartDAO.create_cart] Creando un nuevo carrito.")
			self.cursor.execute(insert_cart, params)
			self.db_conn.commit()
			row: Any = self.cursor.fetchone()
			if not row:
				log.error("[CartDAO.create_cart] No se pudo crear el carrito. No se devolvió fila.")
				return None
			cart_created = c_r_t(row=list(row))
			log.info(f"[CartDAO.create_cart] Carrito creado: {cart_created}.")
			return cart_created
		else:
			log.error("[CartDAO.create_cart] Error al crear un carrito.")
			return None

	def create_cart_product(self, cart: CartProduct) -> Optional[CartProduct]:
		params = (
			getattr(cart, 'cart_id', None) if getattr(cart, 'cart_id', None) is not None else (cart.cart.cart_id if cart.cart else None),
			getattr(cart, 'product_id', None) if getattr(cart, 'product_id', None) is not None else (cart.product.product_id if cart.product else None),
			cart.quantity,
		)
		if self.cursor and self.db_conn:
			log.info("[CartDAO.create_cart_product] Creando nuevo producto en carrito.")
			self.cursor.execute(insert_cart_product, params)
			self.db_conn.commit()
			row: Any = self.cursor.fetchone()
			if not row:
				log.error("[CartDAO.create_cart_product] No se pudo crear el producto en el carrito; no se devolvió fila.")
				return None
			cart_product_created = cp_r_t(row=list(row))
			log.info(f"[CartDAO.create_cart_product] Producto en carrito creado: {cart_product_created}.")
			return cart_product_created
		else:
			log.error("[CartDAO.create_cart_product] Error al crear producto en carrito.")
			return None

	def create_cart_product_with_decrement(self, cart: CartProduct) -> Optional[CartProduct]:
		params = (
			getattr(cart, 'cart_id', None) if getattr(cart, 'cart_id', None) is not None else (cart.cart.cart_id if cart.cart else None),
			getattr(cart, 'product_id', None) if getattr(cart, 'product_id', None) is not None else (cart.product.product_id if cart.product else None),
			cart.quantity,
		)

		if not (self.cursor and self.db_conn):
			log.error("[CartDAO.create_cart_product_with_decrement] Error al crear producto en carrito con decremento: sin conexión DB.")
			return None

		try:
			log.info(f"[CartDAO.create_cart_product_with_decrement] Creando/actualizando cart_product y decrementando stock en una transacción: params={params}.")
			self.cursor.execute(insert_cart_product, params)
			cp_row = self.cursor.fetchone()
			if not cp_row:
				log.error("[CartDAO.create_cart_product_with_decrement] No se obtuvo fila creada en insert_cart_product.")
				self.db_conn.rollback()
				return None
			
			dec_product_id = getattr(cart, 'product_id', None) if getattr(cart, 'product_id', None) is not None else (cart.product.product_id if cart.product else None)
			dec_params = (cart.quantity, dec_product_id, cart.quantity)
			self.cursor.execute(update_product_decrease_if_enough, dec_params)
			dec_row = self.cursor.fetchone()
			if not dec_row:
				self.db_conn.rollback()
				log.warning(f"[CartDAO.create_cart_product_with_decrement] No hay stock suficiente para product_id={dec_product_id}.")
				return None

			self.db_conn.commit()
			created = cp_r_t(list(cp_row))
			log.info(f"[CartDAO.create_cart_product_with_decrement] Producto en carrito creado con decremento: {created}.")
			return created
		except Exception as ex:
			try:
				self.db_conn.rollback()
			except Exception:
				pass
			log.error(f"[CartDAO.create_cart_product_with_decrement] Error en create_cart_product_with_decrement: {ex}.")
			return None

	def get_cart_by_id(self, cart_id: int) -> List[CartProduct]:
		if self.cursor and self.db_conn:
			log.info("[CartDAO.get_cart_by_id] Obteniendo por el id de carrito.")
			self.cursor.execute(select_cart_by_id, (cart_id,))
			rows: List[Any] = self.cursor.fetchall()
			if not rows:
				log.info(f"[CartDAO.get_cart_by_id] No se encontraron productos para cart_id={cart_id}.")
				return []
			carts = [cp_r_t(list(row)) for row in rows]
			log.info(f"[CartDAO.get_cart_by_id] Carrito obtenido por id: {cart_id}, items={len(carts)}.")
			return carts
		else:
			log.error("[CartDAO.get_cart_by_id] Error al obtener por el id de carrito.")
			return []

	def get_all_carts(self) -> List[CartProduct]:
		if self.cursor and self.db_conn:
			log.info("[CartDAO.get_all_carts] Obteniendo a todos los carritos.")
			self.cursor.execute(select_all_carts)
			rows: List[Any] = self.cursor.fetchall()
			carts = [cp_r_t(list(row)) for row in rows]
			log.info(f"[CartDAO.get_all_carts] Todos los carritos obtenidos: {carts}.")
			return carts
		else:
			log.error("[CartDAO.get_all_carts] Error al obtener todas las categorias.")
			return []

	def remove_products_by_cart(self, cart: CartProduct) -> Optional[CartProduct]:
		if not (self.cursor and self.db_conn):
			log.error("[CartDAO.remove_products_by_cart] Error al remover productos del carrito.")
			return None

		log.info("[CartDAO.remove_products_by_cart] Removiendo productos del carrito.")
		pids = getattr(cart, "product_id", None)
		if pids is None:
			log.warning("[CartDAO.remove_products_by_cart] No hay productos para remover en el carrito.")
			return cart

		if isinstance(pids, (str, bytes)):
			pids_list = [pids]
		else:
			try:
				pids_list = list(pids)
			except TypeError:
				pids_list = [pids]

		log.info(f"[CartDAO.remove_products_by_cart] Intentando remover product_ids={pids_list} desde cart_id={cart.cart_id}.")

		for pid in pids_list:
			params = (pid, cart.cart_id)
			log.info(f"[CartDAO.remove_products_by_cart] Ejecutando DELETE para product_id={pid} cart_id={cart.cart_id} params={params}.")
			self.cursor.execute(remove_product_from_cart, params)
			row = None
			try:
				row = self.cursor.fetchone()
				log.info(f"[CartDAO.remove_products_by_cart] DELETE RETURNING row: {row}.")
			except AttributeError:
				log.info("[CartDAO.remove_products_by_cart] Cursor no soporta fetchone tras DELETE.")
			rc = getattr(self.cursor, 'rowcount', None)
			log.info(f"[CartDAO.remove_products_by_cart] Cursor rowcount after delete: {rc}.")
			self.db_conn.commit()
		log.info("[CartDAO.remove_products_by_cart] Productos removidos del carrito.")
		return cart
