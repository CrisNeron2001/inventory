from core.abstracts.form import Form
from typing import Callable
import flet as ft

class ConfirmationStep(Form):
    def __init__(self, on_submit: Callable):
        super().__init__("Confirmación", "confirmation")
        self.on_submit = on_submit
        self.form_data: dict = {}
        
    def create_controls(self, form_data: dict) -> list[ft.Control]:
        self.form_data = form_data
        summary = [
			self.summary_item("Nombre producto", form_data.get('name', 'N/A')),
			self.summary_item("Descripción", form_data.get('description', 'N/A')),
			self.summary_item("Stock", str(form_data.get('quantity', '0'))),
			self.summary_item("Precio", f"${form_data.get('price', '0')}"),
			self.summary_item("Código", form_data.get('sku', 'N/A')),
			self.summary_item("Disponibilidad stock", "Disponible" if form_data.get('is_available') else "No disponible"),
			self.summary_item("Categoría", str(form_data.get('category', 'N/A'))),
			self.summary_item("Marca", str(form_data.get('brand', 'N/A')))
		]
        
        return [
			ft.Text(self.title, size=18, weight=ft.FontWeight.BOLD),
			ft.Divider(height=20),
			ft.Text("Revise los datos antes de crear", size=14),
			ft.Container(
				content=ft.Column(summary),
				padding=ft.Padding(20, 20, 20, 20),
				margin=ft.Margin(0, 20, 0, 20),
				border_radius=10,
				border=ft.border.all(1, ft.Colors.OUTLINE),
			),	
		]
        
    def summary_item(self, label: str, value: str) -> ft.Container:
        return ft.Container(
			content=ft.Row(
				[
					ft.Text(f"{label}:", weight=ft.FontWeight.W_500, expand=1),
					ft.Text(value=value, expand=2)
				]),
			padding=ft.Padding(0, 5, 0, 5)
		)
        
    def get_data(self) -> dict:
        return self.form_data
    
    def validate(self) -> tuple[bool, list[str]]:
        return True, []
    
    def reset(self) -> None:
        pass