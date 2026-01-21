import flet as ft
from typing import List, Optional, Callable
from services.cart_service import CartService
from core.models.dto.cart_product_dto import CartProductDTO
from services.sale_service import SaleService
from services.product_service import ProductService
from services.session_service import SessionService
from config.settings import log
from gui.components.steps.step_navigation import StepNavigator
from gui.components.steps.sale.product_selection_step import ProductSelectionStep
from gui.components.steps.sale.sale_summary_step import SaleSummaryStep
from gui.components.steps.sale.cash_payment_step import CashPaymentStep
from utils.pos_cart_manager import POSCartManager
from utils.pos_ui import POSUI
from utils.pos_navigation import POSNavigationHelper
from gui.components.dialog.validate.success.success_dialog import success_dialog
from gui.components.dialog.validate.error.error_dialog import error_dialog

class POSController:
	def __init__(
		self,
		page: ft.Page,
		router_callback: Optional[Callable] = None,
	):
		self.page = page
		self.router_callback = router_callback
		self.cart_service = CartService()
		self.sale_service = SaleService()
		self.session = SessionService()
		self.product_service = ProductService()

		self.steps = [ProductSelectionStep(), SaleSummaryStep(), CashPaymentStep()]
		self.navigator = StepNavigator(self.steps, self.on_step_changed)

		self.step_indicators = ft.Column(spacing=20, expand=False)
		self.content_container = ft.Column(expand=True)
		self.progress_bar = ft.ProgressBar(value=0, color=ft.Colors.BLUE_600)
		self.btn_prev = None
		self.btn_next = None
		self.products: List = []
		self.carts = []
		self.cart = []
		self.current_cart_id: Optional[int] = None
		self.selected_indices: set = set()
		self.cart_manager = POSCartManager(self, self.page)
		self.ui = POSUI(self)
		self.nav = POSNavigationHelper(self)

	def on_step_changed(self, step_index: int):
		self.ui.update_step_indicators()
		self.ui.update_content()
		self.ui.update_progress()
		self.nav.update_nav_buttons()

	def load_products(self):
		self.products = self.product_service.get_all_products()
		return self.products

	def load_carts(self):
		self.carts = self.cart_service.get_all_carts()
		return self.carts

	def add_to_cart(self, product_id: int, qty: int, cart_id: Optional[int] = None):
		return self.cart_manager.add_to_cart(product_id, qty)

	def remove_from_cart(self, index: int) -> None:
		return self.cart_manager.remove_from_cart(index)

	def cart_total(self) -> int:
		return self.cart_manager.cart_total()

	def confirm_sale(
		self,
		payment_method: str | None = None,
		payment_amount: int | None = None,
	) -> list | None:
		return self.cart_manager.confirm_sale(payment_method=payment_method, payment_amount=payment_amount)

	def create_form_layout(self) -> ft.Container:
		return self.ui.create_form_layout()

	def create_form_layout_internal(self) -> ft.Container:
		self.load_products()

		product_options = [
			ft.dropdown.Option(key=str(p.product_id), text=f"{p.name} - ${p.price}")
			for p in self.products
		]

		ddl = ft.Dropdown(options=product_options, width=360, hint_text="Selecciona producto", label="Producto")
		qty = ft.TextField(value="1", width=120, label="Cantidad")
		cart_list = ft.Column()
		total_lbl = ft.Text("Total: $0", size=18, weight=ft.FontWeight.BOLD)

		def refresh_cart():
			cart_list.controls.clear()
			for idx, it in enumerate(self.cart):
				cart_list.controls.append(
					ft.Row([
						ft.Text(f"{it['product'].name} x {it['qty']}", expand=True),
						ft.Text(f"${it['line_total']}"),
						ft.IconButton(icon=ft.Icons.DELETE, on_click=lambda e, i=idx: on_remove(i)),
					])
				)
			total_lbl.value = f"Total: ${self.cart_total()}"
			cart_list.update()
			total_lbl.update()

		def on_add(e: ft.ControlEvent):
			try:
				if ddl.value is None:
					self.show_validate_error_dialog(["Debe seleccionar un producto"])
					raise ValueError("[POSController.on_add] Debe seleccionar un producto")
				if qty.value is None or str(qty.value).strip() == "":
					self.show_validate_error_dialog(["Cantidad inválida"])
					raise ValueError("[POSController.on_add] Cantidad inválida")

				pid = int(str(ddl.value))
				q = int(str(qty.value))
				self.add_to_cart(pid, q)
				refresh_cart()
			except (ValueError, TypeError) as ve:
				self.show_error_dialog([str(ve)])

		def on_remove(index: int):
			try:
				cpid = getattr(self, 'current_cart_product_id', None)
				if cpid is not None and 0 <= index < len(self.cart):
					car = self.cart[index].get('cart')
					cid = getattr(car, 'cart_id', None)
					prod = self.cart[index].get('product')
					pid = getattr(prod, 'product_id', None)
					prod_name = getattr(prod, "name", "")
					if pid is not None:
						try:
							cp_dto = CartProductDTO(
								cart_product_id=cpid,
								cart_id=cid, 
								product_id=pid, 
								quantity=0, 
								cart=None, 
								product=None
							)
							self.cart_service.remove_products_by_cart(cp_dto)
						except Exception as ex:
							log.error(f"[POSController.on_remove] Error al remover producto persistido {prod_name}: {ex}")
							self.show_validate_error_dialog([f"Error al remover producto persistido {prod_name}"])

				if cid is not None:
					try:
						persisted = self.cart_service.get_cart_by_id(int(cid)) or []
						self.cart = []
						for cp in persisted:
							prod = getattr(cp, 'product', None) if not isinstance(cp, dict) else cp.get('product')
							raw_qty = getattr(cp, 'quantity', None) if not isinstance(cp, dict) else cp.get('quantity', None)
							try:
								qty = int(raw_qty or 0)
							except Exception:
								qty = 0
							if prod is None:
								continue
							line = {'product': prod, 'qty': qty, 'line_total': qty * int(getattr(prod, 'price', 0) or 0)}
							self.cart.append(line)
					except Exception:
						if 0 <= index < len(self.cart):
							self.cart.pop(index)
				else:
					if 0 <= index < len(self.cart):
						self.cart.pop(index)

			except Exception as ex:
				log.error(f"Error en on_remove: {ex}")

			refresh_cart()

		def on_confirm(e: ft.ControlEvent):
			created = self.confirm_sale()
			if created:
				log.info("[POSController.on_confirm] Pago realizado.")
				self.show_success_dialog("Pago realizado.")
			else:
				log.error("[POSController.on_confirm] No se hizo el pago correctamente.")
				self.show_validate_error_dialog(["No se hizo el pago correctamente"])

		add_btn = ft.ElevatedButton("Agregar", on_click=on_add)
		confirm_btn = ft.ElevatedButton("Confirmar venta", on_click=on_confirm, bgcolor=ft.Colors.GREEN_600)

		container = ft.Container(
			content=ft.Column([
				ft.Row([ddl, qty, add_btn]),
				ft.Divider(height=10),
				cart_list,
				ft.Divider(height=10),
				ft.Row([total_lbl, ft.Container(expand=True), confirm_btn]),
			]),
			padding=ft.Padding(20, 20, 20, 20),
			expand=True,
		)
		return container

	def update_step_indicators(self):
		return self.ui.update_step_indicators()

	def update_step_indicators_internal(self):
		self.step_indicators.controls.clear()
		for i, step in enumerate(self.steps):
			is_current = i == self.navigator.current_step
			is_completed = i < self.navigator.current_step

			if is_completed:
				color = ft.Colors.GREEN_600
				icon = ft.Icons.CHECK_CIRCLE
			elif is_current:
				color = ft.Colors.BLUE_600
				icon = ft.Icons.RADIO_BUTTON_CHECKED
			else:
				color = ft.Colors.GREY_400
				icon = ft.Icons.RADIO_BUTTON_UNCHECKED

			step_indicator = ft.Container(
				content=ft.Row([
					ft.Icon(icon, color=color, size=20),
					ft.Text(
						f"{i+1}. {step.title}",
						size=12 if not is_current else 14,
						weight=ft.FontWeight.BOLD if is_current else ft.FontWeight.NORMAL,
						color=color,
					),
				], vertical_alignment=ft.CrossAxisAlignment.CENTER),
				padding=ft.Padding(10, 8, 10, 8),
				border_radius=8,
				bgcolor=ft.Colors.ON_SURFACE_VARIANT if is_current else None,
			)
			self.step_indicators.controls.append(step_indicator)
			if getattr(self.step_indicators, 'page', None):
				self.step_indicators.update()

	def update_content(self):
		return self.ui.update_content()

	def update_content_internal(self):
		self.content_container.controls.clear()
		current = self.navigator.get_current_step()
		data = {}
		if isinstance(current, ProductSelectionStep):
			data['products'] = self.products
			data['on_add'] = (lambda pid, qty: self.add_to_cart(pid, qty))
			data['cart_service'] = self.cart_service
			data['cart_id'] = self.current_cart_id
		if isinstance(current, SaleSummaryStep):
			cid = getattr(self, 'current_cart_id', None)
			self.cart = []
			if cid is not None:
				persisted = self.cart_service.get_cart_by_id(int(cid)) or []
			else:
				persisted = []

			for cp in persisted:
				prod = getattr(cp, 'product', None) if not isinstance(cp, dict) else cp.get('product')
				raw_qty = getattr(cp, 'quantity', None) if not isinstance(cp, dict) else cp.get('quantity', None)
				qty = int(raw_qty or 0)

				if prod is None:
					if self.page is not None:
						self.show_error_dialog([f"Producto asociado al carrito no existe (cart_id={cid})"])
					continue

				line = {'product': prod, 'qty': qty, 'line_total': qty * int(getattr(prod, 'price', 0) or 0)}
				self.cart.append(line)

			data['cart'] = self.cart
			data['on_remove_selected'] = (lambda: self.remove_product_by_cart())
		if isinstance(current, CashPaymentStep):
			data['total'] = self.cart_total()

		controls = current.create_controls(data)
		self.content_container.controls.extend(controls)
		if getattr(self.content_container, 'page', None):
			self.content_container.update()

	def update_progress(self):
		return self.ui.update_progress()

	def update_progress_internal(self):
		progress = self.navigator.get_progress_percentage() / 100
		self.progress_bar.value = progress
		if getattr(self.progress_bar, 'page', None):
			self.progress_bar.update()

	def next_step(self, e: Optional[ft.ControlEvent] = None):
		return self.nav.next_step(e)

	def next_step_internal(self, e: Optional[ft.ControlEvent] = None):
		current = self.navigator.get_current_step()
		valid, errors = current.validate()
		if not valid:
			log.error(f"[POSController.next_step_internal] Hubo un error inesperado:", ";".join(errors))
			self.show_validate_error_dialog([";".join(errors)])
			return

		if isinstance(current, ProductSelectionStep):
			d = current.get_data()
			pid = d.get('product_id')
			qty = d.get('quantity')
			if pid and qty:
				prod = next((p for p in self.products if getattr(p, 'product_id', None) == pid), None)
				if prod:
					line = {'product': prod, 'qty': qty, 'line_total': qty * prod.price}
					self.cart.append(line)

		if isinstance(current, CashPaymentStep):
			d = current.get_data()
			try:
				amount = int(d.get('amount', 0) or 0)
			except (ValueError, TypeError):
				amount = 0
			total = int(self.cart_total() or 0)
			if amount < total:
				self.show_validate_error_dialog(["Monto insuficiente"])
				return
			created = self.confirm_sale(payment_method='cash', payment_amount=amount)
			if created:
				log.info(f"[POSController.next_step_internal] Pago realizado. Venta registrada con éxito: {created}")
				self.show_success_dialog("Pago realizado.")
				self.navigator.reset()
				self.cart.clear()
				self.on_step_changed(self.navigator.current_step)
				return
			else:
				log.error("[POSController.next_step_internal] Error finalizando venta.")
				self.show_validate_error_dialog(["Error finalizando venta"])

		self.navigator.next_step()

	def prev_step(self, e: Optional[ft.ControlEvent] = None):
		return self.nav.prev_step(e)

	def prev_step_internal(self, e: Optional[ft.ControlEvent] = None):
		self.navigator.prev_step()

	def update_nav_buttons(self) -> None:
		return self.nav.update_nav_buttons()

	def update_nav_buttons_internal(self) -> None:
		if self.btn_prev is not None:
			self.btn_prev.disabled = self.navigator.is_first_step()
			if getattr(self.btn_prev, 'page', None):
				self.btn_prev.update()
		if self.btn_next is not None:
			is_last = self.navigator.is_last_step()
			self.btn_next.text = "Finalizar" if is_last else "Siguiente"
			self.btn_next.icon = ft.Icons.CHECK if is_last else ft.Icons.ARROW_FORWARD
			self.btn_next.on_click = (lambda e: self.next_step(e))
			if getattr(self.btn_next, 'page', None):
				self.btn_next.update()

	def create_steps_layout(self) -> ft.Container:
		return self.ui.create_steps_layout()

	def create_steps_layout_internal(self) -> ft.Container:
		self.load_products()

		self.btn_prev = ft.ElevatedButton(
			"Anterior",
			icon=ft.Icons.ARROW_BACK,
			on_click=self.prev_step,
			disabled=self.navigator.is_first_step(),
		)
		self.btn_next = ft.ElevatedButton(
			"Siguiente",
			icon=ft.Icons.ARROW_FORWARD,
			on_click=self.next_step,
			disabled=False,
		)

		nav_buttons = ft.Row([self.btn_prev, self.btn_next], alignment=ft.MainAxisAlignment.CENTER)

		main_content = ft.Row(
			[
				ft.Container(
					content=ft.Column([
						ft.Text("Progreso", size=16, weight=ft.FontWeight.BOLD),
						self.progress_bar,
						ft.Divider(height=20),
						self.step_indicators,
					]),
					width=300,
					padding=ft.Padding(20, 20, 20, 20),
					border_radius=10,
				),
				ft.VerticalDivider(width=1),
				ft.Container(
					content=ft.Column([
						self.content_container,
						ft.Divider(height=20),
						nav_buttons,
					]),
					expand=True,
					padding=ft.Padding(20, 20, 20, 20),
				),
			],
			expand=True,
			alignment=ft.MainAxisAlignment.START,
		)

		self.update_step_indicators()
		self.update_content()
		self.update_progress()
		self.update_nav_buttons()
		return ft.Container(content=main_content, expand=True, padding=ft.Padding(20, 20, 20, 20))

	def on_select_cart_line(self, idx: int, checked: bool) -> None:
		return self.cart_manager.on_select_cart_line(idx, checked)

	def remove_product_by_cart(self) -> None:
		return self.cart_manager.remove_product_by_cart()
		
	def show_error_dialog(self, errors: list[str]):
		error_msg = "\n".join(errors)
		error_dialog(self.page, error_msg, on_close=lambda: self.page.go("/sales"))
		
	def show_validate_error_dialog(self, errors: list[str]):
		error_msg = "\n".join(errors)
		error_dialog(self.page, error_msg) 
		
	def show_success_dialog(self, msg: str):
		success_dialog(self.page, msg, on_close=lambda: self.page.go("/sales"))
