import flet as ft
from typing import Callable, Optional
from services.session_service import SessionService
from services.role_service import RoleService


def define_menu_bar(on_route_change: Callable[[str], None], on_toggle: Optional[Callable[[], None]] = None) -> ft.Container:
    def create_menu_item(icon: str, text: str, route: str) -> ft.ListTile:
        return ft.ListTile(
            leading=ft.Icon(icon),
            title=ft.Text(text),
            on_click=lambda e: on_route_change(route)
        )

    def _logout_click(e: ft.ControlEvent) -> None:
        session = SessionService()
        logout_fn = getattr(session, "logout", None)
        if callable(logout_fn):
            logout_fn()
        on_route_change("/login")

    session = SessionService()
    current_user = session.get_current_user()
    role_name = None
    if current_user and getattr(current_user, "role_inv", None):
        try:
            role_name = getattr(current_user.role_inv, "name", None)
        except Exception:
            if isinstance(current_user.role_inv, str):
                role_name = str(current_user.role_inv)

    if not role_name and current_user and getattr(current_user, 'role_inv_id', None):
        try:
            rs = RoleService()
            role_id_raw = current_user.role_inv_id
            role_id = int(role_id_raw) if role_id_raw is not None else None
            if role_id is not None:
                resolved = rs.get_role_by_id(role_id)
                if resolved:
                    role_name = getattr(resolved, 'name', None)
        except Exception:
            pass
    is_admin = False
    if isinstance(role_name, str) and role_name.lower() in ("admin", "administrador", "administrator", "superuser"):
        is_admin = True
    admin_perms = [
        "product.create",
        "product.update_quantity",
        "user.create",
        "user.view",
        "category.view",
        "brand.view",
        "sale.create",
        "sale.view",
    ]
    if not is_admin and any(session.has_permission(p) for p in admin_perms):
        is_admin = True

    if is_admin:
        can_view_products = True
        can_manage_products = True
        can_view_categories = True
        can_view_brands = True
    else:
        can_view_products = session.has_permission("product.view")
        can_manage_products = session.has_permission("product.update_quantity") or session.has_permission("product.create")
        can_view_categories = session.has_permission("category.view")
        can_view_brands = session.has_permission("brand.view")

    can_create_products = is_admin or session.has_permission("product.create")

    return ft.Container(
        width=280,
        padding=ft.Padding(15, 20, 15, 20),
        content=ft.Column(
            spacing=5,
            controls=[
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.INVENTORY_2, size=32, color=ft.Colors.BLUE_600),
                        ft.Text(
                            "Inventario",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_600
                        )
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    margin=ft.Margin(0, 0, 0, 20)
                ),

                ft.Divider(),

                ft.ListTile(
                    leading=ft.Icon(ft.Icons.HOME),
                    title=ft.Text("Inicio"),
                    on_click=lambda e: on_route_change("/")
                ),

                ft.Divider(height=10),

                *([ft.ExpansionTile(
                    title=ft.Text("Productos", weight=ft.FontWeight.W_500),
                    leading=ft.Icon(ft.Icons.SHOPPING_BAG),
                    controls=(
                        ([create_menu_item(ft.Icons.ADD, "Crear producto", "/products/create")] if (is_admin or session.has_permission("product.create")) else [])
                        + ([create_menu_item(ft.Icons.EDIT, "Actualizar stock", "/products/edit_stock")] if session.has_permission("product.edit_stock") or is_admin else [])
                    ),
                    initially_expanded=False
                )] if (is_admin or session.has_permission("product.view") or session.has_permission("product.create")) else []),

                *([ft.ExpansionTile(
                    title=ft.Text("Categorías", weight=ft.FontWeight.W_500),
                    leading=ft.Icon(ft.Icons.CATEGORY),
                    controls=(
                        ([create_menu_item(ft.Icons.ADD, "Crear categoría", "/categories/create")] if is_admin else [])
                        + ([create_menu_item(ft.Icons.LIST, "Ver categorías", "/categories")] if (is_admin or can_view_categories) else [])
                    ),
                    initially_expanded=False
                )] if (is_admin or can_view_categories) else []),

                *([ft.ExpansionTile(
                    title=ft.Text("Marcas", weight=ft.FontWeight.W_500),
                    leading=ft.Icon(ft.Icons.BRANDING_WATERMARK),
                    controls=(
                        ([create_menu_item(ft.Icons.ADD, "Crear marca", "/brands/create")] if is_admin else [])
                        + ([create_menu_item(ft.Icons.LIST, "Ver marcas", "/brands")] if (is_admin or can_view_brands) else [])
                    ),
                    initially_expanded=False
                )] if (is_admin or can_view_brands) else []),

                *([ft.ExpansionTile(
                    title=ft.Text("Usuarios", weight=ft.FontWeight.W_500),
                    leading=ft.Icon(ft.Icons.PERSON),
                    controls=(
                        ([create_menu_item(ft.Icons.PERSON_ADD, "Crear usuario", "/users/create")] if is_admin else [])
                        + ([create_menu_item(ft.Icons.LIST, "Ver usuarios", "/users")] if is_admin else [])
                    ),
                    initially_expanded=False
                )] if is_admin else []),
                
                ft.ExpansionTile(
                    title=ft.Text("Ventas", weight=ft.FontWeight.W_500),
                    leading=ft.Icon(ft.Icons.PAYMENT),
                    controls=(
                        ([create_menu_item(ft.Icons.PAYMENT, "Punto de venta", "/sales/pos")] if (is_admin or session.has_permission("sale.create")) else [])
                        + ([create_menu_item(ft.Icons.LIST, "Ver ventas", "/sales")] if (is_admin or session.has_permission("sale.view")) else [])
                    ),
                    initially_expanded=False
                ),
                # Debug session menu removed
                ft.Divider(),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.EXIT_TO_APP),
                    title=ft.Text("Cerrar sesión"),
                    on_click=_logout_click,
                ),
            ]
        )
    )