import flet as ft
from typing import Optional, Callable
from gui.controllers.user.edit_user_form_controller import EditUserFormController


def edit_user_view(user_id: int, on_saved: Optional[Callable[[], None]] = None) -> ft.Container:
    controller = EditUserFormController(user_id=user_id, router_callback=(lambda r: on_saved() if on_saved else None))
    return controller.create_form_layout()
