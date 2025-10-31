import flet as ft
from services.product_service import ProductService


def product_detail_view(product_id: int) -> ft.Container:
    svc = ProductService()
    product = svc.get_product_by_id(product_id)

    if not product:
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.SEARCH_OFF, size=52, color=ft.Colors.GREY),
                ft.Text("Producto no encontrado", size=20, weight=ft.FontWeight.BOLD),
            ], alignment=ft.MainAxisAlignment.CENTER),
            expand=True,
        )

    name = getattr(product, "name", "N/A")
    description = getattr(product, "description", "N/A")
    quantity = getattr(product, "quantity", 0)
    price = getattr(product, "price", 0)
    sku = getattr(product, "sku", "N/A")
    is_available = getattr(product, "is_available", False)
    category = getattr(product, "category", None)
    brand = getattr(product, "brand", None)

    def info_row(label: str, value: str) -> ft.Row:
        return ft.Row([
            ft.Text(label + ":", weight=ft.FontWeight.W_500, expand=1),
            ft.Text(value, expand=2),
        ])

    return ft.Container(
        content=ft.Column([
            ft.Text(f"Detalle de producto: {name}", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            info_row("Descripción", str(description)),
            info_row("Cantidad", str(quantity)),
            info_row("Precio", f"${price}"),
            info_row("SKU", str(sku)),
            info_row("Disponible", "Sí" if is_available else "No"),
            info_row("Categoría", str(getattr(category, 'name', category) or "N/A")),
            info_row("Marca", str(getattr(brand, 'name', brand) or "N/A")),
        ]),
        padding=ft.Padding(16, 16, 16, 16),
        expand=True,
    )
