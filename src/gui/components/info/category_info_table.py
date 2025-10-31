from core.abstracts.info import Info
from typing import Sequence, Optional, Callable, Any, cast
from dataclasses import is_dataclass, asdict
import flet as ft
from gui.components.dialog.category.delete_category_dialog import delete_category_dialog

class CategoryInfoTable(Info):
    def __init__(self, router_callback: Optional[Callable[[str], None]] = None):
        super().__init__("Categorias", "category_info_table")
        self.category_data: Sequence[dict] = []
        self.router_callback = router_callback
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
                return {"category_id": item.get("category_id"), "name": item.get("name", "")}
            if is_dataclass(item) and not isinstance(item, type):
                d = asdict(item)
                return {"category_id": d.get("category_id"), "name": d.get("name", "")}
            if hasattr(item, "name") or hasattr(item, "category_id"):
                return {
                    "category_id": getattr(item, "category_id", None),
                    "name": getattr(item, "name", ""),
                }
            return None

        if isinstance(info_data, dict):
            d = to_dict(info_data)
            self.category_data = [d] if d is not None else []
        elif isinstance(info_data, Sequence):
            normalized: list[dict] = []
            for c in info_data:
                d = to_dict(c)
                if d is not None:
                    normalized.append(d)
            self.category_data = normalized
        else:
            self.category_data = []

        rows: list[ft.DataRow] = [self.create_data_row(c) for c in self._get_paged_items()]
        return self.create_category_info_table(rows)
    
    def create_category_info_table(self, rows: list[ft.DataRow]) -> list[ft.Control]:
        data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre")),
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
            hint_text="Nombre de la categoría",
            prefix_icon=ft.Icons.SEARCH,
            on_change=self._on_search_change,
            width=300,
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
                        ft.Text(f"({len(self.category_data)} categorias)", size=16, color=ft.Colors.GREY_600),
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
        
    def create_data_row(self, data: dict) -> ft.DataRow:
        return ft.DataRow(cells=[
			ft.DataCell(ft.Text(data.get('name', 'N/A'))),
            ft.DataCell(ft.Row([
                ft.IconButton(
                    icon=ft.Icons.EDIT,
                    tooltip="Editar",
                    icon_color=ft.Colors.BLUE_600,
                    on_click=lambda e, cid=data.get('category_id', 0): self.on_edit(cid)
                ),
                ft.IconButton(
                    icon=ft.Icons.DELETE,
                    tooltip="Borrar",
                    icon_color=ft.Colors.RED_600,
                    on_click=lambda e, cid=data.get('category_id', 0): self.on_delete(e, cid)
                )
            ], spacing=5)),
		])
        
    def create_empty_state(self) -> ft.Container:
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.INVENTORY_2_OUTLINED, size=64, color=ft.Colors.GREY_400),
                ft.Text("No hay categorias disponibles", size=18, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER),
                ft.Text("Agrega categorias para verlos aquí", size=14, color=ft.Colors.GREY_500, text_align=ft.TextAlign.CENTER),
                ft.ElevatedButton(text="Agregar categoria", icon=ft.Icons.ADD, on_click=self.on_add_category),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16),
            padding=ft.Padding(40, 60, 40, 60),
            alignment=ft.Alignment(0, 0),
        )
        
    def on_edit(self, category_id: int):
        if self.router_callback:
            self.router_callback(f"/categories/edit/{category_id}")

    def on_delete(self, e: ft.ControlEvent, category_id: int):
        try:
            delete_category_dialog(
                e.page, 
                int(category_id), 
                on_deleted=lambda: self.router_callback("/categories") if self.router_callback else None
            )
        except Exception as ex:
            cast(Any, e.page).snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"), open=True)
            e.page.update()
            
    def on_add_category(self, e):
        if self.router_callback:
            self.router_callback("/categories/create")

    def get_data(self) -> dict:
        return {'categories': self.category_data, 'total': self._filtered_total()}

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
        def matches(c: dict) -> bool:
            if not self._search_query:
                return True
            q = self._search_query.lower()
            return q in str(c.get("name", "")).lower()
        items = [c for c in self.category_data if matches(c)]
        try:
            items.sort(key=lambda x: int(x.get("category_id") or 0), reverse=(self._sort_order == "desc"))
        except Exception:
            items.sort(key=lambda x: str(x.get("category_id") or ""), reverse=(self._sort_order == "desc"))
        return items

    def _filtered_total(self) -> int:
        return len(self._filtered_sorted_data())

    def _refresh_table(self):
        if self._table_container is None:
            return
        rows = [self.create_data_row(c) for c in self._get_paged_items()]
        new_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre")),
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
        try:
            self.page_size = int(e.control.value)
            self.current_page = 1
            self._refresh_table()
        except Exception:
            pass