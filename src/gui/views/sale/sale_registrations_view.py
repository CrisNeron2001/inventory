import flet as ft
from typing import Callable, Optional
from services.sale_service import SaleService
from gui.components.info.sale_info_table import SaleInfoTable


def sale_registrations_view(router_callback: Optional[Callable[[str], None]] = None) -> ft.Container:
    svc = SaleService()
    sales = svc.get_all_sales()
    table = SaleInfoTable(router_callback)
    controls = table.create_controls(sales)
    return ft.Container(content=ft.Column(controls), expand=True)
