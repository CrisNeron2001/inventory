from gui.components.steps.product_basic_data_step import BasicDataStep
from gui.components.steps.product_availability_step import AvailabilityStep
from gui.components.steps.product_confirmation_step import ConfirmationStep
from services.product_service import ProductService
from gui.validators.product_form_validator import FormProductValidator
from gui.components.steps.product_step_navigation import StepNavigator
from config.settings import log
from core.models.dto.product_dto import ProductDTO
from core.models.dto.category_dto import CategoryDTO
from core.models.dto.brand_dto import BrandDTO
from utils.helpers import autoincrement_id
import flet as ft

class AddProductFormController:
    def __init__(self):
        self.product_service = ProductService()
        self.validator = FormProductValidator()
        self.form_data: dict = {}
        
        self.steps = [
            BasicDataStep(),
            AvailabilityStep(),
            ConfirmationStep(self.on_submit),
        ]
        
        self.navigator = StepNavigator(self.steps, self.on_step_changed)
        
        self.step_indicators = ft.Column(spacing=20, expand=False)
        self.content_container = ft.Column(expand=True)
        self.progress_bar = ft.ProgressBar(value=0, color=ft.Colors.BLUE_600)
        self.btn_prev = None
        self.btn_next = None
    
    def on_step_changed(self, step_index: int):
        self.update_step_indicators()
        self.update_content()
        self.update_progress()
        self._update_nav_buttons()
        
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
        try:
            if self.step_indicators.page is not None:
                self.step_indicators.update()
        except Exception:
            pass
        
    def update_content(self):
        self.content_container.controls.clear()

        current_step = self.navigator.get_current_step()
        controls = current_step.create_controls(self.form_data)
        
        self.content_container.controls.extend(controls)
        if self.content_container.page is not None:
            self.content_container.update()
        
    def update_progress(self):
        progress = self.navigator.get_progress_percentage() / 100
        self.progress_bar.value = progress
        if self.progress_bar.page is not None:
            self.progress_bar.update()
    
    def on_submit(self, form_data: dict):
        is_valid_basic, errors_basic = self.validator.validate_basic_data(form_data)
        is_valid_av, errors_av = self.validator.validate_availability_data(form_data)
        all_errors: list[str] = []
        if not is_valid_basic:
            all_errors += errors_basic
        if not is_valid_av:
            all_errors += errors_av
        if all_errors:
            log.error(f"Error de validación: {all_errors}")
            self.show_error_dialog(all_errors)
            return
        
        cat_val = form_data.get('category') or form_data.get('category_id')
        brand_val = form_data.get('brand') or form_data.get('brand_id')

        category_dto = None
        if cat_val not in (None, ""):
            try:
                category_dto = CategoryDTO(category_id=int(cat_val), name="")
            except Exception:
                category_dto = None

        brand_dto = None
        if brand_val not in (None, ""):
            try:
                brand_dto = BrandDTO(brand_id=int(brand_val), name="")
            except Exception:
                brand_dto = None

        is_av_val = form_data.get('is_available')
        is_available_bool = (
            is_av_val if isinstance(is_av_val, bool)
            else str(is_av_val).lower().startswith("disponible")
        )

        product_dto = ProductDTO(
			product_id=autoincrement_id(),
			name=form_data['name'],
			description=form_data['description'],
			quantity=int(form_data['quantity']),
			price=int(form_data['price']),
			sku=form_data['sku'],
			is_available=is_available_bool,
			category=category_dto,
			brand=brand_dto
		)

        product_added = self.product_service.create_product(product_dto)

        if product_added:
            log.info("Producto creado")
            self.show_success_dialog()
        else:
            log.error("Error al crear producto")
            self.show_error_dialog(["No se pudo crear el producto. Intente nuevamente."])
            
    def show_error_dialog(self, errors: list[str]):
        error_msg = "\n".join(errors)
        log.error(f"Errores de validación: {error_msg}")
        ft.AlertDialog(title=ft.Text(f"Errores de validación: {error_msg}"))
        
    def show_success_dialog(self):
        log.info("Producto creado con éxito")
        ft.AlertDialog(title=ft.Text(value="Producto creado con éxito"))
        page = getattr(self.content_container, 'page', None) or getattr(self.step_indicators, 'page', None) or getattr(self.progress_bar, 'page', None)
        if page:
            page.go("/")
        
    def reset_form(self):
        self.form_data.clear()
        for step in self.steps:
            step.reset()
        self.navigator.reset()
        self.on_step_changed(0)
            
    def next_step(self, e):
        current_step = self.navigator.get_current_step()
        step_data = current_step.get_data()
        if getattr(current_step, "form_id", "") == "basic_data":
            is_valid, errors = self.validator.validate_basic_data(step_data)
        elif getattr(current_step, "form_id", "") == "availability":
            is_valid, errors = self.validator.validate_availability_data(step_data)
        else:
            is_valid, errors = True, []

        if not is_valid:
            self.show_error_dialog(errors)
            return

        self.form_data.update(step_data)
        self.navigator.next_step()
        
    def prev_step(self, e):
        self.navigator.prev_step()

    def _update_nav_buttons(self) -> None:
        if self.btn_prev is not None:
            self.btn_prev.disabled = self.navigator.is_first_step()
            try:
                if self.btn_prev.page is not None:
                    self.btn_prev.update()
            except Exception:
                pass
        if self.btn_next is not None:
            is_last = self.navigator.is_last_step()
            self.btn_next.text = "Finalizar" if is_last else "Siguiente"
            self.btn_next.icon = ft.Icons.CHECK if is_last else ft.Icons.ARROW_FORWARD
            self.btn_next.on_click = (lambda e: self.on_submit(self.form_data)) if is_last else self.next_step
            if self.btn_next.page is not None:
                self.btn_next.update()
        
    def create_layout(self) -> ft.Container:
        self.btn_prev = ft.ElevatedButton(
            "Anterior",
            icon=ft.Icons.ARROW_BACK,
            on_click=self.prev_step,
            disabled=self.navigator.is_first_step(),
        )
        self.btn_next = ft.ElevatedButton(
            "Siguiente",
            icon=ft.Icons.ARROW_FORWARD,
            on_click=self.next_step,
            disabled=False,
        )
        nav_buttons = ft.Row([self.btn_prev, self.btn_next], alignment=ft.MainAxisAlignment.CENTER)
        
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
						self.content_container,
						ft.Divider(height=20),
						nav_buttons
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
        self._update_nav_buttons()
        
        return ft.Container(
			content=main_content,
			expand=True,
			padding=ft.Padding(20, 20, 20, 20)
		)