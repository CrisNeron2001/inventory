from services.product_service import ProductService
from services.category_service import CategoryService
from services.brand_service import BrandService
from gui.validators.product_form_validator import FormProductValidator
from gui.components.form.edit_product_form import EditProductForm
from core.models.dto.product_dto import ProductDTO
from core.models.dto.category_dto import CategoryDTO
from core.models.dto.brand_dto import BrandDTO
from typing import Optional, Callable
from config.settings import log
import flet as ft

class EditProductFormController:
	def __init__(self, product_id: int, on_saved: Optional[Callable[[], None]] = None) -> None:
		self.product_service = ProductService()
		self.validators = FormProductValidator()
		self.product_form = EditProductForm(self.on_submit)
		self.form_data: dict = {}
		self.product_id = product_id
		self.on_saved = on_saved
		try:
			product = self.product_service.get_product_by_id(product_id)
			if product:
				cat_id = getattr(getattr(product, "category", None), "category_id", None)
				br_id = getattr(getattr(product, "brand", None), "brand_id", None)
				mapping = {
					"category": {
						"id": cat_id,
						"name": getattr(getattr(product, "category", None), "name", None),
						"fetch": lambda: CategoryService().get_all_categories(),
						"id_attr": "category_id",
						"name_attr": "name",
					},
					"brand": {
						"id": br_id,
						"name": getattr(getattr(product, "brand", None), "name", None),
						"fetch": lambda: BrandService().get_all_brands(),
						"id_attr": "brand_id",
						"name_attr": "name",
					},
				}
				for key, cfg in mapping.items():
					if cfg["id"] in (None, "") and cfg.get("name"):
						for item in cfg["fetch"]():
							if getattr(item, cfg["name_attr"], "") == cfg["name"]:
								cfg["id"] = getattr(item, cfg["id_attr"], None)
								break
				cat_id = mapping["category"]["id"]
				br_id = mapping["brand"]["id"]
				cat_name = mapping["category"].get("name")
				br_name = mapping["brand"].get("name")
				if not cat_name and cat_id not in (None, ""):
					for c in CategoryService().get_all_categories():
						if getattr(c, "category_id", None) == cat_id:
							cat_name = getattr(c, "name", None)
							break
				if not br_name and br_id not in (None, ""):
					for b in BrandService().get_all_brands():
						if getattr(b, "brand_id", None) == br_id:
							br_name = getattr(b, "name", None)
							break
				self.form_data = {
					"name": getattr(product, "name", ""),
					"description": getattr(product, "description", ""),
					"stock": getattr(product, "stock", 0),
					"price": getattr(product, "price", 0),
					"sku": getattr(product, "sku", "") or "",
					"is_available": "Disponible" if getattr(product, "is_available", True) else "No disponible",
					"category_id": cat_id,
					"brand_id": br_id,
					"category_name": cat_name or "",
					"brand_name": br_name or "",
				}
		except Exception as e:
			log.error(f"No se pudo cargar el producto {product_id}: {e}")
			ft.AlertDialog(title=ft.Text(f"No se pudo cargar el producto {product_id}: {e}"))

	def on_submit(self, form_data: dict):
		is_valid, errors = self.validators.validate_edit_product_form_data(form_data)
		if not is_valid:
			log.error(f"Error al validar el formulario: {errors}")
			return
		try:
			is_available_val = form_data.get("is_available")
			is_available_bool = True if str(is_available_val).lower().startswith("disponible") else False

			category_val = form_data.get("category") or form_data.get("category_id")
			brand_val = form_data.get("brand") or form_data.get("brand_id")

			category_dto = None
			brand_dto = None
			try:
				if category_val not in (None, ""):
					category_dto = CategoryDTO(category_id=int(category_val), name="")
			except Exception:
				category_dto = None
			try:
				if brand_val not in (None, ""):
					brand_dto = BrandDTO(brand_id=int(brand_val), name="")
			except Exception:
				brand_dto = None

			product_dto = ProductDTO(
				self.product_id,
				name=form_data['name'],
				description=form_data['description'],
				stock=int(form_data['stock']),
				price=int(form_data['price']),
				sku=form_data['sku'],
				is_available=is_available_bool,
				category=category_dto,
				brand=brand_dto
			)
			product_edited = self.product_service.update_product(product_dto)
			log.info(f"Producto editado: {product_edited}")
			ft.AlertDialog(title=ft.Text(value=f"Producto editado: {product_edited}"))
			if product_edited:
				page = getattr(self.product_form, "page", None)
				def go_main_action():
					if page is not None:
						return page.go("/")
					return None
				actions = {
					"use_callback": (self.on_saved is not None, self.on_saved),
					"go_main": (page is not None, go_main_action),
				}
				for key in ("use_callback", "go_main"):
					cond, action = actions[key]
					if cond:
						action()
						break
			return product_edited
		except Exception as e:
			ft.AlertDialog(title=ft.Text(value=f"Ha ocurrido un error {e}"))
			return log.error(f"Ha ocurrido un error {e}")

	def create_form_layout(self) -> ft.Container:
		form_controls = self.product_form.create_controls(self.form_data)
		form_column = ft.Column(
			form_controls,
			scroll=ft.ScrollMode.ALWAYS,
			expand=True,
		)
		main_content = ft.Row([
			ft.Container(
				content=form_column,
				width=300,
				padding=ft.Padding(20, 20, 20, 20),
				border_radius=10,
				expand=True,
			)
		], alignment=ft.MainAxisAlignment.START, expand=True)
		return ft.Container(
			content=main_content,
			padding=ft.Padding(20, 20, 20, 20),
			expand=True,
		)