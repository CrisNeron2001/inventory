import flet as ft
from typing import Optional, Callable
from services.category_service import CategoryService

def delete_category_dialog(page: ft.Page, category_id: int, on_deleted: Optional[Callable[[], None]] = None) -> None:
	category_svc = CategoryService()
	category = category_svc.get_category_by_id(category_id)
	category_name = getattr(category, "name", f"#{category_id}")

	def delete_action(_: ft.ControlEvent):
		category_svc.delete_category(category_id)
		alert_dialog.open = False
		page.update()
		if on_deleted:
			on_deleted()

	def dismiss_dialog(_: ft.ControlEvent):
		alert_dialog.open = False
		page.update()

	alert_dialog = ft.CupertinoAlertDialog(
		title=ft.Text("Eliminar categoría"),
		content=ft.Text(f"¿Estás seguro que deseas eliminar esta categoría?\n{category_name}"),
		actions=[
			ft.CupertinoDialogAction(text="Sí", is_destructive_action=True, on_click=delete_action),
			ft.CupertinoDialogAction(text="No", on_click=dismiss_dialog),
		],
	)

	page.overlay.append(alert_dialog)
	alert_dialog.open = True
	page.update()