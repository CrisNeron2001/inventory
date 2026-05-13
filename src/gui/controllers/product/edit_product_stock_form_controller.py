import flet as ft
from services.product_service import ProductService
from gui.components.form.edit_stock_product_form import EditStockProductForm
from gui.components.dialog.validate.success.success_dialog import success_dialog
from gui.components.dialog.validate.error.error_dialog import error_dialog


class EditProductStockTableController:
    def __init__(self, page: ft.Page):
        self.product_service = ProductService()
        self.page = page
        self.n_page = 1
        self.page_size = 5
        self.search_text = ""
        self.products = []
        self.total_pages = 1
        self.load_products()
        self.selected_product = None
        self.product_form = EditStockProductForm(on_submit=self.on_form_submit)

    def load_products(self):
        all_products = self.product_service.get_all_products()
        if self.search_text:
            all_products = [
                p for p in all_products if self.search_text.lower() in p.name.lower()
            ]
        self.total_pages = max(
            1, (len(all_products) + self.page_size - 1) // self.page_size
        )
        start = (self.n_page - 1) * self.page_size
        end = start + self.page_size
        self.products = all_products[start:end]

    def on_search(self, value):
        self.search_text = value
        self.n_page = 1
        self.load_products()
        self.refresh()

    def on_form_submit(self, data: dict):
        if not self.selected_product:
            return
        try:
            self.selected_product.name = data.get("name", self.selected_product.name)
            self.selected_product.stock = int(data.get("stock") or 0)
            self.selected_product.is_available = (
                data.get("is_available") == "Disponible"
            )
        except Exception as e:
            self.show_validate_error_dialog([f"Hubo un error {str(e)}"])
            return
        self.product_service.update_product(self.selected_product)
        self.show_success_dialog(
            f"Se ha actualizado correctamente el producto: {self.selected_product.name}"
        )
        self.load_products()
        self.refresh()

    def on_select_product(self, product):
        self.selected_product = product
        self.refresh()

    def on_update(self, product, field, value):
        if field == "stock":
            try:
                product.stock = int(value)
            except Exception:
                return

    def on_prev(self, e):
        if self.n_page > 1:
            self.n_page -= 1
            self.load_products()
            self.refresh()

    def on_next(self, e):
        if self.n_page < self.total_pages:
            self.n_page += 1
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
            prefix_icon=ft.Icons.SEARCH,
        )

        def make_row(product):
            return ft.DataRow(
                cells=[
                    ft.DataCell(
                        ft.Text(product.name, width=320),
                        on_tap=lambda e, p=product: self.on_select_product(p),
                    ),
                ]
            )

        table = ft.DataTable(
            columns=[
                ft.DataColumn(
                    ft.Text("Nombre"), numeric=False, tooltip="Nombre del producto"
                ),
            ],
            rows=[make_row(p) for p in self.products],
            column_spacing=32,
            data_row_min_height=48,
            heading_row_height=48,
            width=360,
        )

        paginator = ft.Row(
            [
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=self.on_prev,
                    disabled=self.n_page <= 1,
                    tooltip="Página anterior",
                ),
                ft.Text(f"Página {self.n_page} de {self.total_pages}"),
                ft.IconButton(
                    icon=ft.Icons.ARROW_FORWARD,
                    on_click=self.on_next,
                    disabled=self.n_page >= self.total_pages,
                    tooltip="Página siguiente",
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        )

        form_controls: list[ft.Control] = []
        if self.selected_product is not None:
            form_controls = self.product_form.create_controls(
                {
                    "name": self.selected_product.name,
                    "stock": self.selected_product.stock,
                }
            )

        return ft.Column(
            [
                search_field,
                ft.Divider(),
                ft.Row(
                    [
                        ft.Container(table, expand=True),
                        ft.VerticalDivider(width=1),
                        ft.Container(
                            ft.Column(form_controls, tight=True)
                            if form_controls
                            else ft.Container(),
                            padding=ft.Padding(16, 0, 0, 0),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                ft.Divider(),
                paginator,
            ],
            expand=False,
            tight=True,
        )

    def create_layout(self):
        self.container = ft.Container(
            content=self.create_content(), padding=0, margin=0, expand=False
        )
        return self.container

    def show_validate_error_dialog(self, errors: list[str]):
        error_msg = "\n".join(errors)
        error_dialog(self.page, error_msg)

    def show_success_dialog(self, msg: str):
        success_dialog(self.page, msg)

