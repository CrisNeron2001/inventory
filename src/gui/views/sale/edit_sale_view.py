import flet as ft
from gui.controllers.sale.edit_sale_form_controller import EditSaleFormController

def edit_sale_view(sale_id: int, page: ft.Page) -> ft.Container:
    controller = EditSaleFormController(sale_id=sale_id, page=page)
    return controller.create_form_layout()
