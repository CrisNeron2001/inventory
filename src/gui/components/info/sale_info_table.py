from core.abstracts.info import Info
from typing import Sequence, Optional, Callable, Any, cast
from dataclasses import is_dataclass, asdict
import flet as ft
from gui.components.dialog.sale.delete_sale_dialog import delete_sale_dialog
from gui.views.sale.sale_detail_view import sale_detail_view
from services.session_service import SessionService
from services.cart_service import CartService
from config.settings import log

class SaleInfoTable(Info):
    def __init__(self, router_callback: Optional[Callable[[str], None]] = None):
        super().__init__("Ventas", "sale_info_table")
        self.sales_data: Sequence[dict] = []
        self.router_callback = router_callback
        self.current_page: int = 1
        self.page_size: int = 5
        self._table_container: Optional[ft.Container] = None
        self._pager_label: Optional[ft.Text] = None
        self._page_size_dd: Optional[ft.Dropdown] = None
        self._btn_prev: Optional[ft.IconButton] = None
        self._btn_next: Optional[ft.IconButton] = None
        self._table_height: int = 520

    def create_controls(self, info_data: Any) -> list[ft.Control]:
        carts_cache: dict[int, list] = {}

        def to_dict(item: Any) -> Optional[dict]:
            if isinstance(item, dict):
                sale_id = item.get("sale_id")
                cart_id = item.get("cart_id")
                unit_price = item.get("unit_price", 0)
                total_price = item.get("total_price", 0)
                sale_date = item.get("sale_date")
                notes = item.get("notes", "")

                product_name = item.get("product_name") or (f"Carrito {cart_id}" if cart_id is not None else "N/A")
                quantity = item.get("quantity", 0)

                if cart_id is not None:
                    try:
                        svc = CartService()
                        if cart_id in carts_cache:
                            cart_items = carts_cache[cart_id]
                        else:
                            cart_items = svc.get_cart_by_id(cart_id) or []
                            carts_cache[cart_id] = cart_items

                        names: list[str] = []
                        total_qty = 0
                        for cp in cart_items:
                            prod = None
                            try:
                                prod = cp.product if not isinstance(cp, dict) else cp.get('product')
                            except Exception:
                                prod = None
                            pname = None
                            if prod:
                                try:
                                    pname = getattr(prod, 'name', None) if not isinstance(prod, dict) else prod.get('name')
                                except Exception:
                                    pname = None
                            if pname:
                                names.append(str(pname))

                            raw_q = None
                            try:
                                raw_q = getattr(cp, 'quantity', None) if not isinstance(cp, dict) else cp.get('quantity', 0)
                            except Exception:
                                raw_q = 0
                            try:
                                q = int(raw_q or 0)
                            except Exception:
                                q = 0
                            total_qty += q

                        if names:
                            product_name = ", ".join(names)
                        quantity = total_qty
                        if total_qty == 0 and not cart_items:
                            log.info(f"Carrito {cart_id} no tiene productos asociados (cart_items vacio)")
                    except Exception as ex:
                        log.error(f"Error obteniendo productos del carrito {cart_id}: {ex}")
                        pass

                return {
                    "sale_id": sale_id,
                    "cart_id": cart_id,
                    "product_name": product_name,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total_price": total_price,
                    "sale_date": sale_date,
                    "notes": notes,
                }
            if is_dataclass(item) and not isinstance(item, type):
                d = asdict(item)
                sale_id = d.get("sale_id")
                cart_id = d.get("cart_id")
                unit_price = d.get("unit_price", 0)
                total_price = d.get("total_price", 0)
                sale_date = d.get("sale_date")
                notes = d.get("notes", "")

                product_name = d.get("product_name") or (f"Carrito {cart_id}" if cart_id is not None else "N/A")
                quantity = d.get("quantity", 0)

                return {
                    "sale_id": sale_id,
                    "cart_id": cart_id,
                    "product_name": product_name,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total_price": total_price,
                    "sale_date": sale_date,
                    "notes": notes,
                }
            if hasattr(item, "sale_id"):
                sale_id = getattr(item, "sale_id", None)
                cart_id = getattr(item, "cart_id", None)
                unit_price = getattr(item, "unit_price", 0)
                total_price = getattr(item, "total_price", 0)
                sale_date = getattr(item, "sale_date", None)
                notes = getattr(item, "notes", "")

                product_name = getattr(item, "product_name", None) or (f"Carrito {cart_id}" if cart_id is not None else "N/A")
                quantity = getattr(item, "quantity", 0)

                return {
                    "sale_id": sale_id,
                    "cart_id": cart_id,
                    "product_name": product_name,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total_price": total_price,
                    "sale_date": sale_date,
                    "notes": notes,
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
            if self.router_callback:
                self.router_callback(f"/sales/view/{sale_id}")
                return

            content = sale_detail_view(sale_id)
            if hasattr(e, "page") and getattr(e, "page") is not None:
                e.page.views.append(ft.View(route=f"/sales/view/{sale_id}", controls=[
                    ft.AppBar(title=ft.Text(f"Detalle venta #{sale_id}")),
                    content,
                ]))
                e.page.go(f"/sales/view/{sale_id}")
        except Exception as ex:
            cast(Any, e.page).snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"), open=True)
            e.page.update()

    def on_delete(self, e: ft.ControlEvent, sale_id: int):
        try:
            delete_sale_dialog(
                e.page,
                int(sale_id),
                on_deleted=lambda: self.router_callback("/sales") if self.router_callback else None
            )
        except Exception as ex:
            cast(Any, e.page).snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"), open=True)
            e.page.update()

    def on_edit(self, sale_id: int):
        if self.router_callback:
            self.router_callback(f"/sales/edit/{sale_id}")

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
