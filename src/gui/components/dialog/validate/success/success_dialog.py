import flet as ft
from typing import Callable

def success_dialog(page: ft.Page, msg: str, on_close: Callable[[], None] | None = None) -> None:

	def dismiss_dialog(e: ft.ControlEvent):
		alert_dialog.open = False
		page.update()
		if on_close:
			on_close()

	alert_dialog = ft.CupertinoAlertDialog(
		title=ft.Text(f"{msg}"),
		actions=[
			ft.CupertinoDialogAction(text="Cerrar", on_click=dismiss_dialog),
		],
	)

	page.overlay.append(alert_dialog)
	alert_dialog.open = True
	page.update()