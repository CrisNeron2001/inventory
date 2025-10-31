import flet as ft
from typing import Optional
from services.category_service import CategoryService
from services.brand_service import BrandService
from services.product_service import ProductService


def get_products():
	return ProductService().get_all_products()

def get_categories():
	return CategoryService().get_all_categories()

def get_brands():
	return BrandService().get_all_brands()

def field_category():
	def get_category_options():
		options = []
		for c in get_categories():
			options.append(
				ft.DropdownOption(
					key=str(c.category_id),
					text=str(c.name),
				)
			)
		return options

	def dropdown_category_change(e: ft.ControlEvent) -> None:
		e.control.c = e.control.value

	ddc = ft.Dropdown(
		border=ft.InputBorder.UNDERLINE,
		enable_filter=True,
		editable=True,
		leading_icon=ft.Icons.SEARCH,
		label="Categorias",
		options=get_category_options(),
		on_change=dropdown_category_change,
		label_style=ft.TextStyle(size=20, height=1, weight=ft.FontWeight.NORMAL),
		border_color=ft.Colors.WHITE,
	)

	return ddc


def field_brand():
	def get_brand_options():
		options = []
		for b in get_brands():
			options.append(
				ft.DropdownOption(
					key=str(b.brand_id),
					text=str(b.name),
				)
			)
		return options

	def dropdown_brand_change(e: ft.ControlEvent) -> None:
		e.control.b = e.control.value

	ddb = ft.Dropdown(
		border=ft.InputBorder.UNDERLINE,
		enable_filter=True,
		editable=True,
		leading_icon=ft.Icons.SEARCH,
		label="Marcas",
		options=get_brand_options(),
		on_change=dropdown_brand_change,
		label_style=ft.TextStyle(size=20, height=1, weight=ft.FontWeight.NORMAL),
		border_color=ft.Colors.WHITE,
	)

	return ddb


def field_is_available():
	state_availability = {
		"Disponible": True,
		"No disponible": False,
	}

	def get_state_options():
		options = []
		for state in state_availability:
			options.append(
				ft.DropdownOption(key=str(state))
			)
		return options

	def dropdown_state_change(e: ft.ControlEvent) -> None:
		e.control.state = e.control.value

	ddsa = ft.Dropdown(
		border=ft.InputBorder.UNDERLINE,
		enable_filter=True,
		editable=True,
		leading_icon=ft.Icons.SEARCH,
		label="Estado",
		options=get_state_options(),
		on_change=dropdown_state_change,
		label_style=ft.TextStyle(size=20, height=1, weight=ft.FontWeight.NORMAL),
		border_color=ft.Colors.WHITE,
	)

	return ddsa


def autoincrement_id():
	try:
		lists = [
			("product_id", get_products()),
			("category_id", get_categories()),
			("brand_id", get_brands()),
		]
		max_id = 0
		for id_name, items in lists:
			for item in items:
				max_id = max(max_id, getattr(item, id_name, 0) or 0)
		return max_id + 1
	except Exception:
		return 1


def selected_option_text(dd: Optional[ft.Dropdown]) -> str:
	if dd is None or dd.value in (None, ""):
		return ""
	for opt in (dd.options or []):
		if str(getattr(opt, "key", "")) == str(dd.value):
			content = getattr(opt, "content", None)
			text_val = getattr(content, "value", None) if content else getattr(opt, "text", None)
			return str(text_val or "")
	return ""