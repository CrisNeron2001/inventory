from core.abstracts.info import Info
from typing import Any, Sequence
import flet as ft

class ProductInfoList(Info):
	def __init__(self):
		super().__init__("Información del producto", "product_info_list")
		self.products_data: Sequence[dict] = []
		
	def create_controls(self, info_data: Any) -> list[ft.Control]:
		if isinstance(info_data, dict):
			self.products_data = [info_data]
		elif isinstance(info_data, Sequence):
			self.products_data = [p for p in info_data if isinstance(p, dict)]
		else:
			self.products_data = []
			
		info_products = []
		for product in self.products_data:
			data = product
			info_product = self.create_product_info_list(data)
			info_products.append(info_product)
			
		return info_products
	
	def create_product_info_list(self, data: dict) -> ft.Control:
		availability_text = "Disponible" if data.get("is_available", True) else "No disponible"
		price_formatted = f"${data.get('price', 0)}"
		
		return ft.Container(
			content=ft.Column([
				ft.ListTile(title=ft.Text(value=f"Producto: {data.get('name', 'N/A')}")),
				ft.ListTile(title=ft.Text(value=f"Descripción {data.get('description', 'N/A')}")),
				ft.ListTile(title=ft.Text(value=f"Stock: {str(data.get('stock', '0'))}")),
				ft.ListTile(title=ft.Text(value=f"Precio: {price_formatted}")),
				ft.ListTile(title=ft.Text(value=f"Código: {data.get('sku', 'N/A')}")),
				ft.ListTile(title=ft.Text(value=f"Estado disponibilidad: {availability_text}")),
				ft.ListTile(title=ft.Text(value=f"Categoria: {data.get('category', 'N/A')}")),
				ft.ListTile(title=ft.Text(value=f"Marca: {data.get('brand', 'N/A')}"))
			])
		)

	def get_data(self) -> dict[str, Any]:
		return {'products': self.products_data}