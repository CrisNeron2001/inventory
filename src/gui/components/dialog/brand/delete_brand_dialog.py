import flet as ft
from typing import Optional, Callable
from services.brand_service import BrandService

def delete_brand_dialog(page: ft.Page, brand_id: int, on_deleted: Optional[Callable[[], None]] = None) -> None:
    brand_svc = BrandService()
    brand = brand_svc.get_brand_by_id(brand_id)
    brand_name = getattr(brand, "name", f"#{brand_id}")

    def delete_action(_: ft.ControlEvent):
        brand_svc.delete_brand(brand_id)
        alert_dialog.open = False
        page.update()
        if on_deleted:
            on_deleted()
        
    def dismiss_dialog(_: ft.ControlEvent):
        alert_dialog.open = False
        page.update()
        
    alert_dialog = ft.CupertinoAlertDialog(
		title=ft.Text("Eliminar marca"),
		content=ft.Text(f"¿Estás seguro que deseas eliminar esta marca?\n{brand_name}"),
		actions=[
			ft.CupertinoDialogAction(text="Sí", is_destructive_action=True, on_click=delete_action),
			ft.CupertinoDialogAction(text="No", on_click=dismiss_dialog),
		],
	)
    page.overlay.append(alert_dialog)
    alert_dialog.open = True
    page.update()
