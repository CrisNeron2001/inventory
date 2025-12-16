import flet as ft
from typing import Optional, List
from services.cart_service import CartService
from services.sale_service import SaleService
from services.product_service import ProductService
from services.session_service import SessionService
from core.models.dto.cart_dto import CartDTO
from core.models.dto.cart_product_dto import CartProductDTO
from core.models.dto.sale_dto import SaleDTO
from core.exceptions.exception import AuthorizationFailure
from config.settings import log
from utils.helpers import autoincrement_id

class POSCartManager:
	def __init__(self, controller):
		self.controller = controller
		self.cart_service: CartService = controller.cart_service
		self.sale_service: SaleService = controller.sale_service
		self.product_service: ProductService = controller.product_service
		self.session: SessionService = controller.session
		self.cart: List[dict] = controller.cart

	def add_to_cart(self, product_id: int, qty: int) -> CartProductDTO | None:
		if qty <= 0:
			return None

		prod = next((p for p in self.controller.products if getattr(p, 'product_id', None) == product_id), None)
		if not prod:
			return None

		current_user = self.session.get_current_user()
		user_id = getattr(current_user, 'user_inv_id', None) if current_user else None
		created_cart = None

		if self.controller.current_cart_id is None:
			if not user_id:
				page = getattr(self.controller, 'page', None)
				if page is not None:
					page.snack_bar = ft.SnackBar(ft.Text("Debe iniciar sesión para crear un carrito."), open=True)
					page.update()
				log.error("Intento de crear carrito sin usuario autenticado (user_id is None). Aborting create_cart.")
				return None

			cart_dto = CartDTO(cart_id=None, user_inv_id=user_id, user_inv=None)
			created_cart = self.cart_service.create_cart(cart_dto)
			if not created_cart:
				page = getattr(self.controller, 'page', None)
				if page is not None:
					page.snack_bar = ft.SnackBar(ft.Text("No se pudo crear el carrito. Intenta iniciar sesión o intenta de nuevo."), open=True)
					page.update()
				log.error("create_cart devolvió None; abortando add_to_cart")
				return None

			self.controller.current_cart_id = getattr(created_cart, 'cart_id', None)
			log.info(f"Carrito creado y asignado current_cart_id={self.controller.current_cart_id}")

		else:
			current_stock = getattr(prod, 'stock', None)
			if current_stock is None:
				current_stock = getattr(prod, 'quantity', None)
			current_stock = int(current_stock or 0)
			log.info(f"Validando stock para product_id={product_id}: requested={qty}, available={current_stock}")
			if qty > current_stock:
				page = getattr(self.controller, 'page', None)
				if page is not None:
					page.snack_bar = ft.SnackBar(ft.Text(f"Stock insuficiente. Disponible: {current_stock}"), open=True)
					page.update()
				return None

		if getattr(self, 'controller', None) and getattr(self.controller, 'current_cart_id', None) is None:
			log.error("No current_cart_id available when attempting to create cart_product; aborting")
			page = getattr(self.controller, 'page', None)
			if page is not None:
				page.snack_bar = ft.SnackBar(ft.Text("Error interno: carrito no disponible."), open=True)
				page.update()
			return None

		if product_id is None:
			log.error("product_id is None when attempting to add to cart; aborting")
			return None

		cp_dto = CartProductDTO(
			cart_product_id=autoincrement_id(),
			cart_id=self.controller.current_cart_id, 
			product_id=product_id, 
			quantity=qty, 
			cart=None, 
			product=None
		)
		log.info(f"POSCartManager.add_to_cart preparing to call create_cart_product_with_decrement with cp_dto: {cp_dto}")
		created_cp = self.cart_service.create_cart_product_with_decrement(cp_dto)
		if created_cp:
			log.info(f"create_cart_product devolvió: {created_cp}")
		else:
			log.warning(f"create_cart_product devolvió None para cart_id={self.controller.current_cart_id}, product_id={product_id}, quantity={qty}")

		display_price = None
		display_name = None
		if created_cp:
			prod_info = getattr(created_cp, 'product', None) if not isinstance(created_cp, dict) else created_cp.get('product')
			if prod_info:
				display_name = getattr(prod_info, 'name', None) if not isinstance(prod_info, dict) else prod_info.get('name')
				display_price = getattr(prod_info, 'price', None) if not isinstance(prod_info, dict) else prod_info.get('price')
		if display_price is None and prod is not None:
			display_price = getattr(prod, 'price', 0)
		if display_name is None and prod is not None:
			display_name = getattr(prod, 'name', None)

		line = {'product': prod, 'qty': qty, 'line_total': qty * (display_price or 0), 'cart_product': created_cp}
		self.cart.append(line)
		return created_cp

	def remove_from_cart(self, index: int) -> None:
		if 0 <= index < len(self.cart):
			self.cart.pop(index)

	def cart_total(self) -> int:
		return sum(item['line_total'] for item in self.cart)

	def confirm_sale(self, payment_method: Optional[str] = None, payment_amount: Optional[int] = None) -> Optional[List]:
		current_user = self.session.get_current_user()
		user_id = getattr(current_user, 'user_inv_id', None) if current_user else None
		if not user_id:
			raise AuthorizationFailure("No hay usuario autenticado para registrar la venta.")
		if not self.cart:
			return None

		use_cart_id = getattr(self.controller, 'current_cart_id', None)
		created_cart = None
		if not use_cart_id:
			cart_dto = CartDTO(cart_id=None, user_inv_id=user_id, user_inv=None)
			created_cart = self.cart_service.create_cart(cart_dto)
			if not created_cart:
				raise Exception("No se pudo crear el carrito")
			use_cart_id = getattr(created_cart, 'cart_id', None)
			self.controller.current_cart_id = use_cart_id

		sale_dto = SaleDTO(
			sale_id=None,
			cart_id=use_cart_id,
			sale_date=None,
			notes=None,
		)
		created_sale = self.sale_service.create_sale(sale_dto)

		self.cart.clear()
		self.controller.current_cart_id = None
		return [created_sale] if created_sale else []

	def on_select_cart_line(self, idx: int, checked: bool) -> None:
		if checked:
			self.controller.selected_indices.add(idx)
		else:
			self.controller.selected_indices.discard(idx)
		self.controller.update_content()

	def remove_product_by_cart(self) -> None:
		selected = self.controller.selected_indices
		if not selected:
			return

		if self.controller.current_cart_id is not None:
			pids = [getattr(self.cart[i]['product'], 'product_id', None) for i in selected if i < len(self.cart)]
			log.info(f"POSCartManager.remove_product_by_cart: selected_indices={selected}, cart_id={self.controller.current_cart_id}, product_ids={pids}")
			cp_dto = CartProductDTO(
				cart_product_id=autoincrement_id(),
				cart_id=self.controller.current_cart_id, 
				product_id=self.controller.current_product_id, 
				quantity=0, 
				cart=None, 
				product=None
			)
			setattr(cp_dto, 'product_id', pids)
			self.cart_service.remove_products_by_cart(cp_dto)

		for i in sorted(selected, reverse=True):
			if 0 <= i < len(self.cart):
				self.cart.pop(i)

		self.controller.selected_indices.clear()
		self.controller.update_content()