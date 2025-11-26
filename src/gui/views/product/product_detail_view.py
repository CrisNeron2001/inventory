import flet as ft
from services.product_service import ProductService
from gui.components.info.product_info_list import ProductInfoList
from dataclasses import is_dataclass, asdict


def product_detail_view(product_id: int) -> ft.Container:
    svc = ProductService()
    product = svc.get_product_by_id(product_id)
    info = ProductInfoList()
    payload = {}
    if product is None:
        payload = {}
    elif is_dataclass(product):
        payload = asdict(product)
    elif isinstance(product, dict):
        payload = product
    else:
        field_names = [
			"product_id", "name", "description", "price",
			"stock", "sku", "is_available", "category_name",
			"brand_name", "notes"
		]
        try:
            payload = {k: getattr(product, k) for k in field_names if hasattr(product, k)}
        except Exception:
            payload = {}

    detail = info.create_controls(info_data=payload)
    return ft.Container(content=ft.Column(detail), expand=True)