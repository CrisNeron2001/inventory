import flet as ft
from typing import Optional, Callable
from services.product_service import ProductService
import asyncio


def product_import_dialog(
    page: ft.Page,
    on_import_finished: Optional[Callable] = None,
) -> None:
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
                on_click=lambda e: pick_file(e),
            ),
            ft.TextButton(text="Cancelar", on_click=lambda e: dismiss_dialog(e)),
        ],
    )

    loading_dialog = ft.CupertinoAlertDialog(
        title=ft.Text("Normalizando"),
        content=ft.Row(
            [ft.ProgressRing(), ft.Text("Procesando Excel...", size=14)],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        actions=[],
    )

    def dismiss_dialog(e: ft.ControlEvent):
        alert_dialog.open = False
        page.update()

    def pick_file(e: ft.ControlEvent):
        alert_dialog.open = False
        page.update()

        file_picker = ft.FilePicker()
        file_picker.on_result = on_file_picked

        if file_picker not in page.overlay:
            page.overlay.append(file_picker)
            page.update()

        file_picker.pick_files(allowed_extensions=["csv", "xlsx"])

    def on_file_picked(e: ft.FilePickerResultEvent):
        nonlocal selected_file
        if e.files:
            selected_file = e.files[0].path

            async def do_import():
                page.overlay.append(loading_dialog)
                loading_dialog.open = True
                page.update()

                await asyncio.sleep(0.2)

                service = ProductService()
                import_data(service.import_products_form_excel)

            page.run_task(do_import)

    def import_data(import_func):
        nonlocal products, categories, brands, import_error
        if not selected_file:
            loading_dialog.open = False
            show_result_dialog(
                success=False, message="No se seleccionó ningún archivo."
            )
            return

        try:
            result = import_func(selected_file)

            products = [p for p in result if p is not None]

            if len(products) == 0:
                loading_dialog.open = False
                show_result_dialog(
                    success=False,
                    message="Error: No se pudieron leer filas válidas del Excel. Revisa las columnas.",
                )
                if on_import_finished:
                    on_import_finished([], [], [], "Estructura inválida")
                return

            categories_set = set()
            brands_set = set()
            for p in products:
                cat_obj = (
                    p.get("category")
                    if isinstance(p, dict)
                    else getattr(p, "category", None)
                )
                if cat_obj is not None:
                    name = str(
                        cat_obj.get("name", "")
                        if isinstance(cat_obj, dict)
                        else getattr(cat_obj, "name", cat_obj)
                    ).strip()
                    if name:
                        categories_set.add(name)

                brand_obj = (
                    p.get("brand") if isinstance(p, dict) else getattr(p, "brand", None)
                )
                if brand_obj is not None:
                    bname = str(
                        brand_obj.get("name", "")
                        if isinstance(brand_obj, dict)
                        else getattr(brand_obj, "name", brand_obj)
                    ).strip()
                    if bname:
                        brands_set.add(bname)

            categories = [
                {"category_id": None, "name": name} for name in sorted(categories_set)
            ]
            brands = [{"brand_id": None, "name": name} for name in sorted(brands_set)]
            import_error = None

            # Ocultamos la rueda de carga antes de mostrar el éxito
            loading_dialog.open = False
            page.update()

            show_result_dialog(
                success=True,
                message=f"Se importaron {len(products)} productos correctamente en invdb.",
            )

        except Exception as ex:
            loading_dialog.open = False
            import_error = str(ex)
            show_result_dialog(
                success=False, message=f"Error crítico al importar: {import_error}"
            )

    def show_result_dialog(success: bool, message: str):
        result_dialog = ft.CupertinoAlertDialog(
            title=ft.Text(
                "Importación exitosa" if success else "Error de importación",
                color=ft.Colors.GREEN_400 if success else ft.Colors.RED_400,
            ),
            content=ft.Text(message, size=15),
            actions=[
                ft.TextButton(
                    text="Continuar", on_click=lambda e: close_result_dialog(e)
                )
            ],
        )
        page.overlay.append(result_dialog)
        result_dialog.open = True
        page.update()

    def close_result_dialog(e):
        page.overlay.clear()
        page.update()
        if on_import_finished:
            on_import_finished(products, categories, brands, import_error)

    if page:
        page.overlay.append(alert_dialog)
        alert_dialog.open = True
        page.update()
