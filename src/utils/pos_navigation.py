from typing import Optional
import flet as ft


class POSNavigationHelper:
    def __init__(self, controller):
        self.controller = controller

    def next_step(self, e: Optional[ft.ControlEvent] = None):
        return self.controller._next_step_internal(e)

    def prev_step(self, e: Optional[ft.ControlEvent] = None):
        return self.controller._prev_step_internal(e)

    def _update_nav_buttons(self) -> None:
        return self.controller._update_nav_buttons_internal()
