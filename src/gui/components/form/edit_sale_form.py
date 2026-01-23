import flet as ft
from core.abstracts.form import Form
from typing import Callable, Optional, cast
from utils.helpers import increment_field, decrement_field

class EditSaleForm(Form):
    def __init__(self, on_submit: Callable, products_options: Optional[list] = None):
        super().__init__("Editar venta", "edit_sale")
        self.on_submit = on_submit
        self.field_product: Optional[ft.Dropdown] = None
        self.field_quantity: Optional[ft.TextField] = None
        self.field_unit_price: Optional[ft.TextField] = None
        self.field_notes: Optional[ft.TextField] = None
        self.products_options = products_options or []
        self.quantity_row: Optional[ft.Row] = None
        self.unit_price_row: Optional[ft.Row] = None

    def create_controls(self, form_data: dict) -> list[ft.Control]:
        options = self.products_options
        if form_data.get("product_options"):
            options = form_data.get("product_options")

        self.field_product = ft.Dropdown(options=options, label="Producto", width=360, disabled=True)
        if form_data.get("product_id") not in (None, ""):
            self.field_product.value = str(form_data.get("product_id"))

        self.field_quantity = ft.TextField(label="Cantidad", value=str(form_data.get("quantity", 1)), keyboard_type=ft.KeyboardType.NUMBER)
        self.field_unit_price = ft.TextField(label="Precio unit.", value=str(form_data.get("unit_price", 0)), keyboard_type=ft.KeyboardType.NUMBER)
        self.field_notes = ft.TextField(label="Notas", value=form_data.get("notes", ""))
        self.quantity_row = ft.Row(
			controls=[
				self.field_quantity,
				ft.IconButton(
					icon=ft.Icons.ARROW_DROP_UP,
					on_click=lambda e: increment_field(cast(ft.TextField, self.field_quantity), 1)
				),
				ft.IconButton(
					icon=ft.Icons.ARROW_DROP_DOWN,
					on_click=lambda e: decrement_field(cast(ft.TextField, self.field_quantity), 1)
				),
			],
			vertical_alignment=ft.CrossAxisAlignment.END
		)
        self.unit_price_row = ft.Row(
			controls=[
				self.field_unit_price,
				ft.IconButton(
					icon=ft.Icons.ARROW_DROP_UP,
					on_click=lambda e: increment_field(cast(ft.TextField, self.field_unit_price), 1)
				),
				ft.IconButton(
					icon=ft.Icons.ARROW_DROP_DOWN,
					on_click=lambda e: decrement_field(cast(ft.TextField, self.field_unit_price), 1)
				),
			],
			vertical_alignment=ft.CrossAxisAlignment.END
		)

        submit_btn = ft.ElevatedButton(text="Guardar", on_click=lambda e: self.on_submit(self.get_data()))

        return [
            ft.Row([
                ft.Column([self.field_product, self.quantity_row, self.unit_price_row, self.field_notes], spacing=12)
            ]),
            ft.Container(content=submit_btn, alignment=ft.Alignment(0, 0), margin=ft.Margin(0, 20, 0, 0))
        ]

    def get_data(self) -> dict:
        product_id = None
        if self.field_product and self.field_product.value not in (None, ''):
            try:
                product_id = int(self.field_product.value)
            except (TypeError, ValueError):
                product_id = None

        quantity = 0
        if self.field_quantity and self.field_quantity.value is not None:
            try:
                q_str = str(self.field_quantity.value).strip()
                if q_str != '':
                    quantity = int(q_str)
            except (TypeError, ValueError):
                quantity = 0

        unit_price = 0
        if self.unit_price_row and self.unit_price_row is not None:
            try:
                up_str = str(self.unit_price_row).strip()
                if up_str != '':
                    unit_price = int(up_str)
            except (TypeError, ValueError):
                unit_price = 0

        notes = self.field_notes.value if self.field_notes else ''

        return {
            'product_id': product_id,
            'quantity': quantity,
            'unit_price': unit_price,
            'notes': notes,
        }

    def validate(self) -> tuple[bool, list[str]]:
        errors = []
        data = self.get_data()
        if not data.get('product_id'):
            errors.append('Producto es requerido')
        if data.get('quantity', 0) <= 0:
            errors.append('Cantidad debe ser mayor que 0')
        return (len(errors) == 0, errors)

    def reset(self) -> None:
        pass
