from core.abstracts.info import Info
from typing import Any, Sequence
import flet as ft
import datetime

class SaleInfoList(Info):
	def __init__(self):
		super().__init__("Información de la venta", "sale_info_list")
		self.sales_data: Sequence[dict] = []
		
	def create_controls(self, info_data: Any) -> list[ft.Control]:
		if isinstance(info_data, dict):
			self.sales_data = [info_data]
		elif isinstance(info_data, Sequence):
			self.sales_data = [p for p in info_data if isinstance(p, dict)]
		else:
			self.sales_data = []
			
		info_sales = []
		for sale in self.sales_data:
			data = sale
			info_sale = self.create_sale_info_list(data)
			info_sales.append(info_sale)
			
		return info_sales
	
	def create_sale_info_list(self, data: dict) -> ft.Control:
		unit_price_formatted = f"${data.get('unit_price', 0)}"
		total_price_formatted = f"${data.get('total_price', 0)}"
		sale_date = data.get('sale_date')
		sale_date_formatted = "N/A"

		if isinstance(sale_date, (datetime.date, datetime.datetime)):
			sale_date_formatted = sale_date.strftime("%d-%m-%Y")
		elif isinstance(sale_date, str):
			s = sale_date.strip()
			try:
				d = datetime.date.fromisoformat(s)
				sale_date_formatted = d.strftime("%d-%m-%Y")
			except Exception:
				try:
					dt = datetime.datetime.fromisoformat(s)
					sale_date_formatted = dt.strftime("%d-%m-%Y")
				except Exception:
					for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y", "%Y/%m/%d"):
						dt = datetime.datetime.strptime(s, fmt)
						sale_date_formatted = dt.strftime("%d-%m-%Y")
						break
		
		return ft.Container(
			content=ft.Column([
				ft.ListTile(title=ft.Text(value=f"Producto: {data.get('product_name', 'N/A')}")),
				ft.ListTile(title=ft.Text(value=f"Cantidad: {str(data.get('quantity', '0'))}")),
				ft.ListTile(title=ft.Text(value=f"Precio unit.: {unit_price_formatted}")),
				ft.ListTile(title=ft.Text(value=f"Precio total: {total_price_formatted}")),
				ft.ListTile(title=ft.Text(value=f"Fecha: {sale_date_formatted}")),
			])
		)

	def get_data(self) -> dict[str, Any]:
		return {'sales': self.sales_data}