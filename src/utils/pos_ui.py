import flet as ft
from typing import List
from gui.components.steps.step_navigation import StepNavigator
from gui.components.steps.sale.product_selection_step import ProductSelectionStep
from gui.components.steps.sale.sale_summary_step import SaleSummaryStep
from gui.components.steps.sale.cash_payment_step import CashPaymentStep


class POSUI:
    def __init__(self, controller):
        self.controller = controller

    def create_form_layout(self) -> ft.Container:
        return self.controller._create_form_layout_internal()

    def create_steps_layout(self) -> ft.Container:
        return self.controller._create_steps_layout_internal()

    def update_step_indicators(self) -> None:
        return self.controller._update_step_indicators_internal()

    def update_content(self) -> None:
        return self.controller._update_content_internal()

    def update_progress(self) -> None:
        return self.controller._update_progress_internal()
