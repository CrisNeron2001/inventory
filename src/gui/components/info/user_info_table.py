import flet as ft
from typing import Sequence, Optional, Any
from dataclasses import is_dataclass, asdict
from core.abstracts.info import Info
from gui.components.paginator.paginator import Paginator


class UserInfoTable(Info, Paginator):
    def __init__(self, page):
        Info.__init__(self, "Usuarios", "user_info_table")
        columns = [
            ft.DataColumn(ft.Text("Primer nombre")),
            ft.DataColumn(ft.Text("Segundo nombre")),
            ft.DataColumn(ft.Text("Apellidos")),
            ft.DataColumn(ft.Text("Rut")),
            ft.DataColumn(ft.Text("Acciones")),
        ]
        Paginator.__init__(self, page, columns)
        self.page = page
        self.entity_name = ["user_inv"]

    def create_controls(self, info_data: Any) -> list[ft.Control]:
        def to_dict(item: Any) -> Optional[dict]:
            if isinstance(item, dict):
                return {
                    "user_inv_id": item.get("user_inv_id"),
                    "rut": item.get("rut", ""),
                    "first_name": item.get("first_name", ""),
                    "middle_name": item.get("middle_name", ""),
                    "last_name": item.get("last_name", ""),
                    "created_at": item.get("created_at"),
                }
            if is_dataclass(item) and not isinstance(item, type):
                d = asdict(item)
                return {
                    "user_inv_id": d.get("user_inv_id"),
                    "rut": d.get("rut", ""),
                    "first_name": d.get("first_name", ""),
                    "middle_name": d.get("middle_name", ""),
                    "last_name": d.get("last_name", ""),
                    "created_at": d.get("created_at"),
                }
            if hasattr(item, "rut"):
                return {
                    "user_inv_id": getattr(item, "user_inv_id", None),
                    "rut": getattr(item, "rut", ""),
                    "first_name": getattr(item, "first_name", ""),
                    "middle_name": getattr(item, "middle_name", ""),
                    "last_name": getattr(item, "last_name", ""),
                    "created_at": getattr(item, "created_at", None),
                }
            return None

        if isinstance(info_data, dict):
            d = to_dict(info_data)
            self.seq_data = [d] if d is not None else []
        elif isinstance(info_data, Sequence):
            normalized: list[dict] = []
            for u in info_data:
                d = to_dict(u)
                if d is not None:
                    normalized.append(d)
            self.seq_data = normalized
        else:
            self.seq_data = []

        rows = [self.create_data_row(u) for u in self._get_paged_items()]
        return self.create_data_table(rows)

    def create_data_table(self, rows: list[ft.DataRow]) -> list[ft.Control]:
        data_table = ft.DataTable(
            columns=self.columns,
            rows=rows,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=8,
            heading_row_height=50,
            data_row_max_height=48,
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
            hint_text="Usuario, nombre o apellido",
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
                                    f"({len(self.seq_data)} usuarios)",
                                    size=14,
                                    color=ft.Colors.GREY_600,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Divider(height=10),
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
                ft.DataCell(ft.Text(data.get("first_name", ""))),
                ft.DataCell(ft.Text(data.get("middle_name", ""))),
                ft.DataCell(ft.Text(data.get("last_name", ""))),
                ft.DataCell(ft.Text(data.get("rut", "N/A"))),
                ft.DataCell(
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                tooltip="Editar",
                                icon_color=ft.Colors.BLUE_600,
                                on_click=lambda e, uid=data.get("user_inv_id", 0): (
                                    self.on_edit(uid)
                                ),
                            ),
                        ],
                        spacing=6,
                    )
                ),
            ]
        )

    def create_empty_state(self) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.PERSON_OUTLINE, size=64, color=ft.Colors.GREY_400),
                    ft.Text(
                        "No hay usuarios",
                        size=18,
                        color=ft.Colors.GREY_600,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        "Agrega usuarios para verlos aquí",
                        size=14,
                        color=ft.Colors.GREY_500,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.ElevatedButton(
                        text="Crear usuario",
                        icon=ft.Icons.PERSON_ADD,
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
            self.page.go(f"/users/edit/{id}")

    def on_delete(self, id: int):
        pass

    def on_add(self):
        if self.page:
            self.page.go("/users/create")

    def on_view(self, id: int):
        pass

    def get_data(self) -> dict:
        return {"users": self.seq_data, "total": self._filtered_total()}
