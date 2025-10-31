import flet as ft
from typing import Callable, Optional
from services.brand_service import BrandService
from gui.components.info.brand_info_table import BrandInfoTable


def brand_registrations_view(router_callback: Optional[Callable[[str], None]] = None) -> ft.Container:
    svc = BrandService()
    brands = svc.get_all_brands()
    table = BrandInfoTable(router_callback)
    controls = table.create_controls(brands)
    return ft.Container(content=ft.Column(controls), expand=True)
