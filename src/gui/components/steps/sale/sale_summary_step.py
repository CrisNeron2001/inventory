from core.abstracts.form import Form
from typing import Optional, Callable
import flet as ft
from config.settings import log

class SaleSummaryStep(Form):
    def __init__(self, router_callback: Optional[Callable[[str], None]] = None):
        super().__init__("Resumen de venta", "sale_summary")
        self.table: Optional[ft.DataTable] = None
        self.router_callback = router_callback

    def create_controls(self, form_data: dict) -> list[ft.Control]:
        cart = form_data.get("cart", [])

        rows: list[ft.DataRow] = []
        for it in cart:
            prod = it.get("product")
            name = getattr(prod, 'name', 'N/A')
            qty = it.get('qty', 0)
            lt = it.get('line_total', 0)

            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(name)),
                ft.DataCell(ft.Text(str(qty))),
                ft.DataCell(ft.Text(str(lt))),
            ]))

        self.table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Producto")),
                ft.DataColumn(ft.Text("Cantidad")),
                ft.DataColumn(ft.Text("Total")),
            ],
            rows=rows,
        )

        total = sum(it.get('line_total', 0) for it in cart)
        total_lbl = ft.Text(f"Total a pagar: ${total}", size=16, weight=ft.FontWeight.BOLD)

        return [ft.Text(self.title, size=18), self.table, ft.Divider(), total_lbl]

    def get_data(self) -> dict:
        return {}

    def validate(self) -> tuple[bool, list[str]]:
        return (True, [])

    def reset(self) -> None:
        self.table = None