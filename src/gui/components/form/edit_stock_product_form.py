import flet as ft
from core.abstracts.form import Form
from gui.validators.product_form_validator import FormProductValidator
from typing import Callable, Optional, cast
from utils.helpers import increment_field, decrement_field


class EditStockProductForm(Form):
    def __init__(self, on_submit: Callable) -> None:
        super().__init__("Editar Disponibilidad Producto", "edit_product_stock")
        self.field_name: Optional[ft.TextField] = None
        self.field_stock: Optional[ft.TextField] = None
        self.validator = FormProductValidator()
        self.on_submit = on_submit
        self.form_data: dict = {}
        self.stock_row: Optional[ft.Row] = None

    def create_controls(self, form_data: dict) -> list[ft.Control]:
        self.field_name = ft.TextField(
            label="Nombre producto",
            hint_text="Ingrese el nombre del producto",
            value=form_data.get("name", ""),
            label_style=ft.TextStyle(size=20, height=5, weight=ft.FontWeight.NORMAL),
            border=ft.InputBorder.UNDERLINE,
            border_color=ft.Colors.WHITE,
        )
        self.field_stock = ft.TextField(
            label="Stock",
            hint_text="Ingrese la stock",
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=ft.InputFilter(allow=True, regex_string=r"^\d*\.?\d*$"),
            value=str(form_data.get("stock", "")),
            label_style=ft.TextStyle(size=20, height=5, weight=ft.FontWeight.NORMAL),
            border=ft.InputBorder.UNDERLINE,
            border_color=ft.Colors.WHITE,
        )

        self.stock_row = ft.Row(
            controls=[
                self.field_stock,
                ft.IconButton(
                    icon=ft.Icons.ARROW_DROP_UP,
                    on_click=lambda e: increment_field(
                        cast(ft.TextField, self.field_stock), 1
                    ),
                ),
                ft.IconButton(
                    icon=ft.Icons.ARROW_DROP_DOWN,
                    on_click=lambda e: decrement_field(
                        cast(ft.TextField, self.field_stock), 1
                    ),
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.END,
        )

        button_submit = ft.ElevatedButton(
            text="Guardar cambios",
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE, bgcolor=ft.Colors.LIGHT_GREEN_600
            ),
            on_click=lambda e: self.on_submit(self.get_data()),
        )

        return [
            ft.Row(
                [
                    ft.Container(
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        self.field_name,
                                        self.stock_row,
                                        button_submit,
                                    ],
                                    spacing=20,
                                ),
                            ],
                            spacing=40,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        margin=20,
                    ),
                ]
            ),
        ]

    def get_data(self) -> dict:
        return {
            "name": self.field_name.value if self.field_name is not None else "",
            "stock": self.field_stock.value if self.field_stock is not None else "1",
        }

    def validate(self) -> tuple[bool, list[str]]:
        data = self.get_data()
        return self.validator.validate_edit_product_stock_form_data(data)

    def reset(self) -> None:
        pass

