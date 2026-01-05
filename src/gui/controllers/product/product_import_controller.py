import flet as ft
from gui.components.steps.product_import.product_import_step import ProductImportStep
from gui.components.steps.product_import.product_summary_step import ProductSummaryStep
from gui.components.steps.product_import.category_summary_step import CategorySummaryStep
from gui.components.steps.product_import.brand_summary_step import BrandSummaryStep
from gui.components.steps.step_navigation import StepNavigator

class ProductImportController:
    def __init__(self, page: ft.Page):
        self.page = page
        self.import_step = ProductImportStep(page=self.page)
        self.p_summary_step = ProductSummaryStep([], None, parent=self)
        self.c_summary_step = CategorySummaryStep([], None)
        self.b_summary_step = BrandSummaryStep([], None)
        self.steps = [self.import_step, self.p_summary_step, self.c_summary_step, self.b_summary_step]
        self.navigator = StepNavigator(self.steps, self.on_step_change)
        self.import_step.on_import_finished = self.advance_stepper
        self.progress_bar = ft.ProgressBar(value=0, color=ft.Colors.BLUE_600)
        self.step_indicators = ft.Column(spacing=20, expand=False)
        self.content_container = ft.Column(expand=True)
        # Propagar referencia al padre a los steps de resumen
        self.p_summary_step.parent = self
        self.c_summary_step.parent = self
        self.b_summary_step.parent = self

    def advance_stepper(self):
        # Avanzar al siguiente paso usando el mismo StepNavigator
        self.navigator.next_step()
        # Refrescar indicadores, contenido y barra de progreso
        self.update_step_indicators()
        self.update_content()
        self.update_progress()
        self.page.update()

    def on_step_change(self, step_index):
        print(f"[DEBUG] on_step_change llamado con step_index={step_index}")
        print(f"[DEBUG] selected_file: {getattr(self.import_step, 'selected_file', None)}")
        print(f"[DEBUG] products: {getattr(self.import_step, 'products', None)}")
        print(f"[DEBUG] import_error: {getattr(self.import_step, 'import_error', None)}")

        if step_index in (1, 2, 3):
            if self.import_step.selected_file and (self.import_step.products is None or self.import_step.products == []):
                self.import_step.step = 1

            self.p_summary_step.products = self.import_step.products or []
            self.p_summary_step.error = self.import_step.import_error

            if hasattr(self.import_step, "categories") and self.import_step.categories is not None:
                categories = self.import_step.categories
            else:
                raw_categories = []
                for p in (self.import_step.products or []):
                    val = (p.get("category") if isinstance(p, dict) else getattr(p, "category", None))
                    if val is not None:
                        raw_categories.append(val)
                categories = sorted(set(raw_categories))
            self.c_summary_step.categories = categories
            self.c_summary_step.error = self.import_step.import_error

            if hasattr(self.import_step, "brands") and self.import_step.brands is not None:
                brands = self.import_step.brands
            else:
                raw_brands = []
                for p in (self.import_step.products or []):
                    val = (p.get("brand") if isinstance(p, dict) else getattr(p, "brand", None))
                    if val is not None:
                        raw_brands.append(val)
                brands = sorted(set(raw_brands))
            self.b_summary_step.brands = brands
            self.b_summary_step.error = self.import_step.import_error

        self.update_step_indicators()
        self.update_content()
        self.update_progress()
        self.page.update()

    def update_step_indicators(self):
        self.step_indicators.controls.clear()
        for i, step in enumerate(self.steps):
            is_current = i == self.navigator.current_step
            is_completed = i < self.navigator.current_step
            if is_completed:
                color = ft.Colors.GREEN_600
                icon = ft.Icons.CHECK_CIRCLE
            elif is_current:
                color = ft.Colors.BLUE_600
                icon = ft.Icons.RADIO_BUTTON_CHECKED
            else:
                color = ft.Colors.GREY_400
                icon = ft.Icons.RADIO_BUTTON_UNCHECKED
            step_indicator = ft.Container(
                content=ft.Row([
                    ft.Icon(icon, color=color, size=20),
                    ft.Text(
                        f"{i+1}. {step.title}",
                        size=12 if not is_current else 14,
                        weight=ft.FontWeight.BOLD if is_current else ft.FontWeight.NORMAL,
                        color=color
                    )
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.Padding(10, 8, 10, 8),
                border_radius=8,
                bgcolor=ft.Colors.ON_SURFACE_VARIANT if is_current else None
            )
            self.step_indicators.controls.append(step_indicator)
        if self.step_indicators.page is not None:
            self.step_indicators.update()

    def update_content(self):
        self.content_container.controls.clear()
        current_step = self.navigator.get_current_step()
        controls = current_step.create_controls({'parent': self})
        self.content_container.controls.extend(controls)

        # Reconstruir los botones de navegación en cada actualización
        btn_prev = ft.ElevatedButton(
            "Anterior",
            icon=ft.Icons.ARROW_BACK,
            on_click=lambda e: self.navigator.prev_step(),
            disabled=self.navigator.is_first_step(),
        )
        btn_next = ft.ElevatedButton(
            "Siguiente" if not self.navigator.is_last_step() else "Finalizar",
            icon=ft.Icons.ARROW_FORWARD if not self.navigator.is_last_step() else ft.Icons.CHECK,
            on_click=lambda e: self.navigator.next_step() if not self.navigator.is_last_step() else self.navigator.reset(),
            disabled=(not self.navigator.is_last_step() and not (self.import_step.selected_file or self.import_step.products or self.import_step.import_error)),
        )
        nav_buttons = ft.Row([btn_prev, btn_next], alignment=ft.MainAxisAlignment.CENTER)

        self.content_container.controls.append(ft.Divider(height=20))
        self.content_container.controls.append(nav_buttons)

        if self.content_container.page is not None:
            self.content_container.update()

    def update_progress(self):
        progress = self.navigator.get_progress_percentage() / 100
        self.progress_bar.value = progress
        if self.progress_bar.page is not None:
            self.progress_bar.update()

    def create_layout(self) -> ft.Container:
        main_content = ft.Row(
            [
                ft.Container(
                    content=ft.Column([
                        ft.Text("Progreso", size=16, weight=ft.FontWeight.BOLD),
                        self.progress_bar,
                        ft.Divider(height=20),
                        self.step_indicators
                    ]),
                    width=300,
                    padding=ft.Padding(20, 20, 20, 20),
                    border_radius=10
                ),
                ft.VerticalDivider(width=1),
                ft.Container(
                    content=ft.Column([
                        self.content_container
                    ]),
                    expand=True,
                    padding=ft.Padding(20, 20, 20, 20)
                )
            ],
            expand=True,
            alignment=ft.MainAxisAlignment.START
        )
        self.update_step_indicators()
        self.update_content()
        self.update_progress()
        return ft.Container(
            content=main_content,
            expand=True,
            padding=ft.Padding(20, 20, 20, 20)
        )