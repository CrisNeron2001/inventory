from abc import abstractmethod
from typing import Optional
from datetime import datetime, date
import flet as ft


class Paginator:
    def __init__(self, page: ft.Page, columns: list[ft.DataColumn]):
        self.data: list[dict] = []
        self.seq_data: list[dict] = []
        self.page = page
        self.entity_name: list[str] = [
            "user_inv",
            "product",
            "category",
            "sale",
            "cart",
            "cart_product",
            "brand",
        ]
        self.entity_ids: list[str] = [
            "user_inv_id",
            "product_id",
            "category_id",
            "sale_id",
            "cart_id",
            "cart_product_id",
            "brand_id",
        ]
        self.value: dict[str, set[str]] = {
            "user_inv": {
                "user_inv_id",
                "first_name",
                "middle_name",
                "last_name",
                "rut",
                "password",
                "created_at",
                "updated_at",
            },
            "product": {
                "product_id",
                "name",
                "description",
                "price",
                "stock",
                "category_id",
                "brand_id",
                "created_at",
                "updated_at",
            },
            "category": {
                "category_id",
                "name",
                "description",
                "created_at",
                "updated_at",
            },
            "brand": {"brand_id", "name", "description", "created_at", "updated_at"},
            "cart": {"cart_id", "user_inv_id"},
            "cart_product": {"cart_product_id", "cart_id", "product_id", "quantity"},
            "sale": {"sale_id", "cart_id", "total_amount", "created_at", "updated_at"},
        }
        self.columns = columns
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

    @abstractmethod
    def create_data_table(self, rows: list[ft.DataRow]) -> list[ft.Control]:
        raise NotImplementedError("create_data_table must be implemented by subclass")

    @abstractmethod
    def create_data_row(self, data: dict) -> ft.DataRow:
        raise NotImplementedError("create_data_row must be implemented by subclass")

    @abstractmethod
    def create_empty_state(self) -> ft.Container:
        raise NotImplementedError("create_empty_state must be implemented by subclass")

    @abstractmethod
    def on_edit(self, id: int) -> None:
        pass

    @abstractmethod
    def on_delete(self, id: int) -> None:
        pass

    @abstractmethod
    def on_add(self) -> None:
        pass

    @abstractmethod
    def on_view(self, id: int) -> None:
        pass

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
        def matches(d: dict) -> bool:
            if not self._search_query:
                return True
            q = self._search_query.lower()
            entity_fields = (
                self.value[self.entity_name[0]]
                if self.entity_name and self.entity_name[0] in self.value
                else set()
            )
            return any(q in str(d.get(field, "")).lower() for field in entity_fields)

        items = [d for d in self.seq_data if matches(d)]

        def sort_key(x: dict):
            ca = x.get("created_at")
            ua = x.get("updated_at")
            if isinstance(ca, datetime) or isinstance(ca, date):
                return ca
            if isinstance(ua, datetime) or isinstance(ua, date):
                return ua
            try:
                if isinstance(ca, str):
                    try:
                        return datetime.fromisoformat(ca)
                    except Exception:
                        return ca
                if isinstance(ua, str):
                    try:
                        return datetime.fromisoformat(ua)
                    except Exception:
                        return ua
            except Exception:
                pass
            try:
                id_fields = (
                    self.value[self.entity_ids[0]]
                    if self.entity_ids and self.entity_ids[0] in self.value
                    else set()
                )
                return int(
                    next(x[id_field] for id_field in id_fields if id_field in x), 0
                )
            except Exception:
                id_fields = (
                    self.value[self.entity_ids[0]]
                    if self.entity_ids and self.entity_ids[0] in self.value
                    else set()
                )
                return str(x[id_field] for id_field in id_fields if id_field in x or "")

        try:
            items.sort(key=sort_key, reverse=(self._sort_order == "desc"))
        except Exception:
            items.sort(
                key=lambda x: str(next(iter(x.values()), "")) if x else "",
                reverse=(self._sort_order == "desc"),
            )
        return items

    def _filtered_total(self) -> int:
        return len(self._filtered_sorted_data())

    def _refresh_table(self):
        if self._table_container is None:
            return
        items = self._get_paged_items()

        rows = [self.create_data_row(d) for d in items]

        visible_columns = [c for c in self.columns if c.visible]
        num_visible_cols = len(visible_columns)

        for row in rows:
            visible_cells = [c for c in row.cells if c.visible]
            num_visible_cells = len(visible_cells)
            if num_visible_cells != num_visible_cols:
                if num_visible_cells > num_visible_cols:
                    row.cells = row.cells[:num_visible_cols]
                else:
                    while len(row.cells) < num_visible_cols:
                        row.cells.append(ft.DataCell(ft.Text("")))

        new_table = ft.DataTable(
            columns=self.columns,
            rows=rows,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=8,
            heading_row_height=50,
            data_row_max_height=48,
        )
        self._table_container.content = (
            ft.Column([new_table], scroll=ft.ScrollMode.AUTO, expand=True)
            if len(rows) > 0
            else self.create_empty_state()
        )

        if self._pager_label:
            self._pager_label.value = self._pager_text()

        if self._btn_prev and self._btn_next:
            self._btn_prev.disabled = self.current_page <= 1
            self._btn_next.disabled = self.current_page >= self._total_pages()

        controls_to_update = [
            self._table_container,
            self._pager_label,
            self._btn_prev,
            self._btn_next,
        ]
        for ctl in controls_to_update:
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
        except Exception:
            self.page_size = 5
        self.current_page = 1
        self._refresh_table()
