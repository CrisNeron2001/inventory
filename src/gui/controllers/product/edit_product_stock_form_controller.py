import flet as ft
from services.product_service import ProductService

class EditProductStockTableController:
    def __init__(self, on_saved=None):
        self.product_service = ProductService()
        self.on_saved = on_saved
        self.page = 1
        self.page_size = 5
        self.search_text = ""
        self.products = []
        self.total_pages = 1
        self.load_products()

    def load_products(self):
        all_products = self.product_service.get_all_products()
        if self.search_text:
            all_products = [p for p in all_products if self.search_text.lower() in p.name.lower()]
        self.total_pages = max(1, (len(all_products) + self.page_size - 1) // self.page_size)
        start = (self.page - 1) * self.page_size
        end = start + self.page_size
        self.products = all_products[start:end]

    def on_search(self, value):
        self.search_text = value
        self.page = 1
        self.load_products()
        self.refresh()

    def on_update(self, product, field, value):
        if field == "stock":
            try:
                product.stock = int(value)
            except Exception:
                return
        elif field == "is_available":
            product.is_available = value == "Disponible"
        self.product_service.update_product(product)
        self.load_products()
        self.refresh()

    def on_prev(self, e):
        if self.page > 1:
            self.page -= 1
            self.load_products()
            self.refresh()

    def on_next(self, e):
        if self.page < self.total_pages:
            self.page += 1
            self.load_products()
            self.refresh()

    def refresh(self):
        if hasattr(self, "container") and self.container:
            self.container.content = self.create_content()
            self.container.update()

    def create_content(self):
        search_field = ft.TextField(
            label="Buscar producto por nombre",
            value=self.search_text,
            on_change=lambda e: self.on_search(e.control.value),
            width=300,
            prefix_icon=ft.Icons.SEARCH
        )

        def make_row(product):
            stock_field = ft.TextField(
                value=str(product.stock),
                width=120,
                text_align=ft.TextAlign.CENTER,
                on_change=lambda e, p=product: self.on_update(p, 'stock', e.control.value)
            )
            avail_field = ft.Dropdown(
                value="Disponible" if product.is_available else "No disponible",
                options=[
                    ft.dropdown.Option("Disponible"),
                    ft.dropdown.Option("No disponible")
                ],
                width=160,
                on_change=lambda e, p=product: self.on_update(p, 'is_available', e.control.value)
            )
            return ft.DataRow(cells=[
                ft.DataCell(ft.Text(product.name, width=320)),
                ft.DataCell(stock_field),
                ft.DataCell(avail_field),
            ])

        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre"), numeric=False, tooltip="Nombre del producto"),
                ft.DataColumn(ft.Text("Stock"), numeric=True, tooltip="Cantidad en stock"),
                ft.DataColumn(ft.Text("Disponibilidad"), numeric=False, tooltip="Estado de disponibilidad"),
            ],
            rows=[make_row(p) for p in self.products],
            column_spacing=32,
            data_row_min_height=48,
            heading_row_height=48,
            width=700,
        )

        paginator = ft.Row([
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                on_click=self.on_prev,
                disabled=self.page <= 1,
                tooltip="Página anterior"
            ),
            ft.Text(f"Página {self.page} de {self.total_pages}"),
            ft.IconButton(
                icon=ft.Icons.ARROW_FORWARD,
                on_click=self.on_next,
                disabled=self.page >= self.total_pages,
                tooltip="Página siguiente"
            ),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)

        return ft.Column([
            search_field,
            ft.Divider(),
            ft.Row([table], alignment=ft.MainAxisAlignment.CENTER),
            paginator
        ], expand=False, tight=True)

    def create_layout(self):
        self.container = ft.Container(content=self.create_content(), padding=0, margin=0, expand=False)
        return self.container