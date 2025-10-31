import flet as ft
from typing import Optional, Callable
from gui.controllers.product.edit_product_form_controller import EditProductFormController


def edit_product_view(product_id: int, on_saved: Optional[Callable[[], None]] = None) -> ft.Container:
    controller = EditProductFormController(product_id, on_saved=on_saved)
    layout = controller.create_form_layout()


    return ft.Container(
        content=ft.Column([
            ft.Divider(),
            layout,
        ]),
        padding=ft.Padding(20, 16, 20, 16),
        expand=True,
    )
