import flet as ft


def sku_conflict_dialog(page: ft.Page, sku: str) -> None:
    msg = f"Ya existe un producto con el código: {sku}." \
          "\nPor favor ingrese un código (SKU) diferente."

    def dismiss_dialog(e: ft.ControlEvent):
        alert_dialog.open = False
        page.update()

    alert_dialog = ft.CupertinoAlertDialog(
        title=ft.Text("SKU duplicado"),
        content=ft.Text(msg),
        actions=[
            ft.CupertinoDialogAction(text="Cerrar", on_click=dismiss_dialog),
        ],
    )

    page.overlay.append(alert_dialog)
    alert_dialog.open = True
    page.update()
