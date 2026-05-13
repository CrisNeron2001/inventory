import flet as ft
from core.abstracts.button import Button
from typing import Optional
from gui.components.dialog.product.product_import_dialog import product_import_dialog
from gui.components.dialog.validate.error.error_dialog import error_dialog


class ProductImportButton(Button):
    def __init__(self, page: ft.Page):
        super().__init__("Botón de importar producto", "import_button")
        self.button_import: Optional[ft.ElevatedButton] = None
        self.page = page

    def create_controls(self) -> list[ft.Control]:
        self.button_import = ft.ElevatedButton(
            text="Importar desde Excel",
            on_click=lambda _: self.on_import(),
            width=200,
            height=50,
        )

        return [
            ft.Column(
                controls=[
                    self.button_import,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            )
        ]

    def on_import(self):
        try:
            product_import_dialog(
                self.page,
                on_import_finished=lambda *_: self.page.go("/") if self.page else None,
            )
        except RuntimeError as e:
            error_dialog(
                self.page,
                f"Error al importar {e}",
                lambda: self.page.go("/products/create/") if self.page else None,
            )
