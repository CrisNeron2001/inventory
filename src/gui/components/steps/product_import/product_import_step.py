import flet as ft
from typing import Optional
from gui.components.dialog.product.product_import_dialog import product_import_dialog

class ProductImportStep:
    def __init__(self, file_picker=None, on_import_finished=None, page=None):
        self.title = "Cargar datos productos"
        self.selected_file: Optional[str] = None
        self.products = []
        self.categories = []
        self.brands = []
        self.import_error = None
        self.step = 0
        self.file_picker = file_picker
        self.on_import_finished = on_import_finished
        self.page = page
        self.dialog_data = None

    def create_controls(self, form_data: Optional[dict] = None) -> list[ft.Control]:
        if self.step == 0:
            def on_import_finished(products, categories, brands, import_error):
                self.products = products
                self.categories = categories
                self.brands = brands
                self.import_error = import_error
                self.selected_file = None if import_error else (products[0].get('file') if products and isinstance(products[0], dict) and 'file' in products[0] else None)
                self.step = 1
                if self.page:
                    self.page.update()
                if self.on_import_finished:
                    self.on_import_finished()

            def open_dialog(e):
                if self.page is None:
                    return
                product_import_dialog(
                    page=self.page,
                    file_picker=self.file_picker,
                    on_import_finished=on_import_finished
                )

            controls = [
                ft.Text(self.title, size=18, weight=ft.FontWeight.BOLD),
                ft.Divider(height=20),
                ft.ElevatedButton(
                    text="Selecciona un archivo .xlsx o .csv",
                    icon=ft.Icons.UPLOAD_FILE,
                    on_click=open_dialog
                )
            ]
            if self.selected_file:
                controls.append(ft.Text(f"Archivo seleccionado: {self.selected_file}", color=ft.Colors.GREEN_400, size=14))
            return controls
        elif self.step == 1:
            return self.create_summary_controls()
        return []


    def create_summary_controls(self) -> list[ft.Control]:
        controls = [
            ft.Text("Resumen de importación", size=18, weight=ft.FontWeight.BOLD),
            ft.Divider(height=20),
        ]
        if self.import_error:
            controls.append(ft.Text(f"Error al importar: {self.import_error}", color=ft.Colors.RED_400))
        else:
            controls.append(ft.Text(f"Productos importados: {len(self.products)}", color=ft.Colors.GREEN_400))
            controls.append(self.create_table(self.products, "Productos"))
        controls.append(ft.ElevatedButton(text="Finalizar", icon=ft.Icons.CHECK, on_click=self.finish_step))
        return controls

    def create_table(self, items, title):
        if not items:
            return ft.Text(f"No se encontraron datos de {title.lower()}.")
        columns = ["name", "description", "stock", "price", "sku", "is_available", "category", "brand"]
        headers = [ft.DataColumn(ft.Text(col.capitalize())) for col in columns]
        rows = []
        for item in items:
            if hasattr(item, '__dict__'):
                data = item.__dict__
            else:
                data = item
            row_cells = [ft.DataCell(ft.Text(str(data.get(col, '')))) for col in columns]
            rows.append(ft.DataRow(cells=row_cells))
        return ft.DataTable(columns=headers, rows=rows, heading_row_height=40, data_row_min_height=32, width=900)

    def finish_step(self, e):
        self.step = 0
        self.selected_file = None
        self.products = []
        self.import_error = None

    def get_data(self) -> dict:
        return {
            'products': self.products,
            'categories': self.categories,
            'brands': self.brands,
            'error': self.import_error
        }

    def validate(self) -> tuple[bool, list[str]]:
        return True, []

    def reset(self) -> None:
        self.step = 0
        self.selected_file = None
        self.products = []
        self.import_error = None