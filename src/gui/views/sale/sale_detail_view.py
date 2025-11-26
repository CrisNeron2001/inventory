import flet as ft
from services.sale_service import SaleService
from gui.components.info.sale_info_list import SaleInfoList
from dataclasses import is_dataclass, asdict


def sale_detail_view(sale_id: int) -> ft.Container:
    svc = SaleService()
    sale = svc.get_sale_by_id(sale_id)
    info = SaleInfoList()
    payload = {}
    if sale is None:
        payload = {}
    elif is_dataclass(sale):
        payload = asdict(sale)
    elif isinstance(sale, dict):
        payload = sale
    else:
        field_names = [
			"sale_id", "cart_id", "product_name",
			"quantity", "unit_price", "total_price", 
			"sale_date", "notes",
		]
        try:
            payload = {k: getattr(sale, k) for k in field_names if hasattr(sale, k)}
        except Exception:
            payload = {}

    detail = info.create_controls(info_data=payload)
    return ft.Container(content=ft.Column(detail), expand=True)