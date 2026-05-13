# flet
import flet as ft

# typings
from typing import Callable, Dict, cast

# menu
from gui.components.menu.menu import define_menu_bar

# add
from gui.views.product.menu_create_product_view import menu_create_product_view
from gui.views.product.create_product_manual_view import create_product_manual_view
from gui.views.category.add_category_view import add_category_view
from gui.views.brand.add_brand_view import add_brand_view
from gui.views.auth.login_view import login_view
from gui.views.auth.register_view import register_view

# edit
from gui.views.product.edit_product_view import edit_product_view
from gui.views.product.edit_product_stock_view import edit_product_stock_view
from gui.views.category.edit_category_view import edit_category_view
from gui.views.brand.edit_brand_view import edit_brand_view

# detail view
from gui.views.product.product_detail_view import product_detail_view
from gui.views.sale.sale_detail_view import sale_detail_view

# table registrations
from gui.views.product.product_registrations_view import product_registrations_view
from gui.views.category.category_registrations_view import category_registrations_view
from gui.views.brand.brand_registrations_view import brand_registrations_view
from gui.views.sale.pos_view import pos_view
from gui.views.sale.sale_registrations_view import sale_registrations_view
from gui.views.sale.edit_sale_view import edit_sale_view
from gui.views.user.user_registrations_view import user_registrations_view
from gui.views.user.add_user_view import add_user_view
from gui.views.user.edit_user_view import edit_user_view

# delete dialog
from gui.components.dialog.product.delete_product_dialog import delete_product_dialog
from gui.components.dialog.category.delete_category_dialog import delete_category_dialog
from gui.components.dialog.brand.delete_brand_dialog import delete_brand_dialog
from gui.components.dialog.sale.delete_sale_dialog import delete_sale_dialog
from gui.components.dialog.user.delete_user_dialog import delete_user_dialog

# validations dialogs
from gui.components.dialog.validate.error.error_dialog import error_dialog


