from core.abstracts.info import Info
from typing import Sequence, Optional, Any, cast
from dataclasses import is_dataclass, asdict
import flet as ft
from gui.views.product.product_detail_view import product_detail_view
from gui.components.paginator.paginator import Paginator


class ProductInfoTable(Info, Paginator):
    def __init__(self, page):
        Info.__init__(self, "Productos", "product_info_table")
        columns = [
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Descripción")),
            ft.DataColumn(ft.Text("Stock")),
            ft.DataColumn(ft.Text("Precio")),
            ft.DataColumn(ft.Text("Código")),
            ft.DataColumn(ft.Text("Categoría")),
            ft.DataColumn(ft.Text("Marca")),
            ft.DataColumn(ft.Text("Acciones")),
        ]
        Paginator.__init__(self, page, columns)
        self.page = page
        self.entity_name = ["product"]

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
                    "category": cat_name(cat),
                    "brand": cat_name(br),
                }
            return None

        if isinstance(info_data, dict):
            d = to_dict(info_data)
            self.seq_data = [d] if d is not None else []
        elif isinstance(info_data, Sequence):
            normalized: list[dict] = []
            for p in info_data:
                d = to_dict(p)
                if d is not None:
                    normalized.append(d)
            self.seq_data = normalized
        else:
            self.seq_data = []

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
                self._search_input,
                self._sort_dd,
                ft.Container(expand=True),
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
                                    f"({len(self.seq_data)} productos)",
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
        price_formatted = f"${data.get('price', 0)}"

        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(data.get("name", "N/A"))),
                ft.DataCell(ft.Text(data.get("description", "N/A"))),
                ft.DataCell(ft.Text(str(data.get("stock", 0)))),
                ft.DataCell(ft.Text(price_formatted)),
                ft.DataCell(ft.Text(data.get("sku", "N/A"))),
                ft.DataCell(ft.Text(str(data.get("category", "N/A")))),
                ft.DataCell(ft.Text(str(data.get("brand", "N/A")))),
                ft.DataCell(
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                tooltip="Editar",
                                icon_color=ft.Colors.BLUE_600,
                                on_click=lambda e, pid=data.get("product_id", 0): (
                                    self.on_edit(pid)
                                ),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.REMOVE_RED_EYE,
                                tooltip="Ver detalles",
                                icon_color=ft.Colors.GREEN_600,
                                on_click=lambda e, pid=data.get("product_id", 0): (
                                    self.on_view(pid)
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
                        "No hay productos disponibles",
                        size=18,
                        color=ft.Colors.GREY_600,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        "Agrega productos para verlos aquí",
                        size=14,
                        color=ft.Colors.GREY_500,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.ElevatedButton(
                        text="Agregar Producto",
                        icon=ft.Icons.ADD,
                        on_click=self.on_add(),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
            ),
            padding=ft.Padding(40, 60, 40, 60),
            alignment=ft.Alignment(0, 0),
        )

    def on_edit(self, id: int):
        if self.page:
            self.page.go(f"/products/edit/{id}")

    def on_delete(self, id: int):
        pass

    def on_view(self, id: int):
        try:
            if self.page:
                self.page.go(f"/products/view/{id}")
                return

            content = product_detail_view(self.page, id)
            cast(Any, self.page).views.append(
                ft.View(
                    route=f"/products/view/{id}",
                    controls=[
                        ft.AppBar(title=ft.Text(f"Detalle producto #{id}")),
                        content,
                    ],
                )
            )
            self.page.go(f"/products/view/{id}")
        except Exception:
            self.page.update()

    def on_add(self):
        if self.page:
            self.page.go("/products/create/")

    def get_data(self) -> dict:
        return {"products": self.seq_data, "total": self._filtered_total()}
