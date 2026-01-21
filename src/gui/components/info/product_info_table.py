from core.abstracts.info import Info
from typing import Sequence, Optional, Any, cast
from dataclasses import is_dataclass, asdict
import flet as ft
from gui.components.dialog.product.delete_product_dialog import delete_product_dialog
from services.session_service import SessionService
from gui.views.product.product_detail_view import product_detail_view
from gui.components.dialog.validate.error.error_dialog import error_dialog

class ProductInfoTable(Info):
    def __init__(self, page: ft.Page):
        super().__init__("Productos", "product_info_table")
        self.products_data: Sequence[dict] = []
        self.page = page
        self.current_page: int = 1
        self.page_size: int = 5
        self._table_container: Optional[ft.Container] = None
        self._pager_label: Optional[ft.Text] = None
        self._page_size_dd: Optional[ft.Dropdown] = None
        self._btn_prev: Optional[ft.IconButton] = None
        self._btn_next: Optional[ft.IconButton] = None
        self._table_height: int = 520
        self._search_query: str = ""
        self._sort_order: str = "desc"
        self._search_input: Optional[ft.TextField] = None
        self._sort_dd: Optional[ft.Dropdown] = None

    def create_controls(self, info_data: Any) -> list[ft.Control]:
        def to_dict(item: Any) -> Optional[dict]:
            if isinstance(item, dict):
                return {
                    "product_id": item.get("product_id"),
                    "name": item.get("name", ""),
                    "description": item.get("description", ""),
                    "stock": item.get("stock", 0),
                    "price": item.get("price", 0),
                    "sku": item.get("sku"),
                    "is_available": item.get("is_available", True),
                    "category": (
                        (item.get("category") or {}).get("name")
                        if isinstance(item.get("category"), dict)
                        else item.get("category")
                    ),
                    "brand": (
                        (item.get("brand") or {}).get("name")
                        if isinstance(item.get("brand"), dict)
                        else item.get("brand")
                    ),
                }
            if is_dataclass(item) and not isinstance(item, type):
                d = asdict(item)
                cat = d.get("category")
                br = d.get("brand")
                return {
                    "product_id": d.get("product_id"),
                    "name": d.get("name", ""),
                    "description": d.get("description", ""),
                    "stock": d.get("stock", 0),
                    "price": d.get("price", 0),
                    "sku": d.get("sku"),
                    "is_available": d.get("is_available", True),
                    "category": (cat.get("name") if isinstance(cat, dict) else cat),
                    "brand": (br.get("name") if isinstance(br, dict) else br),
                }
            if hasattr(item, "name"):
                cat = getattr(item, "category", None)
                br = getattr(item, "brand", None)
                def cat_name(v: Any) -> Optional[str]:
                    if v is None:
                        return None
                    if isinstance(v, str):
                        return v
                    if is_dataclass(v) and not isinstance(v, type):
                        vd = asdict(v)
                        return vd.get("name")
                    return getattr(v, "name", None)
                return {
                    "product_id": getattr(item, "product_id", None),
                    "name": getattr(item, "name", ""),
                    "description": getattr(item, "description", ""),
                    "stock": getattr(item, "stock", 0),
                    "price": getattr(item, "price", 0),
                    "sku": getattr(item, "sku", None),
                    "is_available": getattr(item, "is_available", True),
                    "category": cat_name(cat),
                    "brand": cat_name(br),
                }
            return None

        if isinstance(info_data, dict):
            d = to_dict(info_data)
            self.products_data = [d] if d is not None else []
        elif isinstance(info_data, Sequence):
            normalized: list[dict] = []
            for p in info_data:
                d = to_dict(p)
                if d is not None:
                    normalized.append(d)
            self.products_data = normalized
        else:
            self.products_data = []

        rows: list[ft.DataRow] = [self.create_product_row(p) for p in self._get_paged_items()]
        return self.create_product_info_table(rows)

    def create_product_info_table(self, rows: list[ft.DataRow]) -> list[ft.Control]:
        data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Descripción")),
                ft.DataColumn(ft.Text("Stock")),
                ft.DataColumn(ft.Text("Precio")),
                ft.DataColumn(ft.Text("Código")),
                ft.DataColumn(ft.Text("Estado Disponibilidad")),
                ft.DataColumn(ft.Text("Categoría")),
                ft.DataColumn(ft.Text("Marca")),
                ft.DataColumn(ft.Text("Acciones"))
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

        self._search_input = ft.TextField(
            value=self._search_query,
            label="Buscar",
            hint_text="Nombre, descripción o código",
            prefix_icon=ft.Icons.SEARCH,
            on_change=self._on_search_change,
            width=320,
        )
        self._sort_dd = ft.Dropdown(
            value=self._sort_order,
            options=[
                ft.DropdownOption(key="desc", text="Más reciente"),
                ft.DropdownOption(key="asc", text="Más antiguo"),
            ],
            width=160,
            label="Orden",
            on_change=self._on_sort_change,
        )

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
            self._search_input,
            self._sort_dd,
            ft.Container(expand=True),
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
                        ft.Text(f"({len(self.products_data)} productos)", size=16, color=ft.Colors.GREY_600),
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

    def create_product_row(self, data: dict) -> ft.DataRow:
        availability_text = "Disponible" if data.get("is_available", True) else "No disponible"
        price_formatted = f"${data.get('price', 0)}"
        session = SessionService()
        can_view_delete = session.has_permission("product.delete")
        current_user = session.get_current_user()
        role_name = None
        if current_user and getattr(current_user, "role_inv", None):
            role_name = getattr(current_user.role_inv, "name", None)
        is_admin = False
        if isinstance(role_name, str) and role_name.lower() in ("admin", "administrador", "administrator", "superuser"):
            is_admin = True

        return ft.DataRow(cells=[
            ft.DataCell(ft.Text(data.get('name', 'N/A'))),
            ft.DataCell(ft.Text(data.get('description', 'N/A'))),
            ft.DataCell(ft.Text(str(data.get('stock', 0)))),
            ft.DataCell(ft.Text(price_formatted)),
            ft.DataCell(ft.Text(data.get('sku', 'N/A'))),
            ft.DataCell(ft.Text(availability_text)),
            ft.DataCell(ft.Text(str(data.get('category', 'N/A')))),
            ft.DataCell(ft.Text(str(data.get('brand', 'N/A')))),
            ft.DataCell(ft.Row([
                ft.IconButton(
                    icon=ft.Icons.EDIT,
                    tooltip="Editar",
                    icon_color=ft.Colors.BLUE_600,
                    on_click=lambda e, pid=data.get('product_id', 0): self.on_edit(pid)
                ),
                *([ft.IconButton(
                    icon=ft.Icons.DELETE,
                    tooltip="Borrar",
                    icon_color=ft.Colors.RED_600,
                    disabled=not can_view_delete,
                    on_click=lambda e, pid=data.get('product_id', 0): self.on_delete(e, pid)
                )] if is_admin else []),
                ft.IconButton(
                    icon=ft.Icons.REMOVE_RED_EYE, 
                    tooltip="Ver detalles", 
                    icon_color=ft.Colors.GREEN_600,
                    on_click=lambda e, pid=data.get('product_id', 0): self.on_view(e, pid)),
                ], spacing=5)),
        ])

    def create_empty_state(self) -> ft.Container:
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.INVENTORY_2_OUTLINED, size=64, color=ft.Colors.GREY_400),
                ft.Text("No hay productos disponibles", size=18, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER),
                ft.Text("Agrega productos para verlos aquí", size=14, color=ft.Colors.GREY_500, text_align=ft.TextAlign.CENTER),
                ft.ElevatedButton(text="Agregar Producto", icon=ft.Icons.ADD, on_click=self.on_add_product),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16),
            padding=ft.Padding(40, 60, 40, 60),
            alignment=ft.Alignment(0, 0),
        )

    def on_edit(self, product_id: int):
        if self.page:
            self.page.go(f"/products/edit/{product_id}")

    def on_delete(self, e: ft.ControlEvent, product_id: int):
        try:
            delete_product_dialog(
				e.page,
				int(product_id),
				on_deleted=lambda: self.page.go("/products") if self.page else None
			)
        except Exception as ex:
            self.show_error_dialog([str(ex)])
            self.page.update()

    def on_view(self, e: ft.ControlEvent, product_id: int):
        try:
            if self.page:
                self.page.go(f"/products/view/{product_id}")
                return

            content = product_detail_view(self.page, product_id)
            cast(Any, self.page).views.append(ft.View(route=f"/products/view/{product_id}", controls=[
                ft.AppBar(title=ft.Text(f"Detalle producto #{product_id}")),
                content,
            ]))
            self.page.go(f"/products/view/{product_id}")
        except Exception as ex:
            self.show_error_dialog([str(ex)])
            self.page.update()

    def on_add_product(self, e):
        if self.page:
            self.page.go("/products/create")

    def get_data(self) -> dict:
        return {'products': self.products_data, 'total': self._filtered_total()}

    def _get_paged_items(self) -> list[dict]:
        data = self._filtered_sorted_data()
        total = len(data)
        if total == 0:
            return []
        self.current_page = max(1, min(self.current_page, self._total_pages()))
        start = (self.current_page - 1) * self.page_size
        end = min(start + self.page_size, total)
        return list(data[start:end])

    def _total_pages(self) -> int:
        if self.page_size <= 0:
            return 1
        total = self._filtered_total()
        return max(1, (total + self.page_size - 1) // self.page_size)

    def _pager_text(self) -> str:
        total = self._filtered_total()
        if total == 0:
            return "0 de 0"
        start = (self.current_page - 1) * self.page_size + 1
        end = min(self.current_page * self.page_size, total)
        return f"Mostrando {start}-{end} de {total} | Página {self.current_page} de {self._total_pages()}"

    def _filtered_sorted_data(self) -> list[dict]:
        def matches(p: dict) -> bool:
            if not self._search_query:
                return True
            q = self._search_query.lower()
            return (
                q in str(p.get("name", "")).lower()
                or q in str(p.get("description", "")).lower()
                or q in str(p.get("sku", "")).lower()
            )
        items = [p for p in self.products_data if matches(p)]
        try:
            items.sort(key=lambda x: int(x.get("product_id") or 0), reverse=(self._sort_order == "desc"))
        except Exception:
            items.sort(key=lambda x: str(x.get("product_id") or ""), reverse=(self._sort_order == "desc"))
        return items

    def _filtered_total(self) -> int:
        return len(self._filtered_sorted_data())

    def _refresh_table(self):
        if self._table_container is None:
            return
        rows = [self.create_product_row(p) for p in self._get_paged_items()]
        new_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Descripción")),
                ft.DataColumn(ft.Text("Stock")),
                ft.DataColumn(ft.Text("Precio")),
                ft.DataColumn(ft.Text("Código")),
                ft.DataColumn(ft.Text("Estado Disponibilidad")),
                ft.DataColumn(ft.Text("Categoría")),
                ft.DataColumn(ft.Text("Marca")),
                ft.DataColumn(ft.Text("Acciones"))
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

    def _on_search_change(self, e: ft.ControlEvent):
        self._search_query = str(e.control.value or "")
        self.current_page = 1
        self._refresh_table()

    def _on_sort_change(self, e: ft.ControlEvent):
        self._sort_order = str(e.control.value or "desc")
        self.current_page = 1
        self._refresh_table()

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