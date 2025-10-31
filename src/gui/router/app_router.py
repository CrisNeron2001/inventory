#flet
import flet as ft

#typings
from typing import Callable, Dict, Any, cast

#menu
from gui.components.menu.menu import define_menu_bar

#add
from gui.views.product.add_product_view import add_product_view
from gui.views.category.add_category_view import add_category_view
from gui.views.brand.add_brand_view import add_brand_view

#edit
from gui.views.product.edit_product_view import edit_product_view
from gui.views.category.edit_category_view import edit_category_view
from gui.views.brand.edit_brand_view import edit_brand_view

#detail view
from gui.views.product.product_detail_view import product_detail_view

#table registrations
from gui.views.product.product_registrations_view import product_registrations_view
from gui.views.category.category_registrations_view import category_registrations_view
from gui.views.brand.brand_registrations_view import brand_registrations_view

#delete dialog
from gui.components.dialog.product.delete_product_dialog import delete_product_dialog
from gui.components.dialog.category.delete_category_dialog import delete_category_dialog
from gui.components.dialog.brand.delete_brand_dialog import delete_brand_dialog


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
            "/products/create": {"title": "Crear producto", "view": self._create_product_view},
            "/categories": {"title": "Categorías", "view": self._categories_list_view},
            "/categories/create": {"title": "Crear categoría", "view": self._create_category_view},
            "/brands": {"title": "Marcas", "view": self._brands_list_view},
            "/brands/create": {"title": "Crear marca", "view": self._create_brand_view},
        }

    def start(self) -> None:
        self.page.go(self.page.route or "/")

    def navigate_to(self, route: str) -> None:
        self.page.go(route)

    def _route_change(self, _: ft.RouteChangeEvent) -> None:
        route = self.page.route
        self.page.views.clear()
        self._add_base_view(route)

        if (
            self.product_handle_dynamic_route(route)
            or self.category_handle_dynamic_route(route)
            or self.brand_handle_dynamic_route(route)
        ):
            self.page.update()
            return

        if route in self.routes and route != "/":
            self._push_view(route, self.routes[route]["title"], self.routes[route]["view"]())

        self.page.update()

    def _view_pop(self, _: ft.ViewPopEvent) -> None:
        self.page.views.pop()
        top = self.page.views[-1]
        self.page.go(str(top.route))

    def _build_layout(self, content: ft.Control) -> ft.Row:
        menu_panel = define_menu_bar(self.navigate_to, self._toggle_sidebar)
        self._sidebar_container = ft.Container(
            content=menu_panel,
            width=280 if self._sidebar_open else 0,
            opacity=1.0 if self._sidebar_open else 0.0,
            animate=ft.Animation(250, ft.AnimationCurve.EASE_IN_OUT),
            animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
        )
        return ft.Row([
            self._sidebar_container,
            ft.VerticalDivider(width=1),
            content,
        ], expand=True)

    def _create_menu_button(self) -> ft.IconButton:
        self._menu_toggle_btn = ft.IconButton(
            icon=ft.Icons.CLOSE if self._sidebar_open else ft.Icons.MENU,
            tooltip="Mostrar/ocultar menú",
            on_click=self._toggle_sidebar,
        )
        return self._menu_toggle_btn

    def _add_base_view(self, current_route: str) -> None:
        content = self._home_view() if current_route == "/" else ft.Container(expand=True)
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
            self._menu_toggle_btn.icon = ft.Icons.CLOSE if self._sidebar_open else ft.Icons.MENU
        self.page.update()

    def _push_view(self, route: str, title: str, content: ft.Control) -> None:
        layout = self._build_layout(content)
        self.page.views.append(
            ft.View(
                route=route,
                controls=[
                    ft.AppBar(
                        title=ft.Text(title),
                        bgcolor=ft.Colors.SURFACE,
                        leading=self._create_menu_button(),
                    ),
                    layout,
                ],
                padding=0,
            )
        )

    def product_handle_dynamic_route(self, route: str) -> bool:
        handlers: Dict[str, Callable[[str], None]] = {}
        
        def handle_delete(pid: str) -> None:
            self._push_view("/products", "Productos", self._products_list_view())
            delete_product_dialog(self.page, int(pid), on_deleted=lambda: self.page.go("/products"))
            
        def handle_view(pid: str) -> None:
            content = product_detail_view(int(pid))
            self._push_view(route, f"Detalle producto #{pid}", content)
            
        def handle_edit(pid: str) -> None:
            content = edit_product_view(int(pid), on_saved=lambda: self.page.go("/products"))
            self._push_view(route, f"Editar producto #{pid}", content)
            
        handlers = {
			"/products/delete/": handle_delete,
			"/products/view/": handle_view,
			"/products/edit/": handle_edit,
		}
        
        for prefix, handler in handlers.items():
            if route.startswith(prefix):
                pid = route.split("/")[-1]
                try:
                    handler(pid)
                except Exception as ex:
                    cast(Any, self.page).snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"), open=True)
                return True
        return False

    def category_handle_dynamic_route(self, route: str) -> bool:
        handlers: Dict[str, Callable[[str], None]] = {}

        def handle_delete(cid: str) -> None:
            self._push_view("/categories", "Categorías", self._categories_list_view())
            delete_category_dialog(self.page, int(cid), on_deleted=lambda: self.page.go("/categories"))

        def handle_edit(cid: str) -> None:
            content = edit_category_view(int(cid))
            self._push_view(route, f"Editar categoría #{cid}", content)

        handlers = {
            "/categories/delete/": handle_delete,
            "/categories/edit/": handle_edit,
        }

        for prefix, handler in handlers.items():
            if route.startswith(prefix):
                cid = route.split("/")[-1]
                try:
                    handler(cid)
                except Exception as ex:
                    cast(Any, self.page).snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"), open=True)
                return True
        return False

    def brand_handle_dynamic_route(self, route: str) -> bool:
        handlers: Dict[str, Callable[[str], None]] = {}

        def handle_delete(bid: str) -> None:
            self._push_view("/brands", "Marcas", self._brands_list_view())
            delete_brand_dialog(self.page, int(bid), on_deleted=lambda: self.page.go("/brands"))

        def handle_edit(bid: str) -> None:
            content = edit_brand_view(int(bid), on_saved=lambda: self.page.go("/brands"))
            self._push_view(route, f"Editar marca #{bid}", content)

        handlers = {
            "/brands/delete/": handle_delete,
            "/brands/edit/": handle_edit,
        }

        for prefix, handler in handlers.items():
            if route.startswith(prefix):
                bid = route.split("/")[-1]
                try:
                    handler(bid)
                except Exception as ex:
                    cast(Any, self.page).snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"), open=True)
                return True
        return False

    def _home_view(self) -> ft.Container:
        return product_registrations_view(self.navigate_to)

    def _quick_card(self, title: str, icon: str, route: str) -> ft.Container:
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, size=40, color=ft.Colors.BLUE_600),
                ft.Text(title, weight=ft.FontWeight.W_500),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=6),
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
        return product_registrations_view(self.navigate_to)

    def _create_product_view(self) -> ft.Container:
        return add_product_view()

    def _categories_list_view(self) -> ft.Container:
        return category_registrations_view(self.navigate_to)

    def _create_category_view(self) -> ft.Container:
        return add_category_view()

    def _brands_list_view(self) -> ft.Container:
        return brand_registrations_view(self.navigate_to)

    def _create_brand_view(self) -> ft.Container:
        return add_brand_view()