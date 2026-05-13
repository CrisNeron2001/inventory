from typing import Callable, Optional
from core.abstracts.button import Button
import flet as ft


class ProductCreateButton(Button):
    def __init__(self, to_create: Callable):
        super().__init__("Botón de crear producto", "create_button")
        self.button_create: Optional[ft.ElevatedButton] = None
        self.to_create = to_create

    def create_controls(self) -> list[ft.Control]:
        self.button_create = ft.ElevatedButton(
            text="Crear nuevo producto",
            on_click=lambda _: self.to_create(),
            width=200,
            height=50,
        )

        return [
            ft.Column(
                controls=[self.button_create],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            )
        ]
