import flet as ft
from gui.controllers.product.edit_product_stock_form_controller import EditProductStockTableController

def edit_product_stock_view() -> ft.Container:
    controller = EditProductStockTableController()
    layout = controller.create_layout()
    return ft.Container(
        content=ft.Column([
            ft.Text("Editar Stock y Disponibilidad de Productos", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
            ft.Divider(),
            layout,
        ]),
        padding=ft.Padding(20, 16, 20, 16),
        expand=True,
    )
