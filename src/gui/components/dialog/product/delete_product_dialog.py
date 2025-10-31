import flet as ft
from typing import Optional, Callable
from services.product_service import ProductService

def delete_product_dialog(page: ft.Page, product_id: int, on_deleted: Optional[Callable[[], None]] = None) -> None:
    product_svc = ProductService()
    product = product_svc.get_product_by_id(product_id)
    product_name = getattr(product, "name", f"#{product_id}")
    
    def delete_action(_: ft.ControlEvent):
        product_svc.delete_product(product_id)
        alert_dialog.open = False
        page.update()
        if on_deleted:
            on_deleted()
            
    def dismiss_dialog(_: ft.ControlEvent):
        alert_dialog.open = False
        page.update()
        
    alert_dialog = ft.CupertinoAlertDialog(
		title=ft.Text("Eliminar producto"),
		content=ft.Text(f"¿Estás seguro que deseas eliminar este producto?\n{product_name}"),
		actions=[
			ft.CupertinoDialogAction(text="Sí", is_destructive_action=True, on_click=delete_action),
			ft.CupertinoDialogAction(text="No", on_click=dismiss_dialog),
		],
	)
    
    page.overlay.append(alert_dialog)
    alert_dialog.open = True
    page.update()