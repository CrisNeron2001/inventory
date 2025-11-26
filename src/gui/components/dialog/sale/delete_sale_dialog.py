import flet as ft
from typing import Optional, Callable
from services.sale_service import SaleService

def delete_sale_dialog(page: ft.Page, sale_id: int, on_deleted: Optional[Callable[[], None]] = None) -> None:
	sale_svc = SaleService()
	sale = sale_svc.get_sale_by_id(sale_id)
	sale_name = getattr(sale, "name", f"#{sale_id}")

	def delete_action(_: ft.ControlEvent):
		sale_svc.delete_sale(sale_id)
		alert_dialog.open = False
		page.update()
		if on_deleted:
			on_deleted()

	def dismiss_dialog(_: ft.ControlEvent):
		alert_dialog.open = False
		page.update()

	alert_dialog = ft.CupertinoAlertDialog(
		title=ft.Text("Eliminar venta"),
		content=ft.Text(f"¿Estás seguro que deseas eliminar esta venta?\n{sale_name}"),
		actions=[
			ft.CupertinoDialogAction(text="Sí", is_destructive_action=True, on_click=delete_action),
			ft.CupertinoDialogAction(text="No", on_click=dismiss_dialog),
		],
	)

	page.overlay.append(alert_dialog)
	alert_dialog.open = True
	page.update()