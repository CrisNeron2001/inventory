import flet as ft
from gui.components.button.product.product_create_button import ProductCreateButton
from gui.components.button.product.product_import_button import ProductImportButton


class MenuProductController:
    def __init__(self, page: ft.Page):
        self.page = page
        self.create_button = ProductCreateButton(self.to_create_product)
        self.import_button = ProductImportButton(self.page)

    def to_create_product(self, e=None):
        return self.page.go("/products/create/manual")

    def button_import_product(self) -> ft.ElevatedButton:
        return ft.ElevatedButton(
            text="Importar desde Excel",
            icon=ft.Icons.FILE_UPLOAD,
            on_click=lambda _: self.import_button.on_import(),
            width=200,
            height=50,
        )

    def button_create_product(self) -> ft.ElevatedButton:
        return ft.ElevatedButton(
            text="Crear nuevo producto",
            icon=ft.Icons.ADD,
            on_click=self.to_create_product,
            width=200,
            height=50,
        )

    def create_layout(self) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [self.button_create_product()],
                        expand=True,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1),
                    ft.Row(
                        [self.button_import_product()],
                        expand=True,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            ),
            expand=True,
        )
