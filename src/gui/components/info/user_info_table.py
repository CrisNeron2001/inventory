import flet as ft
from typing import Sequence, Optional, Any
from dataclasses import is_dataclass, asdict
from core.abstracts.info import Info
from gui.components.dialog.user.delete_user_dialog import delete_user_dialog
from datetime import datetime, date
from gui.components.dialog.validate.error.error_dialog import error_dialog

class UserInfoTable(Info):
	def __init__(self, page: ft.Page):
		super().__init__("Usuarios", "user_info_table")
		self.users_data: Sequence[dict] = []
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
					"user_inv_id": item.get("user_inv_id"),
					"username": item.get("username", ""),
					"first_name": item.get("first_name", ""),
					"last_name": item.get("last_name", ""),
					"role": (item.get("role_inv") or {}).get("name") if isinstance(item.get("role_inv"), dict) else item.get("role_inv"),
					"created_at": item.get("created_at"),
				}
			if is_dataclass(item) and not isinstance(item, type):
				d = asdict(item)
				return {
					"user_inv_id": d.get("user_inv_id"),
					"username": d.get("username", ""),
					"first_name": d.get("first_name", ""),
					"last_name": d.get("last_name", ""),
					"role": (d.get("role_inv") or {}).get("name") if isinstance(d.get("role_inv"), dict) else d.get("role_inv"),
					"created_at": d.get("created_at"),
				}
			if hasattr(item, "username"):
				role = getattr(item, "role_inv", None)
				role_name = None
				if isinstance(role, dict):
					role_name = role.get("name")
				elif is_dataclass(role) and not isinstance(role, type):
					role_name = asdict(role).get("name")
				else:
					role_name = getattr(role, "name", None)

				return {
					"user_inv_id": getattr(item, "user_inv_id", None),
					"username": getattr(item, "username", ""),
					"first_name": getattr(item, "first_name", ""),
					"last_name": getattr(item, "last_name", ""),
					"role": role_name,
					"created_at": getattr(item, "created_at", None),
				}
			return None

		if isinstance(info_data, dict):
			d = to_dict(info_data)
			self.users_data = [d] if d is not None else []
		elif isinstance(info_data, Sequence):
			normalized: list[dict] = []
			for u in info_data:
				d = to_dict(u)
				if d is not None:
					normalized.append(d)
			self.users_data = normalized
		else:
			self.users_data = []

		rows = [self.create_user_row(u) for u in self._get_paged_items()]
		return self.create_user_info_table(rows)

	def create_user_info_table(self, rows: list[ft.DataRow]) -> list[ft.Control]:
		data_table = ft.DataTable(
			columns=[
				ft.DataColumn(ft.Text("Usuario")),
				ft.DataColumn(ft.Text("Nombre")),
				ft.DataColumn(ft.Text("Apellido")),
				ft.DataColumn(ft.Text("Rol")),
				ft.DataColumn(ft.Text("Creado")),
				ft.DataColumn(ft.Text("Acciones")),
			],
			rows=rows,
			border=ft.border.all(1, ft.Colors.OUTLINE),
			border_radius=8,
			heading_row_height=50,
			data_row_max_height=48,
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
					ft.Row([ft.Text(self.title, size=24, weight=ft.FontWeight.BOLD), ft.Text(f"({len(self.users_data)} usuarios)", size=14, color=ft.Colors.GREY_600)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
					ft.Divider(height=10),
					pager,
					ft.Divider(height=10),
					self._table_container,
				]),
				padding=ft.Padding(20, 20, 20, 20),
				expand=True,
			)
		]

	def create_user_row(self, data: dict) -> ft.DataRow:
		created_at = data.get("created_at")
		created_at_formatted = "N/A"
		try:
			if isinstance(created_at, datetime):
				created_at_formatted = created_at.strftime("%d-%m-%Y %H:%M:%S")
			elif isinstance(created_at, date):
				created_at_formatted = created_at.strftime("%d-%m-%Y")
			elif isinstance(created_at, str):
				s = created_at.strip()
				try:
					dt = datetime.fromisoformat(s)
					created_at_formatted = dt.strftime("%d-%m-%Y %H:%M:%S")
				except Exception:
					for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y", "%Y/%m/%d"):
						try:
							dt = datetime.strptime(s, fmt)
							created_at_formatted = dt.strftime("%d-%m-%Y %H:%M:%S")
							break
						except Exception:
							continue
		except Exception:
			created_at_formatted = "N/A"
		return ft.DataRow(cells=[
			ft.DataCell(ft.Text(data.get("username", "N/A"))),
			ft.DataCell(ft.Text(data.get("first_name", ""))),
			ft.DataCell(ft.Text(data.get("last_name", ""))),
			ft.DataCell(ft.Text(str(data.get("role", "")))),
			ft.DataCell(ft.Text(created_at_formatted)),
			ft.DataCell(ft.Row([
				ft.IconButton(icon=ft.Icons.EDIT, tooltip="Editar", icon_color=ft.Colors.BLUE_600, on_click=lambda e, uid=data.get("user_inv_id", 0): self.on_edit(uid)),
				ft.IconButton(icon=ft.Icons.DELETE, tooltip="Borrar", icon_color=ft.Colors.RED_600, on_click=lambda e, uid=data.get("user_inv_id", 0): self.on_delete(e, uid)),
			], spacing=6))
		])

	def create_empty_state(self) -> ft.Container:
		return ft.Container(
			content=ft.Column([
				ft.Icon(ft.Icons.PERSON_OUTLINE, size=64, color=ft.Colors.GREY_400),
				ft.Text("No hay usuarios", size=18, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER),
				ft.Text("Agrega usuarios para verlos aquí", size=14, color=ft.Colors.GREY_500, text_align=ft.TextAlign.CENTER),
				ft.ElevatedButton(text="Crear usuario", icon=ft.Icons.PERSON_ADD, on_click=self.on_add_user),
			], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16),
			padding=ft.Padding(40, 60, 40, 60),
			alignment=ft.Alignment(0, 0),
		)

	def on_edit(self, user_id: int):
		if self.page:
			self.page.go(f"/users/edit/{user_id}")

	def on_delete(self, e: ft.ControlEvent, user_id: int):
		try:
			delete_user_dialog(e.page, int(user_id), on_deleted=lambda: self.page.go("/users") if self.page else None)
		except Exception as ex:
			self.show_error_dialog([str(ex)])
			self.page.update()

	def on_add_user(self, e):
		if self.page:
			self.page.go("/users/create")

	def get_data(self) -> dict:
		return {"users": self.users_data, "total": self._filtered_total()}

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
		def matches(u: dict) -> bool:
			if not self._search_query:
				return True
			q = self._search_query.lower()
			return (
				q in str(u.get("username", "")).lower()
				or q in str(u.get("first_name", "")).lower()
				or q in str(u.get("last_name", "")).lower()
			)
		items = [u for u in self.users_data if matches(u)]
		def sort_key(x: dict):
			ca = x.get("created_at")
			if isinstance(ca, datetime) or isinstance(ca, date):
				return ca
			try:
				if isinstance(ca, str):
					try:
						return datetime.fromisoformat(ca)
					except Exception:
						return ca
			except Exception:
				pass
			try:
				return int(x.get("user_inv_id") or 0)
			except Exception:
				return str(x.get("user_inv_id") or "")
		try:
			items.sort(key=sort_key, reverse=(self._sort_order == "desc"))
		except Exception:
			items.sort(key=lambda x: str(x.get("user_inv_id") or ""), reverse=(self._sort_order == "desc"))
		return items

	def _filtered_total(self) -> int:
		return len(self._filtered_sorted_data())

	def _refresh_table(self):
		if self._table_container is None:
			return
		rows = [self.create_user_row(u) for u in self._get_paged_items()]
		new_table = ft.DataTable(
			columns=[
				ft.DataColumn(ft.Text("Usuario")),
				ft.DataColumn(ft.Text("Nombre")),
				ft.DataColumn(ft.Text("Apellido")),
				ft.DataColumn(ft.Text("Rol")),
				ft.DataColumn(ft.Text("Creado")),
				ft.DataColumn(ft.Text("Acciones")),
			],
			rows=rows,
			border=ft.border.all(1, ft.Colors.OUTLINE),
			border_radius=8,
			heading_row_height=50,
			data_row_max_height=48,
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
		except Exception:
			self.page_size = 5
		self.current_page = 1
		self._refresh_table()

	def show_error_dialog(self, errors: list[str]):
		error_msg = "\n".join(errors)
		error_dialog(self.page, error_msg, on_close=lambda: self.page.go("/"))