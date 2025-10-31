import flet as ft
from typing import Callable, Optional
from services.category_service import CategoryService
from gui.components.info.category_info_table import CategoryInfoTable


def category_registrations_view(router_callback: Optional[Callable[[str], None]] = None) -> ft.Container:
    svc = CategoryService()
    categories = svc.get_all_categories()
    table = CategoryInfoTable(router_callback)
    controls = table.create_controls(categories)
    return ft.Container(content=ft.Column(controls), expand=True)
