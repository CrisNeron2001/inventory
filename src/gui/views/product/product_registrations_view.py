import flet as ft
from typing import Callable, Optional
from services.product_service import ProductService
from gui.components.info.product_info_table import ProductInfoTable


def product_registrations_view(router_callback: Optional[Callable[[str], None]] = None) -> ft.Container:
    svc = ProductService()
    products = svc.get_all_products()
    table = ProductInfoTable(router_callback)
    controls = table.create_controls(products)
    return ft.Container(content=ft.Column(controls), expand=True)
