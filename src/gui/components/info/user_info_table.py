import flet as ft
from typing import Sequence, Optional, Callable, Any, cast
from dataclasses import is_dataclass, asdict
from core.abstracts.info import Info
from services.user_service import UserService
from gui.components.dialog.user.delete_user_dialog import delete_user_dialog
from datetime import datetime, date


class UserInfoTable(Info):
    def __init__(self, router_callback: Optional[Callable[[str], None]] = None):
        super().__init__("Usuarios", "user_info_table")
        self.users_data: Sequence[dict] = []
        self.router_callback = router_callback
        self._table_container: Optional[ft.Container] = None

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

        rows = [self.create_user_row(u) for u in self.users_data]
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

        self._table_container = ft.Container(content=ft.Column([data_table], scroll=ft.ScrollMode.AUTO, expand=True), padding=ft.Padding(10, 10, 10, 10)) if len(rows) > 0 else self.create_empty_state()

        return [
            ft.Container(
                content=ft.Column([
                    ft.Row([ft.Text(self.title, size=24, weight=ft.FontWeight.BOLD), ft.Text(f"({len(self.users_data)} usuarios)", size=14, color=ft.Colors.GREY_600)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
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

        # DEBUG: print raw value/type to help trace why created_at isn't parsed
        try:
            print(f"[UserInfoTable] created_at raw: {repr(created_at)} type: {type(created_at)}")
        except Exception:
            pass

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
        if self.router_callback:
            self.router_callback(f"/users/edit/{user_id}")

    def on_delete(self, e: ft.ControlEvent, user_id: int):
        try:
            delete_user_dialog(e.page, int(user_id), on_deleted=lambda: self.router_callback("/users") if self.router_callback else None)
        except Exception as ex:
            cast(Any, e.page).snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"), open=True)
            e.page.update()

    def on_add_user(self, e):
        if self.router_callback:
            self.router_callback("/users/create")

    def get_data(self) -> dict:
        return {"users": self.users_data, "total": len(self.users_data)}
