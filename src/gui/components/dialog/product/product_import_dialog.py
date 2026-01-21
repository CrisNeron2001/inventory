
import flet as ft
from typing import Optional, Callable
from services.product_import_service import load_products_from_file
import asyncio

def product_import_dialog(page: ft.Page, file_picker: Optional[ft.FilePicker] = None, on_import_finished: Optional[Callable] = None) -> None:
	selected_file: Optional[str] = None
	products = []
	categories = []
	brands = []
	import_error = None

	alert_dialog = ft.CupertinoAlertDialog(
		title=ft.Text("Importar producto"),
		content=ft.Text("Selecciona un archivo .xlsx o .csv para importar."),
		actions=[
			ft.ElevatedButton(
				icon=ft.Icons.UPLOAD_FILE,
				text="Seleccionar archivo",
				on_click=lambda e: pick_file(e)
			),
			ft.TextButton(
				text="Cancelar",
				on_click=lambda e: dismiss_dialog(e)
			)
		]
	)

	loading_dialog = ft.CupertinoAlertDialog(
		title=ft.Text("Normalizando"),
		content=ft.Row([
			ft.ProgressRing(),
			ft.Text("Cargando...", size=14)
		], alignment=ft.MainAxisAlignment.CENTER),
		actions=[]
	)

	def dismiss_dialog(e: ft.ControlEvent):
		alert_dialog.open = False
		page.update()

	def pick_file(e: ft.ControlEvent):
		nonlocal file_picker
		if not file_picker:
			file_picker = ft.FilePicker()
			file_picker.on_result = on_file_picked

		async def do_pick():
			await asyncio.sleep(0.1)
			if file_picker is not None:
				file_picker.pick_files(allowed_extensions=["csv", "xlsx"])

		if file_picker is None:
			return

		if file_picker not in page.overlay:
			page.overlay.append(file_picker)
			page.update()
			page.run_task(do_pick)
		else:
			file_picker.pick_files(allowed_extensions=["csv", "xlsx"])

	def on_file_picked(e: ft.FilePickerResultEvent):
		nonlocal selected_file, products, categories, brands, import_error
		if e.files:
			selected_file = e.files[0].path
			alert_dialog.open = False
			page.overlay.append(loading_dialog)
			loading_dialog.open = True
			page.update()
			async def do_import():
				await asyncio.sleep(0.1)
				import_data(load_products_from_file)
			page.run_task(do_import)

	def import_data(import_func):
		nonlocal products, categories, brands, import_error
		if not selected_file:
			import_error = "No se seleccionó ningún archivo."
			products = []
			categories = []
			brands = []
			show_result_dialog(success=False, message=import_error)
			if on_import_finished:
				on_import_finished(products, categories, brands, import_error)
			return
		try:
			result = import_func(selected_file)
			products = [p for p in result if p]
			categories_set = set()
			brands_set = set()
			for p in products:
				cat_obj = (p.get("category") if isinstance(p, dict) else getattr(p, "category", None))
				if cat_obj is not None:
					if isinstance(cat_obj, dict):
						name = str(cat_obj.get("name", "")).strip()
					else:
						name = str(getattr(cat_obj, "name", cat_obj)).strip()
					if name:
						categories_set.add(name)
				brand_obj = (p.get("brand") if isinstance(p, dict) else getattr(p, "brand", None))
				if brand_obj is not None:
					if isinstance(brand_obj, dict):
						bname = str(brand_obj.get("name", "")).strip()
					else:
						bname = str(getattr(brand_obj, "name", brand_obj)).strip()
					if bname:
						brands_set.add(bname)
			categories = sorted(categories_set)
			brands = sorted(brands_set)
			import_error = None
			show_result_dialog(success=True, message=f"Se importaron {len(products)} productos, {len(categories)} categorías y {len(brands)} marcas correctamente.")
			if on_import_finished:
				on_import_finished(products, categories, brands, import_error)
		except Exception as ex:
			import_error = str(ex)
			products = []
			categories = []
			brands = []
			show_result_dialog(success=False, message=f"Error al importar: {import_error}")
			if on_import_finished:
				on_import_finished(products, categories, brands, import_error)

	def show_result_dialog(success: bool, message: str):
		loading_dialog.open = False
		result_dialog = ft.CupertinoAlertDialog(
			title=ft.Text("Importación exitosa" if success else "Error de importación", color=ft.Colors.GREEN_400 if success else ft.Colors.RED_400),
			content=ft.Text(message, size=15),
			actions=[
				ft.TextButton(
					text="Cerrar",
					on_click=lambda e: close_result_dialog(e)
				)
			]
		)
		page.overlay.append(result_dialog)
		result_dialog.open = True
		page.update()

	def close_result_dialog(e):
		for dlg in list(page.overlay):
			if isinstance(dlg, ft.CupertinoAlertDialog):
				dlg.open = False
		page.update()

	if page:
		page.overlay.append(alert_dialog)
		alert_dialog.open = True
		page.update()