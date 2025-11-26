import flet as ft
from typing import Callable, Optional
from gui.controllers.sale.edit_sale_form_controller import EditSaleFormController


def edit_sale_view(sale_id: int, on_saved: Optional[Callable[[], None]] = None) -> ft.Container:
    controller = EditSaleFormController(sale_id, on_saved=on_saved)
    return controller.create_form_layout()
