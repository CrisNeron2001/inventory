from core.abstracts.form import Form
from typing import Optional
import flet as ft


class CashPaymentStep(Form):
    def __init__(self):
        super().__init__("Pago en efectivo", "cash_payment")
        self.amount_field: Optional[ft.TextField] = None

    def create_controls(self, form_data: dict) -> list[ft.Control]:
        total = form_data.get('total', 0)
        self.amount_field = ft.TextField(value=str(total), label="Monto recibido", keyboard_type=ft.KeyboardType.NUMBER)
        return [ft.Text(self.title, size=18), ft.Text(f"Total: ${total}"), self.amount_field]

    def get_data(self) -> dict:
        try:
            amount = int(str(self.amount_field.value)) if self.amount_field and self.amount_field.value else 0
        except Exception:
            amount = 0
        return {"amount": amount}

    def validate(self) -> tuple[bool, list[str]]:
        d = self.get_data()
        errors = []
        if d.get('amount', 0) <= 0:
            errors.append("Monto inválido")
        return (len(errors) == 0, errors)

    def reset(self) -> None:
        self.amount_field = None
