from core.abstracts.form import Form
from gui.validators.product_form_validator import FormProductValidator
from utils.constants import ALLOWED_FIELD
from typing import Optional
import flet as ft

class BasicDataStep(Form):
    def __init__(self):
        super().__init__("Datos básicos", "basic_data")
        self.field_name: Optional[ft.TextField] = None
        self.field_desc: Optional[ft.TextField] = None 
        self.field_stock: Optional[ft.TextField] = None
        self.field_price: Optional[ft.TextField] = None
        self.field_sku: Optional[ft.TextField] = None

    def create_controls(self, form_data: dict) -> list[ft.Control]:            
        self.field_name = ft.TextField(
			label="Nombre producto", 
			hint_text="Ingrese el nombre del producto",
			value=form_data.get('name', 'N/A')
		)
        self.field_desc = ft.TextField(
			label="Descripción",
			hint_text="Ingrese descripción",
			value=form_data.get('description', 'N/A')
		)
        self.field_stock = ft.TextField(
			label="Stock",
			hint_text="Ingrese la stock",
			keyboard_type=ft.KeyboardType.NUMBER,
			input_filter=ft.InputFilter(allow=True, regex_string=r"^\d*\.?\d*$"),
			value=str(form_data.get('stock', 0))
		)
        self.field_price = ft.TextField(
			label="Precio",
			hint_text="Ingrese el precio",
			keyboard_type=ft.KeyboardType.NUMBER,
			input_filter=ft.InputFilter(allow=True, regex_string=r"^\d*\.?\d*$"),
			value=str(form_data.get('price', 0))
		)
        self.field_sku = ft.TextField(
			label="Código",
			hint_text="Ingrese el código",
			value=form_data.get('sku', 'N/A')
		)
        return [
            ft.Text(self.title, size=18),
			self.field_name,
			self.field_desc,
			self.field_stock,
			self.field_price,
			self.field_sku
		] 

    def get_data(self) -> dict:
        return {
			'name': self.field_name.value if self.field_name is not None else '',
			'description': self.field_desc.value if self.field_desc is not None else '',
			'stock': self.field_stock.value if self.field_stock is not None else '0',
			'price': self.field_price.value if self.field_price is not None else '0',
			'sku': self.field_sku.value if self.field_sku is not None else ''
		}

    def validate(self) -> tuple[bool, list[str]]:
        data = self.get_data()
        return FormProductValidator.validate_step_product_form_data("basic_data", data)

    def reset(self) -> None:
        for field in ALLOWED_FIELD['field_basic_data']:
            setattr(self, field, None)