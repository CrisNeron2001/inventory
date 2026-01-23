from core.abstracts.form import Form
from typing import Optional, cast
from utils.helpers import increment_field, decrement_field
import flet as ft

class CashPaymentStep(Form):
    def __init__(self):
        super().__init__("Pago en efectivo", "cash_payment")
        self.amount_field: Optional[ft.TextField] = None
        self.amount_row: Optional[ft.Row] = None

    def create_controls(self, form_data: dict) -> list[ft.Control]:
        total = form_data.get('total', 0)
        self.amount_field = ft.TextField(value=str(total), label="Monto recibido", keyboard_type=ft.KeyboardType.NUMBER)
        self.amount_row = ft.Row(
			controls=[
				self.amount_field,
				ft.IconButton(
					icon=ft.Icons.ARROW_DROP_UP,
					on_click=lambda e: increment_field(cast(ft.TextField, self.amount_field), 1)
				),
				ft.IconButton(
					icon=ft.Icons.ARROW_DROP_DOWN,
					on_click=lambda e: decrement_field(cast(ft.TextField, self.amount_field), 1)
				),
			],
			vertical_alignment=ft.CrossAxisAlignment.END
		)
        return [ft.Text(self.title, size=18), ft.Text(f"Total: ${total}"), self.amount_row]

    def get_data(self) -> dict:
        try:
            if self.amount_field is not None and self.amount_field.value is not None:
                amount = int(str(self.amount_field.value).strip() or "1")
            else:
                amount = 1
        except Exception:
            amount = 1
        return {"amount": amount}

    def validate(self) -> tuple[bool, list[str]]:
        d = self.get_data()
        errors = []
        if d.get('amount', 0) <= 0:
            errors.append("Monto inválido")
        return (len(errors) == 0, errors)

    def reset(self) -> None:
        self.amount_field = None
