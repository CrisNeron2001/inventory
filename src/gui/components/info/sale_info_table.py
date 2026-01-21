from core.abstracts.info import Info
from typing import Sequence, Optional, Any
from dataclasses import is_dataclass, asdict
import flet as ft
from gui.components.dialog.sale.delete_sale_dialog import delete_sale_dialog
from gui.views.sale.sale_detail_view import sale_detail_view
from services.session_service import SessionService
from gui.components.dialog.validate.error.error_dialog import error_dialog

class SaleInfoTable(Info):
    def __init__(self, page: ft.Page):
        super().__init__("Ventas", "sale_info_table")
        self.sales_data: Sequence[dict] = []
        self.current_page: int = 1
        self.page_size: int = 5
        self._table_container: Optional[ft.Container] = None
        self._pager_label: Optional[ft.Text] = None
        self._page_size_dd: Optional[ft.Dropdown] = None
        self._btn_prev: Optional[ft.IconButton] = None
        self._btn_next: Optional[ft.IconButton] = None
        self._table_height: int = 520
        self.page = page

    def create_controls(self, info_data: Any) -> list[ft.Control]:
        carts_cache: dict[int, list] = {}

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
            self.sales_data = [d] if d is not None else []
        elif isinstance(info_data, Sequence):
            normalized: list[dict] = []
            for p in info_data:
                d = to_dict(p)
                if d is not None:
                    normalized.append(d)
            self.sales_data = normalized
        else:
            self.sales_data = []

        rows: list[ft.DataRow] = [self.create_sale_row(p) for p in self._get_paged_items()]
        return self.create_sale_info_table(rows)

    def create_sale_info_table(self, rows: list[ft.DataRow]) -> list[ft.Control]:
        data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Producto")),
                ft.DataColumn(ft.Text("Cantidad")),
                ft.DataColumn(ft.Text("Precio unit.")),
                ft.DataColumn(ft.Text("Total")),
                ft.DataColumn(ft.Text("Fecha")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=rows,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=8,
            heading_row_height=50,
            data_row_max_height=60,
        )

        self._table_container = ft.Container(
            content=ft.Column([data_table], scroll=ft.ScrollMode.AUTO, expand=True),
            border_radius=8,
            padding=ft.Padding(10, 10, 10, 10),
            height=self._table_height,
        ) if len(rows) > 0 else self.create_empty_state()

        self._pager_label = ft.Text(self._pager_text(), size=12, color=ft.Colors.GREY_600)
        self._page_size_dd = ft.Dropdown(
            value=str(self.page_size),
            options=[ft.DropdownOption(key=str(v)) for v in [5, 10, 20, 50]],
            width=90,
            on_change=self._on_page_size_change,
            label="Por página",
        )
        self._btn_prev = ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, tooltip="Anterior", on_click=self._on_prev, disabled=(self.current_page <= 1))
        self._btn_next = ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT, tooltip="Siguiente", on_click=self._on_next, disabled=(self.current_page >= self._total_pages()))

        pager = ft.Row([
            self._btn_prev,
            self._btn_next,
            ft.VerticalDivider(width=1),
            self._pager_label,
            ft.Container(expand=True),
            self._page_size_dd,
        ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER)

        return [
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(self.title, size=24, weight=ft.FontWeight.BOLD),
                        ft.Text(f"({len(self.sales_data)} ventas)", size=16, color=ft.Colors.GREY_600),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(height=20),
                    pager,
                    ft.Divider(height=10),
                    self._table_container,
                ]),
                padding=ft.Padding(20, 20, 20, 20),
                expand=True,
            )
        ]

    def create_sale_row(self, data: dict) -> ft.DataRow:
        session = SessionService()
        can_view_delete = session.has_permission("sale.delete")
        current_user = session.get_current_user()
        role_name = None
        if current_user and getattr(current_user, "role_inv", None):
            role_name = getattr(current_user.role_inv, "name", None)
        is_admin = False
        if isinstance(role_name, str) and role_name.lower() in ("admin", "administrador", "administrator", "superuser"):
            is_admin = True
        
        return ft.DataRow(cells=[
            ft.DataCell(ft.Text(str(data.get('sale_id', 'N/A')))),
            ft.DataCell(ft.Text(str(data.get('product_name', 'N/A')))),
            ft.DataCell(ft.Text(str(data.get('quantity', 0)))),
            ft.DataCell(ft.Text(str(data.get('unit_price', 0)))),
            ft.DataCell(ft.Text(str(data.get('total_price', 0)))),
            ft.DataCell(ft.Text(str(data.get('sale_date', '')))),
            ft.DataCell(ft.Row([
                ft.IconButton(
                    icon=ft.Icons.EDIT, 
                    tooltip="Editar", 
                    icon_color=ft.Colors.BLUE_600,
                    on_click=lambda e, sid=data.get('sale_id', 0): self.on_edit(sid)),
                ft.IconButton(
                    icon=ft.Icons.REMOVE_RED_EYE, 
                    tooltip="Ver", 
                    icon_color=ft.Colors.GREEN_600,
                    on_click=lambda e, sid=data.get('sale_id', 0): self.on_view(e, sid)),
                *([ft.IconButton(
                    icon=ft.Icons.DELETE, 
                    tooltip="Borrar", 
                    disabled=not can_view_delete,
                    icon_color=ft.Colors.RED_600,
                    on_click=lambda e, sid=data.get('sale_id', 0): self.on_delete(e, sid)
                )] if is_admin else []),
            ], spacing=5)),
        ])

    def create_empty_state(self) -> ft.Container:
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.INVENTORY_2_OUTLINED, size=64, color=ft.Colors.GREY_400),
                ft.Text("No hay ventas registradas", size=18, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER),
                ft.Text("Registra ventas para verlas aquí", size=14, color=ft.Colors.GREY_500, text_align=ft.TextAlign.CENTER),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16),
            padding=ft.Padding(40, 60, 40, 60),
            alignment=ft.Alignment(0, 0),
        )

    def on_view(self, e: ft.ControlEvent, sale_id: int):
        try:
            if self.page:
                self.page.go(f"/sales/view/{sale_id}")
                return

            content = sale_detail_view(sale_id, self.page)
            self.page.views.append(ft.View(route=f"/sales/view/{sale_id}", controls=[
                    ft.AppBar(title=ft.Text(f"Detalle venta #{sale_id}")),
                    content,
                ]))
            self.page.go(f"/sales/view/{sale_id}")
        except Exception as ex:
            self.show_error_dialog([str(ex)])
            self.page.update()

    def on_delete(self, e: ft.ControlEvent, sale_id: int):
        try:
            delete_sale_dialog(
                self.page,
                int(sale_id),
                on_deleted=lambda: self.page.go("/sales") if self.page else None
            )
        except Exception as ex:
            self.show_error_dialog([str(ex)])
            self.page.update()

    def on_edit(self, sale_id: int):
        if self.page:
            self.page.go(f"/sales/edit/{sale_id}")

    def get_data(self) -> dict:
        return {'sales': self.sales_data, 'total': len(self.sales_data)}

    def _get_paged_items(self) -> list[dict]:
        total = len(self.sales_data)
        if total == 0:
            return []
        self.current_page = max(1, min(self.current_page, self._total_pages()))
        start = (self.current_page - 1) * self.page_size
        end = min(start + self.page_size, total)
        return list(self.sales_data[start:end])

    def _total_pages(self) -> int:
        if self.page_size <= 0:
            return 1
        total = len(self.sales_data)
        return max(1, (total + self.page_size - 1) // self.page_size)

    def _pager_text(self) -> str:
        total = len(self.sales_data)
        if total == 0:
            return "0 de 0"
        start = (self.current_page - 1) * self.page_size + 1
        end = min(self.current_page * self.page_size, total)
        return f"Mostrando {start}-{end} de {total} | Página {self.current_page} de {self._total_pages()}"

    def _refresh_table(self):
        if self._table_container is None:
            return
        rows = [self.create_sale_row(c) for c in self._get_paged_items()]
        new_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Producto")),
                ft.DataColumn(ft.Text("Cantidad")),
                ft.DataColumn(ft.Text("Precio unit.")),
                ft.DataColumn(ft.Text("Total")),
                ft.DataColumn(ft.Text("Fecha")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=rows,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=8,
            heading_row_height=50,
            data_row_max_height=60,
    )
        self._table_container.content = ft.Column([new_table], scroll=ft.ScrollMode.AUTO, expand=True) if len(rows) > 0 else self.create_empty_state()

        if self._pager_label:
            self._pager_label.value = self._pager_text()

        btn_states = {
            self._btn_prev: (self.current_page <= 1),
            self._btn_next: (self.current_page >= self._total_pages()),
        }
        for btn, disabled in btn_states.items():
            if btn:
                btn.disabled = disabled

        for ctl in [self._table_container, self._pager_label, self._btn_prev, self._btn_next]:
            if ctl:
                ctl.update()

    def _on_prev(self, e: ft.ControlEvent):
        if self.current_page > 1:
            self.current_page -= 1
            self._refresh_table()

    def _on_next(self, e: ft.ControlEvent):
        if self.current_page < self._total_pages():
            self.current_page += 1
            self._refresh_table()

    def _on_page_size_change(self, e: ft.ControlEvent):
        self.page_size = int(e.control.value)
        self.current_page = 1
        self._refresh_table()
        
    def show_error_dialog(self, errors: list[str]):
        error_msg = "\n".join(errors)
        error_dialog(self.page, error_msg, on_close=lambda: self.page.go("/"))