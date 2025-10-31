import flet as ft
from typing import Callable, Optional

def define_menu_bar(on_route_change: Callable[[str], None], on_toggle: Optional[Callable[[], None]] = None) -> ft.Container:
    def create_menu_item(icon: str, text: str, route: str) -> ft.ListTile:
        return ft.ListTile(
            leading=ft.Icon(icon),
            title=ft.Text(text),
            on_click=lambda e: on_route_change(route)
        )
    
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
                
                ft.ExpansionTile(
                    title=ft.Text("Productos", weight=ft.FontWeight.W_500),
                    leading=ft.Icon(ft.Icons.SHOPPING_BAG),
                    controls=[
                        create_menu_item(ft.Icons.ADD, "Crear producto", "/products/create"),
                    ],
                    initially_expanded=False
                ),
                
                ft.ExpansionTile(
                    title=ft.Text("Categorías", weight=ft.FontWeight.W_500),
                    leading=ft.Icon(ft.Icons.CATEGORY),
                    controls=[
                        create_menu_item(ft.Icons.ADD, "Crear categoría", "/categories/create"),
                        create_menu_item(ft.Icons.LIST, "Ver categorías", "/categories"),
                    ],
                    initially_expanded=False
                ),
                
                ft.ExpansionTile(
                    title=ft.Text("Marcas", weight=ft.FontWeight.W_500),
                    leading=ft.Icon(ft.Icons.BRANDING_WATERMARK),
                    controls=[
                        create_menu_item(ft.Icons.ADD, "Crear marca", "/brands/create"),
                        create_menu_item(ft.Icons.LIST, "Ver marcas", "/brands"),
                    ],
                    initially_expanded=False
                ),
            ]
        )
    )