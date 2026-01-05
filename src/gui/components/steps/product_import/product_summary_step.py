import flet as ft
from typing import Optional, Dict, Any, List, Tuple

class ProductSummaryStep:
    def __init__(self, products, error=None, parent: Optional[Any] = None):
        self.title = "Resumen de producto"
        self.products = products
        self.error = error
        self.page_size = 5
        self.current_page = 0
        self.parent = parent

    def create_controls(self, form_data: Optional[Dict[str, Any]] = None) -> List[ft.Control]:
        # Referencia al padre para refrescar la vista al paginar
        if form_data and 'parent' in form_data:
            self.parent = form_data['parent']
        controls = [
            ft.Text(self.title, size=18, weight=ft.FontWeight.BOLD),
            ft.Divider(height=20),
        ]
        if self.error:
            controls.append(ft.Text(f"Error al importar productos: {self.error}", color=ft.Colors.RED_400))
        else:
            controls.append(ft.Text(f"Productos importados: {len(self.products)}", color=ft.Colors.GREEN_400))
            controls.append(self.create_table(self.products, "Productos"))

        total_pages = max(1, (len(self.products) + self.page_size - 1) // self.page_size)
        pag_controls = []
        pag_controls.append(
            ft.ElevatedButton(
                text="Anterior",
                icon=ft.Icons.ARROW_BACK,
                on_click=lambda e: self.change_page(-1),
                disabled=self.current_page == 0
            )
        )
        pag_controls.append(ft.Text(f"Página {self.current_page+1} de {total_pages}", size=12))
        pag_controls.append(
            ft.ElevatedButton(
                text="Siguiente",
                icon=ft.Icons.ARROW_FORWARD,
                on_click=lambda e: self.change_page(1),
                disabled=self.current_page >= total_pages-1
            )
        )
        controls.append(ft.Row(pag_controls, alignment=ft.MainAxisAlignment.CENTER))
        return [ft.Container(ft.Column(controls), expand=True)]

    def create_table(self, items, title):
        if not items:
            return ft.Text(f"No se encontraron datos de {title.lower()}.")

        columns = [
            ("name", "Nombre"),
            ("description", "Descripción"),
            ("stock", "Stock"),
            ("price", "Precio"),
            ("sku", "Código"),
            ("is_available", "Disponible"),
            ("category", "Categoría"),
            ("brand", "Marca")
        ]
        headers = [ft.DataColumn(ft.Text(col_es, size=12)) for _, col_es in columns]
        # Paginación
        start = self.current_page * self.page_size
        end = start + self.page_size
        page_items = items[start:end]
        rows = []
        for item in page_items:
            if hasattr(item, '__dict__'):
                data = item.__dict__
            else:
                data = item
            row_cells = []
            for col, _ in columns:
                val = data.get(col, '')
                # Mostrar nombre si es objeto
                if col == "category" and val:
                    if hasattr(val, 'name'):
                        val = val.name
                    elif isinstance(val, dict):
                        val = val.get('name', '')
                if col == "brand" and val:
                    if hasattr(val, 'name'):
                        val = val.name
                    elif isinstance(val, dict):
                        val = val.get('name', '')
                if col == "is_available":
                    val = "Sí" if val else "No"
                row_cells.append(ft.DataCell(ft.Text(str(val), size=12)))
            rows.append(ft.DataRow(cells=row_cells))
        # Scroll horizontal y vertical, tamaño compacto
        return ft.Container(
            content=ft.DataTable(
                columns=headers,
                rows=rows,
                heading_row_height=28,
                data_row_min_height=24,
                width=800,
                horizontal_lines=ft.BorderSide(1, ft.Colors.GREY_700),
                vertical_lines=ft.BorderSide(1, ft.Colors.GREY_700),
            ),
            expand=False,
            width=820,
            height=340,
            padding=ft.Padding(0,0,0,0),
            border_radius=8,
            margin=ft.Margin(0,0,0,0),
        )

    def change_page(self, delta):
        total_pages = max(1, (len(self.products) + self.page_size - 1) // self.page_size)
        self.current_page = max(0, min(self.current_page + delta, total_pages - 1))
        # Refrescar la vista del padre si existe
        if self.parent:
            self.parent.update_content()
            # Forzar actualización de la página para refrescar botones y controles
            if hasattr(self.parent, 'page') and self.parent.page:
                self.parent.page.update()

    def get_data(self) -> Dict[str, Any]:
        return {
            'products': self.products,
            'error': self.error
        }

    def validate(self) -> Tuple[bool, List[str]]:
        return True, []

    def reset(self) -> None:
        self.products = []
        self.error = None
