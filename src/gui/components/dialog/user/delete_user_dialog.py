import flet as ft
from typing import Optional, Callable
from services.user_service import UserService


def delete_user_dialog(page: ft.Page, user_id: int, on_deleted: Optional[Callable[[], None]] = None) -> None:
    user_svc = UserService()
    user = user_svc.get_user_by_id(user_id)
    username = getattr(user, "username", f"#{user_id}")

    def delete_action(_: ft.ControlEvent):
        user_svc.delete_user(user_id)
        alert_dialog.open = False
        page.update()
        if on_deleted:
            on_deleted()

    def dismiss_dialog(_: ft.ControlEvent):
        alert_dialog.open = False
        page.update()

    alert_dialog = ft.CupertinoAlertDialog(
        title=ft.Text("Eliminar usuario"),
        content=ft.Text(f"¿Estás seguro que deseas eliminar este usuario?\n{username}"),
        actions=[
            ft.CupertinoDialogAction(text="Sí", is_destructive_action=True, on_click=delete_action),
            ft.CupertinoDialogAction(text="No", on_click=dismiss_dialog),
        ],
    )

    page.overlay.append(alert_dialog)
    alert_dialog.open = True
    page.update()
