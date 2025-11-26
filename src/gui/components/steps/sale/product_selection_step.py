from core.abstracts.form import Form
from core.models.dto.cart_product_dto import CartProductDTO
from typing import Optional, List, Any
import flet as ft
from config.settings import log


class ProductSelectionStep(Form):
	def __init__(self):
		super().__init__("Seleccionar productos", "product_selection")
		self.ddl: Optional[ft.Dropdown] = None
		self.qty: Optional[ft.TextField] = None
		self.add_btn: Optional[ft.ElevatedButton] = None
		self.added_container: Optional[ft.Column] = None
		self.added_products: list[dict] = []

		self._products: List[Any] = []
		self._products_by_id: dict = {}
		self._on_add_callback = None
		self._cart_service = None
		self._cart_id: Any = None

	def _reload_lines(self):
		if self.added_products is None:
			self.added_products = []
		if self.added_container is None:
			self.added_container = ft.Column(spacing=6)

		self.added_products.clear()
		self.added_container.controls.clear()

		if getattr(self, '_cart_service', None) and getattr(self, '_cart_id', None):
			get_cart = getattr(self._cart_service, 'get_cart_by_id', None)
			lines = []

			cart_id_int = int(self._cart_id)

			if callable(get_cart):
				if cart_id_int is not None:
					lines = get_cart(cart_id_int) or []
				else:
					lines = []
			else:
				get_all = getattr(self._cart_service, 'get_all_carts', None)
				if callable(get_all):
					all_c = get_all() or []
					if not isinstance(all_c, (list, tuple, set)):
						all_c = [all_c]
					for cp in all_c:
						cid = cp.get('cart_id') if isinstance(cp, dict) else getattr(cp, 'cart_id', None)
						if cid is not None and cart_id_int is not None and int(str(cid)) == cart_id_int:
							lines.append(cp)

			if not isinstance(lines, list):
				if isinstance(lines, (tuple, set)):
					lines = list(lines)
				else:
					lines = [lines]

			for cp in lines:
				if isinstance(cp, dict):
					pid = cp.get('product_id')
					qty = cp.get('quantity')
					prod = cp.get('product')
				else:
					pid = getattr(cp, 'product_id', None)
					qty = getattr(cp, 'quantity', None)
					prod = getattr(cp, 'product', None)

				pname = None
				pprice = None
				if prod:
					if isinstance(prod, dict):
						pname = prod.get('name')
						pprice = prod.get('price')
					else:
						pname = getattr(prod, 'name', None)
						pprice = getattr(prod, 'price', None)
				else:
					p = self._products_by_id.get(pid)
					if p:
						pname = getattr(p, 'name', None)
						pprice = getattr(p, 'price', None)

				label = f"{pname} - ${pprice}" if pname is not None else None
				item = {"product_id": pid, "quantity": qty, "label": label}
				self.added_products.append(item)
				idx = len(self.added_products) - 1
				remove_btn = ft.IconButton(
					icon=ft.Icons.DELETE, 
					tooltip="Quitar", 
					on_click=lambda ev, 
					i=idx: self._remove_item(i)
				)
				row = ft.Row(
					[
						ft.Text(
							f"{item.get('label') or f'Producto {pid}'} x{qty}", 
							expand=True
						), 
						remove_btn
					], 
					alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
				self.added_container.controls.append(row)

		page = getattr(self.added_container, 'page', None)
		if page is not None:
			page.update()
		# If the control is not yet added to the page, avoid calling update()
		# because Flet raises `AssertionError: Column Control must be added to the page first`.

	def create_controls(self, form_data: dict) -> list[ft.Control]:
		products: List[Any] = form_data.get("products", [])
		self._products = products
		self._products_by_id = {getattr(p, 'product_id', None): p for p in products}
		self._on_add_callback = form_data.get('on_add')
		self._cart_service = form_data.get('cart_service')
		self._cart_id = form_data.get('cart_id')

		options = [ft.dropdown.Option(key=str(p.product_id), text=f"{p.name} - ${p.price}") for p in products]
		self.ddl = ft.Dropdown(options=options, width=360, hint_text="Selecciona producto", label="Producto")
		self.qty = ft.TextField(value="1", width=120, label="Cantidad")
		self.add_btn = ft.ElevatedButton(text="Agregar", on_click=self._on_add_click)

		self.added_container = ft.Column(spacing=6)

		if getattr(self, '_cart_service', None) and getattr(self, '_cart_id', None):
			self._reload_lines()

		left = ft.Column([self.ddl, self.qty, self.add_btn], spacing=8)
		right = ft.Container(
			content=ft.Column([
				ft.Text("Productos agregados", weight=ft.FontWeight.W_600),
				ft.Divider(),
				self.added_container,
			], spacing=6),
			padding=ft.Padding(8, 8, 8, 8),
			border=ft.border.all(1, ft.Colors.GREY_700),
			width=420,
			height=240,
		)

		return [ft.Text(self.title, size=18), ft.Row([left, right], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)]

	def get_data(self) -> dict:
		return {
			"cart_items": list(self.added_products),
		}

	def validate(self) -> tuple[bool, list[str]]:
		errors: list[str] = []
		if not self.added_products:
			errors.append("Debe agregar al menos un producto")
		return (len(errors) == 0, errors)

	def reset(self) -> None:
		self.ddl = None
		self.qty = None
		self.added_products = []
		if self.added_container is not None:
			self.added_container.controls.clear()
			self.added_container.update()

	def _on_add_click(self, e: ft.ControlEvent) -> None:
		if not self.ddl or not self.ddl.value:
			return
		pid = int(self.ddl.value)
		qty = int(str(self.qty.value)) if self.qty and self.qty.value else 0
		if qty <= 0:
			return

		text = None
		for opt in (self.ddl.options or []):
			if str(opt.key) == str(pid):
				text = opt.text
				break

		item = {"product_id": pid, "quantity": qty, "label": text}
		created = None

		if hasattr(self, '_on_add_callback') and callable(self._on_add_callback):
			created = self._on_add_callback(pid, qty)

		pname = None
		pprice = None
		if created:
			prod_info = getattr(created, 'product', None) if not isinstance(created, dict) else created.get('product')
			if prod_info:
				if not isinstance(prod_info, dict):
					pname = getattr(prod_info, 'name', None)
					pprice = getattr(prod_info, 'price', None)
				else:
					pname = prod_info.get('name')
					pprice = prod_info.get('price')

		if not pname:
			p = self._products_by_id.get(pid)
			if p:
				pname = getattr(p, 'name', None)
				pprice = getattr(p, 'price', None)

		if pname:
			item['label'] = f"{pname} - ${pprice}"

		self.added_products.append(item)

		idx = len(self.added_products) - 1
		remove_btn = ft.IconButton(
			icon=ft.Icons.DELETE, 
			tooltip="Quitar", 
			on_click=lambda ev, 
			i=idx: self._remove_item(i)
		)
		row = ft.Row(
			[
				ft.Text(
					f"{item.get('label')} x{qty}", 
					expand=True
				), remove_btn
			], 
			alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
		if self.added_container is not None:
			self.added_container.controls.append(row)
			self.added_container.update()

	def _remove_item(self, index: int) -> None:
		if index < 0 or index >= len(self.added_products):
			return
		if getattr(self, '_cart_service', None) and getattr(self, '_cart_id', None):
			item = self.added_products[index]
			pid = item.get('product_id')
			cart_id_int = int(self._cart_id)
			if pid is not None and cart_id_int is not None:
				cp = CartProductDTO(cart_id=cart_id_int, product_id=pid, quantity=0, cart=None, product=None)
				svc = getattr(self, '_cart_service', None)
				remove_fn = getattr(svc, 'remove_products_by_cart', None)
				if callable(remove_fn):
					try:
						log.info(f"ProductSelectionStep._remove_item calling remove_products_by_cart for cart_id={cart_id_int}, product_id={pid}")
						res = remove_fn(cp)
						log.info(f"ProductSelectionStep._remove_item remove_fn result: {res}")
					except Exception as e:
						log.error(f"Error calling remove_products_by_cart: {e}")

			if getattr(self, '_cart_service', None) and getattr(self, '_cart_id', None):
				self._reload_lines()
				return

		self.added_products.pop(index)
		if self.added_container is not None:
			self.added_container.controls.clear()
			for idx, item in enumerate(self.added_products):
				remove_btn = ft.IconButton(
					icon=ft.Icons.DELETE, 
					tooltip="Quitar", 
					on_click=lambda ev, 
					i=idx: self._remove_item(i)
				)
				row = ft.Row(
					[
						ft.Text(
							f"{item.get('label')} x{item.get('quantity')}", 
			  				expand=True
						), remove_btn
					], 
				 alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
				self.added_container.controls.append(row)
			self.added_container.update()
