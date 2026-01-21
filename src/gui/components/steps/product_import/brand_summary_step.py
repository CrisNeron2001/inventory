import flet as ft
from typing import Optional, Dict, Any, List, Tuple, cast

class BrandSummaryStep:
	def __init__(self, brands, error: str, page: ft.Page):
		self.title = "Resumen de marca"
		self.brands = brands
		self.error = error
		self.page_size = 5
		self.current_page = 0
		self.parent: Optional[Any] = None
		self.page = page

	def create_controls(self, context: Optional[Dict[str, Any]] = None) -> List[ft.Control]:
		if context is not None and 'parent' in context:
			self.parent = context['parent']
		controls = [
			ft.Text(self.title, size=18, weight=ft.FontWeight.BOLD),
			ft.Divider(height=20),
		]
		if self.error:
			controls.append(ft.Text(f"Error al importar marcas: {self.error}", color=ft.Colors.RED_400))
		else:
			controls.append(ft.Text(f"Marcas importadas: {len(self.brands)}", color=ft.Colors.GREEN_400))
			controls.append(self.create_table(self.brands, "Marcas"))

		total_pages = max(1, (len(self.brands) + self.page_size - 1) // self.page_size)
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
		return cast(List[ft.Control], [ft.Container(ft.Column(controls), expand=True)])
	
	def create_table(self, items, title):
		if not items:
			return ft.Text(f"No se encontraron datos de {title.lower()}.")
		columns = [("name", "Nombre")]
		headers = [ft.DataColumn(ft.Text(col_es, size=12)) for _, col_es in columns]

		start = self.current_page * self.page_size
		end = start + self.page_size
		page_items = items[start:end]
		rows = []
		for item in page_items:
			value = str(item)
			row_cells = [ft.DataCell(ft.Text(value, size=12))]
			rows.append(ft.DataRow(cells=row_cells))
		return ft.Container(
			content=ft.DataTable(
				columns=headers,
				rows=rows,
				heading_row_height=28,
				data_row_min_height=24,
				width=400,
				horizontal_lines=ft.BorderSide(1, ft.Colors.GREY_700),
				vertical_lines=ft.BorderSide(1, ft.Colors.GREY_700),
			),
			expand=False,
			width=420,
			height=220,
			padding=ft.Padding(0,0,0,0),
			border_radius=8,
			margin=ft.Margin(0,0,0,0),
		)

	def change_page(self, delta):
		total_pages = max(1, (len(self.brands) + self.page_size - 1) // self.page_size)
		self.current_page = max(0, min(self.current_page + delta, total_pages - 1))
		if hasattr(self, 'parent') and self.parent:
			self.parent.update_content()
			if hasattr(self.parent, 'page') and self.parent.page:
				self.parent.page.update()
	
	def get_data(self) -> Dict[str, Any]:
		return {
			'brands': self.brands,
			'error': self.error
		}
	
	def validate(self) -> Tuple[bool, List[str]]:
		return True, []
	
	def reset(self) -> None:
		self.brands = []
		self.error = None