import flet as ft
from core.abstracts.form import Form
from utils.helpers import field_category, field_brand, field_is_available, selected_option_text
from gui.validators.product_form_validator import FormProductValidator
from typing import Callable, Optional
from services.session_service import SessionService


class EditProductForm(Form):
	def __init__(self, on_submit: Callable):
		super().__init__("Editar producto", "edit_product")
		self.field_name: Optional[ft.TextField] = None
		self.field_desc: Optional[ft.TextField] = None
		self.field_stock: Optional[ft.TextField] = None
		self.field_price: Optional[ft.TextField] = None
		self.field_sku: Optional[ft.TextField] = None
		self.field_is_available: Optional[ft.Dropdown] = None
		self.field_category: Optional[ft.Dropdown] = None
		self.field_brand: Optional[ft.Dropdown] = None
		self.validator = FormProductValidator()
		self.on_submit = on_submit
		self.form_data: dict = {}

	def create_controls(self, form_data: dict) -> list[ft.Control]:
		session = SessionService()
		can_update_all = session.has_permission("product.update")
		can_update_details = can_update_all

		self.field_name = ft.TextField(
			label="Nombre producto",
			hint_text="Ingrese el nombre del producto",
			value=form_data.get('name', ''),
			disabled=not can_update_details,
			label_style=ft.TextStyle(size=20, height=5, weight=ft.FontWeight.NORMAL),
			border=ft.InputBorder.UNDERLINE,
			border_color=ft.Colors.WHITE,
		)

		self.field_desc = ft.TextField(
			label="Descripción",
			hint_text="Ingrese descripción",
			value=form_data.get('description', ''),
			disabled=not can_update_details,
			label_style=ft.TextStyle(size=20, height=5, weight=ft.FontWeight.NORMAL),
			border=ft.InputBorder.UNDERLINE,
			border_color=ft.Colors.WHITE,
		)

		self.field_stock = ft.TextField(
			label="Stock",
			hint_text="Ingrese la stock",
			keyboard_type=ft.KeyboardType.NUMBER,
			input_filter=ft.InputFilter(allow=True, regex_string=r"^\d*\.?\d*$"),
			value=str(form_data.get('stock', '')),
			label_style=ft.TextStyle(size=20, height=5, weight=ft.FontWeight.NORMAL),
			border=ft.InputBorder.UNDERLINE,
			border_color=ft.Colors.WHITE,
		)

		self.field_price = ft.TextField(
			label="Precio",
			hint_text="Ingrese el precio",
			keyboard_type=ft.KeyboardType.NUMBER,
			input_filter=ft.InputFilter(allow=True, regex_string=r"^\d*\.?\d*$"),
			value=str(form_data.get('price', '')),
			label_style=ft.TextStyle(size=20, height=5, weight=ft.FontWeight.NORMAL),
			border=ft.InputBorder.UNDERLINE,
			border_color=ft.Colors.WHITE,
		)

		self.field_sku = ft.TextField(
			label="Código",
			hint_text="Ingrese el código",
			value=form_data.get('sku', ''),
			disabled=not can_update_details,
			label_style=ft.TextStyle(size=20, height=5, weight=ft.FontWeight.NORMAL),
			border=ft.InputBorder.UNDERLINE,
			border_color=ft.Colors.WHITE,
		)

		self.field_is_available = field_is_available()
		self.field_category = field_category()
		self.field_brand = field_brand()

		if self.field_category is not None:
			self.field_category.disabled = not can_update_details
		if self.field_brand is not None:
			self.field_brand.disabled = not can_update_details

		if self.field_is_available is not None:
			self.field_is_available.value = form_data.get('is_available') or None
		if self.field_category is not None and form_data.get('category_id') not in (None, ""):
			self.field_category.value = str(form_data.get('category_id'))
		if self.field_brand is not None and form_data.get('brand_id') not in (None, ""):
			self.field_brand.value = str(form_data.get('brand_id'))

		button_submit = ft.ElevatedButton(
			text="Ingresar",
			style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.LIGHT_GREEN_600),
			on_click=lambda e: self.on_submit(self.get_data())
		)

		can_submit = can_update_all or can_update_details
		if not can_submit:
			button_submit.disabled = True
			button_submit.tooltip = "No tienes permisos para editar este producto"

		return [
			ft.Row([
				ft.Container(
					ft.Row([
						ft.Column([
							self.field_name,
							self.field_stock,
							self.field_sku,
							self.field_category,
						], alignment=ft.MainAxisAlignment.START, spacing=20),
						ft.Column([
							self.field_desc,
							self.field_price,
							self.field_is_available,
							self.field_brand,
						], spacing=20),
					], spacing=40, vertical_alignment=ft.CrossAxisAlignment.CENTER),
					margin=20
				),
			]),
			ft.Container(
				content=button_submit,
				alignment=ft.Alignment(0, 0),
				margin=ft.Margin(0,20,0,0)
			)
		]

	def get_data(self) -> dict:
		return {
			'name': self.field_name.value if self.field_name is not None else '',
			'description': self.field_desc.value if self.field_desc is not None else '',
			'stock': self.field_stock.value if self.field_stock is not None else '0',
			'price': self.field_price.value if self.field_price is not None else '0',
			'sku': self.field_sku.value if self.field_sku is not None else '',
			'is_available': self.field_is_available.value if self.field_is_available is not None else '',
			'category': self.field_category.value if self.field_category is not None else '',
			'brand': self.field_brand.value if self.field_brand is not None else '',
			'category_name': selected_option_text(self.field_category),
			'brand_name': selected_option_text(self.field_brand),
		}

	def validate(self) -> tuple[bool, list[str]]:
		data = self.get_data()
		return self.validator.validate_edit_product_form_data(data)

	def reset(self) -> None:
		pass