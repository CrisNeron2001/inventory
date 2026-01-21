from core.abstracts.form import Form
from gui.validators.name_field_validator import NameFieldValidator
from typing import Any, Callable, Optional
import flet as ft

class CategoryForm(Form):
    def __init__(self, on_submit: Callable) -> None:
        super().__init__("Formulario de categoria", "category_form")
        self.field_name: Optional[ft.TextField] = None
        self.validator = NameFieldValidator()
        self.on_submit = on_submit
        self.form_data: dict = {}
        
    def create_controls(self, form_data: dict) -> list[ft.Control]:
        self.field_name = ft.TextField(
            label="Nombre de la categoria", 
            hint_text="Ingrese el nombre de la categoria",
            value=form_data.get('name', '')
        )
        button_submit = ft.ElevatedButton(
            text="Ingresar", 
            style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.LIGHT_GREEN_600), # type: ignore
            on_click=lambda e: self.on_submit(self.get_data())
        )
        return [
            ft.Text(self.title, size=18),
			self.field_name,
						ft.Container(
				content=button_submit,
				alignment=ft.Alignment(0, 0),
				margin=ft.Margin(0, 20, 0, 0)
			)
		]
        
    def get_data(self) -> dict[Any, str]:
        return {
            'name': getattr(self.field_name, 'value', '') or ''
        }
        
    def validate(self) -> tuple[bool, list[str]]:
        data = self.get_data()
        return self.validator.validate_name_field(data)
    
    def reset(self) -> None:
        pass