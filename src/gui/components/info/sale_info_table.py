from core.abstracts.info import Info
from typing import Sequence, Optional, Any
from dataclasses import is_dataclass, asdict
import flet as ft
from gui.views.sale.sale_detail_view import sale_detail_view
from gui.components.paginator.paginator import Paginator


class SaleInfoTable(Info, Paginator):
    def __init__(self, page):
        Info.__init__(self, "Ventas", "sale_info_table")
        columns = [
            ft.DataColumn(ft.Text("Producto")),
            ft.DataColumn(ft.Text("Cantidad")),
            ft.DataColumn(ft.Text("Precio unit.")),
            ft.DataColumn(ft.Text("Total")),
            ft.DataColumn(ft.Text("Fecha")),
            ft.DataColumn(ft.Text("Acciones")),
        ]
        Paginator.__init__(self, page, columns)
        self.page = page
        self.entity_name = ["sale"]

    def create_controls(self, info_data: Any) -> list[ft.Control]:
        def to_dict(item: Any) -> Optional[dict]:
            if isinstance(item, dict):
                return {
                    "sale_id": item.get("sale_id"),
                    "product_name": item.get("product_name", "N/A"),
                    "quantity": item.get("quantity", 0),
                    "unit_price": item.get("unit_price", 0),
                    "total_price": item.get("total_price", 0),
                    "sale_date": item.get("sale_date"),
                    "notes": item.get("notes", ""),
                }
            if is_dataclass(item) and not isinstance(item, type):
                d = asdict(item)
                return {
                    "sale_id": d.get("sale_id"),
                    "product_name": d.get("product_name", "N/A"),
                    "quantity": d.get("quantity", 0),
                    "unit_price": d.get("unit_price", 0),
                    "total_price": d.get("total_price", 0),
                    "sale_date": d.get("sale_date"),
                    "notes": d.get("notes", ""),
                }
            if hasattr(item, "sale_id"):
                return {
                    "sale_id": getattr(item, "sale_id", None),
                    "product_name": getattr(item, "product_name", "N/A"),
                    "quantity": getattr(item, "quantity", 0),
                    "unit_price": getattr(item, "unit_price", 0),
                    "total_price": getattr(item, "total_price", 0),
                    "sale_date": getattr(item, "sale_date", None),
                    "notes": getattr(item, "notes", ""),
                }
            return None

        if isinstance(info_data, dict):
            d = to_dict(info_data)
            self.seq_data = [d] if d is not None else []
            self.sales_data = self.seq_data
        elif isinstance(info_data, Sequence):
            normalized: list[dict] = []
            for p in info_data:
                d = to_dict(p)
                if d is not None:
                    normalized.append(d)
            self.seq_data = normalized
            self.sales_data = normalized
        else:
            self.seq_data = []
            self.sales_data = []

        rows: list[ft.DataRow] = [
            self.create_data_row(p) for p in self._get_paged_items()
        ]
        return self.create_data_table(rows)

    def create_data_table(self, rows: list[ft.DataRow]) -> list[ft.Control]:
        data_table = ft.DataTable(
            columns=self.columns,
            rows=rows,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=8,
            heading_row_height=50,
            data_row_max_height=60,
        )

        self._table_container = (
            ft.Container(
                content=ft.Column([data_table], scroll=ft.ScrollMode.AUTO, expand=True),
                border_radius=8,
                padding=ft.Padding(10, 10, 10, 10),
                height=self._table_height,
            )
            if len(rows) > 0
            else self.create_empty_state()
        )

        self._pager_label = ft.Text(
            self._pager_text(), size=12, color=ft.Colors.GREY_600
        )
        self._page_size_dd = ft.Dropdown(
            value=str(self.page_size),
            options=[ft.DropdownOption(key=str(v)) for v in [5, 10, 20, 50]],
            width=90,
            on_change=self._on_page_size_change,
            label="Por página",
        )
        self._btn_prev = ft.IconButton(
            icon=ft.Icons.CHEVRON_LEFT,
            tooltip="Anterior",
            on_click=self._on_prev,
            disabled=(self.current_page <= 1),
        )
        self._btn_next = ft.IconButton(
            icon=ft.Icons.CHEVRON_RIGHT,
            tooltip="Siguiente",
            on_click=self._on_next,
            disabled=(self.current_page >= self._total_pages()),
        )

        pager = ft.Row(
            [
                self._btn_prev,
                self._btn_next,
                ft.VerticalDivider(width=1),
                self._pager_label,
                ft.Container(expand=True),
                self._page_size_dd,
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        return [
            ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(self.title, size=24, weight=ft.FontWeight.BOLD),
                                ft.Text(
                                    f"({len(self.sales_data)} ventas)",
                                    size=16,
                                    color=ft.Colors.GREY_600,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Divider(height=20),
                        pager,
                        ft.Divider(height=10),
                        self._table_container,
                    ]
                ),
                padding=ft.Padding(20, 20, 20, 20),
                expand=True,
            )
        ]

    def create_data_row(self, data: dict) -> ft.DataRow:
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(str(data.get("product_name", "N/A")))),
                ft.DataCell(ft.Text(str(data.get("quantity", 0)))),
                ft.DataCell(ft.Text(str(data.get("unit_price", 0)))),
                ft.DataCell(ft.Text(str(data.get("total_price", 0)))),
                ft.DataCell(ft.Text(str(data.get("sale_date", "")))),
                ft.DataCell(
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                tooltip="Editar",
                                icon_color=ft.Colors.BLUE_600,
                                on_click=lambda e, sid=data.get("sale_id", 0): (
                                    self.on_edit(sid)
                                ),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.REMOVE_RED_EYE,
                                tooltip="Ver",
                                icon_color=ft.Colors.GREEN_600,
                                on_click=lambda e, sid=data.get("sale_id", 0): (
                                    self.on_view(sid)
                                ),
                            ),
                        ],
                        spacing=5,
                    )
                ),
            ]
        )

    def create_empty_state(self) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(
                        ft.Icons.INVENTORY_2_OUTLINED, size=64, color=ft.Colors.GREY_400
                    ),
                    ft.Text(
                        "No hay ventas registradas",
                        size=18,
                        color=ft.Colors.GREY_600,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        "Registra ventas para verlas aquí",
                        size=14,
                        color=ft.Colors.GREY_500,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
            ),
            padding=ft.Padding(40, 60, 40, 60),
            alignment=ft.Alignment(0, 0),
        )

    def on_add(self) -> None:
        return None

    def on_view(self, id: int):
        try:
            if self.page:
                self.page.go(f"/sales/view/{id}")
                return

            content = sale_detail_view(id, self.page)
            self.page.views.append(
                ft.View(
                    route=f"/sales/view/{id}",
                    controls=[
                        ft.AppBar(title=ft.Text(f"Detalle venta #{id}")),
                        content,
                    ],
                )
            )
            self.page.go(f"/sales/view/{id}")
        except Exception:
            self.page.update()

    def on_delete(self, id: int):
        pass

    def on_edit(self, id: int):
        if self.page:
            self.page.go(f"/sales/edit/{id}")

    def get_data(self) -> dict:
        return {"sales": self.sales_data, "total": len(self.sales_data)}