class AppRouter:
    def __init__(self, page: ft.Page):
        self.page = page

        self.page.on_route_change = self._route_change
        self.page.on_view_pop = self._view_pop
        self._sidebar_open: bool = False
        self._sidebar_container: ft.Container | None = None
        self._menu_toggle_btn: ft.IconButton | None = None

        self.routes: Dict[str, Dict] = {
            "/": {"title": "Inventario", "view": self._home_view},
            "/products/create": {
                "title": "Crear producto",
                "view": self._create_product_view,
            },
            "/products/edit_stock": {
                "title": "Editar Disponibilidad producto",
                "view": self._edit_product_stock_view,
            },
            "/categories": {"title": "Categorías", "view": self._categories_list_view},
            "/categories/create": {
                "title": "Crear categoría",
                "view": self._create_category_view,
            },
            "/brands": {"title": "Marcas", "view": self._brands_list_view},
            "/brands/create": {"title": "Crear marca", "view": self._create_brand_view},
            "/sales/pos": {"title": "Punto de venta", "view": self._pos_view},
            "/sales": {"title": "Ventas", "view": self._sales_list_view},
            "/users": {"title": "Usuarios", "view": self._users_list_view},
            "/users/create": {"title": "Crear usuario", "view": self._create_user_view},
            "/login": {"title": "Iniciar sesión", "view": self._login_view},
            "/register": {"title": "Crear cuenta", "view": self._register_view},
        }

    def user_exists(self) -> bool:
        return self.page.session.get("user_inv") is not None

    def start(self) -> None:
        if self.user_exists():
            self.page.go("/")
        else:
            self.page.go("/login")

    def navigate_to(self, route: str) -> None:
        try:
            current = self.page.route
        except Exception:
            current = None

        if current == route:
            self.page.views.clear()
            self._add_base_view(route)
            self.page.update()
        else:
            self.page.go(route)

    def _route_change(self, _: ft.RouteChangeEvent) -> None:
        route = self.page.route
        self.page.views.clear()
        self._add_base_view(route)

        if (
            self.product_handle_dynamic_route(route)
            or self.category_handle_dynamic_route(route)
            or self.brand_handle_dynamic_route(route)
            or self._user_handle_dynamic_route(route)
            or self.sale_handle_dynamic_route(route)
        ):
            self.page.update()
            return

        if route in self.routes and route not in ("/", "/login", "/register"):
            self._push_view(
                route, self.routes[route]["title"], self.routes[route]["view"]()
            )
        self.page.update()

    def _view_pop(self, _: ft.ViewPopEvent) -> None:
        if self.page.views:
            self.page.views.pop()
            if self.page.views:
                top = self.page.views[-1]
                self.page.go(str(top.route))
                print(top.route)
            else:
                self.page.go("/")

    def _build_layout(self, content: ft.Control) -> ft.Row:
        menu_panel = define_menu_bar(self.navigate_to, self._toggle_sidebar)
        self._sidebar_container = ft.Container(
            content=menu_panel,
            width=280 if self._sidebar_open else 0,
            opacity=1.0 if self._sidebar_open else 0.0,
            animate=ft.Animation(250, ft.AnimationCurve.EASE_IN_OUT),
            animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
        )
        return ft.Row(
            [
                self._sidebar_container,
                ft.VerticalDivider(width=1),
                content,
            ],
            expand=True,
        )

    def _create_menu_button(self) -> ft.IconButton:
        self._menu_toggle_btn = ft.IconButton(
            icon=ft.Icons.CLOSE if self._sidebar_open else ft.Icons.MENU,
            tooltip="Mostrar/ocultar menú",
            on_click=self._toggle_sidebar,
        )
        return self._menu_toggle_btn

    def _create_back_button(self) -> ft.IconButton:
        return ft.IconButton(
            icon=ft.Icons.CANCEL,
            tooltip="Atrás",
            on_click=self._on_back,
        )

    def _on_back(self, e: ft.ControlEvent | None = None) -> None:
        if len(self.page.views) > 1:
            self.page.views.pop()
            top = self.page.views[-1]
            self.page.go(str(top.route))
        else:
            self.page.go("/")

    def _add_base_view(self, current_route: str) -> None:
        if current_route in ("/login", "/register"):
            self._sidebar_open = False
            content = (
                self._login_view()
                if current_route == "/login"
                else self._register_view()
            )
            layout = ft.Container(content=content, expand=True)

            base = ft.View(
                route=current_route,
                controls=[
                    ft.AppBar(
                        title=ft.Text(self.routes[current_route]["title"]),
                        bgcolor=ft.Colors.SURFACE,
                    ),
                    layout,
                ],
                padding=0,
            )
            self.page.views.append(base)
            return

        content = (
            self._home_view() if current_route == "/" else ft.Container(expand=True)
        )
        layout = self._build_layout(content)

        base = ft.View(
            route="/",
            controls=[
                ft.AppBar(
                    title=ft.Text(self.routes["/"]["title"]),
                    bgcolor=ft.Colors.SURFACE,
                    leading=self._create_menu_button(),
                ),
                layout,
            ],
            padding=0,
        )
        self.page.views.append(base)

    def _toggle_sidebar(self, e: ft.ControlEvent | None = None) -> None:
        self._sidebar_open = not self._sidebar_open
        if self._sidebar_container is not None:
            self._sidebar_container.width = 280 if self._sidebar_open else 0
            self._sidebar_container.opacity = 1.0 if self._sidebar_open else 0.0
        if self._menu_toggle_btn is not None:
            self._menu_toggle_btn.icon = (
                ft.Icons.CLOSE if self._sidebar_open else ft.Icons.MENU
            )
        self.page.update()

    def _push_view(self, route: str, title: str, content: ft.Control) -> None:
        layout = self._build_layout(content)
        leading_btn = self._create_menu_button()
        actions = (
            [cast(ft.Control, self._create_back_button())]
            if route not in ("/login", "/register")
            else None
        )

        self.page.views.append(
            ft.View(
                route=route,
                controls=[
                    ft.AppBar(
                        title=ft.Text(title),
                        bgcolor=ft.Colors.SURFACE,
                        leading=leading_btn,
                        actions=actions,
                    ),
                    layout,
                ],
                padding=0,
            )
        )

    def product_handle_dynamic_route(self, route: str) -> bool:
        handlers: Dict[str, Callable[[str], None]] = {}

        def create_product_subroutes(mode: str) -> None:
            if mode == "manual":
                content = create_product_manual_view(self.page)
                self._push_view(route, "Creacion manual de producto", content)

        def handle_delete(pid: str) -> None:
            self._push_view("/products", "Productos", self._products_list_view())
            delete_product_dialog(
                self.page, int(pid), on_deleted=lambda: self.page.go("/products")
            )

        def handle_view(pid: str) -> None:
            content = product_detail_view(self.page, int(pid))
            self._push_view(route, f"Detalle producto #{pid}", content)

        def handle_edit(pid: str) -> None:
            content = edit_product_view(int(pid), self.page)
            self._push_view(route, f"Editar producto #{pid}", content)

        handlers = {
            "/products/delete/": handle_delete,
            "/products/view/": handle_view,
            "/products/edit/": handle_edit,
            "/products/create/": create_product_subroutes,
        }

        for prefix, handler in handlers.items():
            if route.startswith(prefix):
                param = route[len(prefix) :]
                if param.endswith("/"):
                    param = param[:-1]
                if not param and prefix != "/products/create/":
                    return False
                try:
                    handler(param)
                except Exception as ex:
                    self.show_validate_error_dialog([str(ex)])
                return True
        return False

    def category_handle_dynamic_route(self, route: str) -> bool:
        handlers: Dict[str, Callable[[str], None]] = {}

        def handle_delete(cid: str) -> None:
            self._push_view("/categories", "Categorías", self._categories_list_view())
            delete_category_dialog(
                self.page, int(cid), on_deleted=lambda: self.page.go("/categories")
            )

        def handle_edit(cid: str) -> None:
            content = edit_category_view(int(cid), self.page)
            self._push_view(route, f"Editar categoría #{cid}", content)

        handlers = {
            "/categories/delete/": handle_delete,
            "/categories/edit/": handle_edit,
        }

        for prefix, handler in handlers.items():
            if route.startswith(prefix):
                param = route[len(prefix) :]
                if param.endswith("/"):
                    param = param[:-1]
                if not param and prefix != "/categories/create/":
                    return False
                try:
                    handler(param)
                except Exception as ex:
                    self.show_validate_error_dialog([str(ex)])
                return True
        return False

    def brand_handle_dynamic_route(self, route: str) -> bool:
        handlers: Dict[str, Callable[[str], None]] = {}

        def handle_delete(bid: str) -> None:
            self._push_view("/brands", "Marcas", self._brands_list_view())
            delete_brand_dialog(
                self.page, int(bid), on_deleted=lambda: self.page.go("/brands")
            )

        def handle_edit(bid: str) -> None:
            content = edit_brand_view(int(bid), self.page)
            self._push_view(route, f"Editar marca #{bid}", content)

        handlers = {
            "/brands/delete/": handle_delete,
            "/brands/edit/": handle_edit,
        }

        for prefix, handler in handlers.items():
            if route.startswith(prefix):
                param = route[len(prefix) :]
                if param.endswith("/"):
                    param = param[:-1]
                if not param and prefix != "/brands/create/":
                    return False
                try:
                    handler(param)
                except Exception as ex:
                    self.show_validate_error_dialog([str(ex)])
                return True
        return False

    def sale_handle_dynamic_route(self, route: str) -> bool:
        handlers: Dict[str, Callable[[str], None]] = {}

        def handle_view(sid: str) -> None:
            content = sale_detail_view(int(sid), self.page)
            self._push_view(route, f"Detalle venta #{sid}", content)

        def handle_edit(sid: str) -> None:
            content = edit_sale_view(int(sid), self.page)
            self._push_view(route, f"Editar venta #{sid}", content)

        def handle_delete(sid: str) -> None:
            self._push_view("/sales", "Ventas", self._sales_list_view())
            delete_sale_dialog(
                self.page, int(sid), on_deleted=lambda: self.page.go("/sales")
            )

        handlers = {
            "/sales/delete/": handle_delete,
            "/sales/view/": handle_view,
            "/sales/edit/": handle_edit,
        }

        for prefix, handler in handlers.items():
            if route.startswith(prefix):
                param = route[len(prefix) :]
                if param.endswith("/"):
                    param = param[:-1]
                if not param and prefix not in ("/sales/create/", "/sales/pos/"):
                    return False
                try:
                    handler(param)
                except Exception as ex:
                    self.show_validate_error_dialog([str(ex)])
                return True
        return False

    def _user_handle_dynamic_route(self, route: str) -> bool:
        handlers: Dict[str, Callable[[str], None]] = {}

        def handle_delete(uid: str) -> None:
            self._push_view("/users", "Usuarios", self._users_list_view())
            delete_user_dialog(
                self.page, int(uid), on_deleted=lambda: self.page.go("/users")
            )

        def handle_edit(uid: str) -> None:
            content = edit_user_view(int(uid), self.page)
            self._push_view(route, f"Editar usuario #{uid}", content)

        handlers = {
            "/users/delete/": handle_delete,
            "/users/edit/": handle_edit,
        }

        for prefix, handler in handlers.items():
            if route.startswith(prefix):
                param = route[len(prefix) :]
                if param.endswith("/"):
                    param = param[:-1]
                if not param and prefix != "/users/create/":
                    return False
                try:
                    handler(param)
                except Exception as ex:
                    self.show_validate_error_dialog([str(ex)])
                return True
        return False

    def _home_view(self) -> ft.Container:
        return product_registrations_view(self.page)

    def _quick_card(self, title: str, icon: str, route: str) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=40, color=ft.Colors.BLUE_600),
                    ft.Text(title, weight=ft.FontWeight.W_500),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=6,
            ),
            width=160,
            height=120,
            border_radius=10,
            border=ft.border.all(2, ft.Colors.BLUE_200),
            bgcolor=ft.Colors.WHITE,
            padding=ft.Padding(12, 12, 12, 12),
            ink=True,
            on_click=lambda e: self.navigate_to(route),
        )

    def _products_list_view(self) -> ft.Container:
        return product_registrations_view(self.page)

    def _users_list_view(self) -> ft.Container:
        return user_registrations_view(self.page)

    def _create_user_view(self) -> ft.Container:
        return add_user_view(self.page)

    def _create_product_view(self) -> ft.Container:
        return menu_create_product_view(self.page)

    def _edit_product_stock_view(self) -> ft.Container:
        return edit_product_stock_view(self.page)

    def _categories_list_view(self) -> ft.Container:
        return category_registrations_view(self.page)

    def _create_category_view(self) -> ft.Container:
        return add_category_view(self.page)

    def _brands_list_view(self) -> ft.Container:
        return brand_registrations_view(self.page)

    def _create_brand_view(self) -> ft.Container:
        return add_brand_view(self.page)

    def _pos_view(self) -> ft.Container:
        user_data = self.page.session.get("user_inv")
        uid = None
        if user_data:
            uid = (
                getattr(user_data, "user_inv_id", None)
                if not isinstance(user_data, dict)
                else user_data.get("user_inv_id")
            )
        return pos_view(self.page, user_inv_id=uid)

    def _sales_list_view(self) -> ft.Container:
        return sale_registrations_view(self.page)

    def _login_view(self) -> ft.Container:
        return login_view(self.page)

    def _register_view(self) -> ft.Container:
        return register_view(self.page)

    def show_validate_error_dialog(self, errors: list[str]):
        error_msg = "\n".join(errors)
        error_dialog(self.page, error_msg)
