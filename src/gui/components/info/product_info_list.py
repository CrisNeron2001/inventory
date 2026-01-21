from core.abstracts.info import Info
from typing import Any, Sequence
from dataclasses import is_dataclass, asdict
import flet as ft

class ProductInfoList(Info):
	def __init__(self):
		super().__init__("Información del producto", "product_info_list")
		self.products_data: Sequence[dict] = []
		
	def create_controls(self, info_data: Any) -> list[ft.Control]:
		if is_dataclass(info_data) and not isinstance(info_data, type):
			self.products_data = [asdict(info_data)]
		elif isinstance(info_data, dict):
			self.products_data = [info_data]
		elif isinstance(info_data, Sequence):
			self.products_data = []
			for p in info_data:
				if is_dataclass(p) and not isinstance(p, type):
					self.products_data.append(asdict(p))
				elif isinstance(p, dict):
					self.products_data.append(p)
		else:
			self.products_data = []

		info_products: list[ft.Control] = []
		for product in self.products_data:
			info_product = self.create_product_info_list(product)
			info_products.append(info_product)

		return info_products
	
	def create_product_info_list(self, data: dict) -> ft.Control:
		availability_text = "Disponible" if data.get("is_available", True) else "No disponible"
		price_formatted = f"${data.get('price', 0)}"

		category = data.get("category")
		if isinstance(category, dict):
			category = category.get("name")
		brand = data.get("brand")
		if isinstance(brand, dict):
			brand = brand.get("name")

		return ft.Container(
			content=ft.Column([
				ft.ListTile(title=ft.Text(value=f"Producto: {data.get('name', 'N/A')}")),
				ft.ListTile(title=ft.Text(value=f"Descripción {data.get('description', 'N/A')}")),
				ft.ListTile(title=ft.Text(value=f"Stock: {str(data.get('stock', '0'))}")),
				ft.ListTile(title=ft.Text(value=f"Precio: {price_formatted}")),
				ft.ListTile(title=ft.Text(value=f"Código: {data.get('sku', 'N/A')}")),
				ft.ListTile(title=ft.Text(value=f"Estado disponibilidad: {availability_text}")),
				ft.ListTile(title=ft.Text(value=f"Categoria: {category or 'N/A'}")),
				ft.ListTile(title=ft.Text(value=f"Marca: {brand or 'N/A'}")),
			])
		)

	def get_data(self) -> dict[str, Any]:
		return {'products': self.products_data}