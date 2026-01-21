import flet as ft
from typing import Callable, Optional

def error_dialog(page: ft.Page, error: str, on_close: Optional[Callable[[], None] | None] = None) -> None:
	def dismiss_dialog(_: ft.ControlEvent):
		alert_dialog.open = False
		page.update()
		if on_close:
			on_close()

	alert_dialog = ft.CupertinoAlertDialog(
		title=ft.Text("Ocurrió un error"),
		content=ft.Text(f"Error detectado: {error}"),
		actions=[
			ft.CupertinoDialogAction(text="Cerrar", on_click=dismiss_dialog),
		],
	)
	
	page.overlay.append(alert_dialog)
	alert_dialog.open = True
	page.update()