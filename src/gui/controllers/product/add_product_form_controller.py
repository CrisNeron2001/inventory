from gui.components.steps.product.product_basic_data_step import BasicDataStep
from gui.components.steps.product.product_availability_step import AvailabilityStep
from gui.components.steps.product.product_confirmation_step import ConfirmationStep
from services.product_service import ProductService
from gui.validators.product_form_validator import FormProductValidator
from gui.components.steps.step_navigation import StepNavigator
from config.settings import log
from core.models.dto.product_dto import ProductDTO
from core.models.dto.category_dto import CategoryDTO
from core.models.dto.brand_dto import BrandDTO
from utils.helpers import autoincrement_id
from gui.components.dialog.validate.success.success_dialog import success_dialog
from gui.components.dialog.validate.error.error_dialog import error_dialog
from gui.components.dialog.product.sku.sku_conflict_dialog import sku_conflict_dialog
import flet as ft

class AddProductFormController:
    def __init__(self, page: ft.Page):
        self.product_service = ProductService()
        self.validator = FormProductValidator()
        self.form_data: dict = {}
        self.page = page
        
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
        self.update_nav_buttons()
        
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
        errors: list[str] = []
        if not is_valid_basic:
            errors += errors_basic
        if not is_valid_av:
            errors += errors_av
        if errors:
            log.error(f"[AddProductFormController.on_submit] Error de validación: {errors}")
            self.show_validate_error_dialog(errors)
            return
        
        cat_val = form_data.get('category') or form_data.get('category_id')
        brand_val = form_data.get('brand') or form_data.get('brand_id')

        category_dto = None
        if isinstance(cat_val, dict):
            category_id_raw = cat_val.get("category_id")
            try:
                category_id = int(category_id_raw) if category_id_raw not in (None, "") else 0
            except (ValueError, TypeError):
                category_id = 0
            category_dto = CategoryDTO(
                category_id=category_id,
                name=cat_val.get("name", "")
            )

        brand_dto = None
        if isinstance(brand_val, dict):
            brand_id_raw = brand_val.get("brand_id")
            try:
                brand_id = int(brand_id_raw) if brand_id_raw not in (None, "") else 0
            except (ValueError, TypeError):
                brand_id = 0
            brand_dto = BrandDTO(
                brand_id=brand_id,
                name=brand_val.get("name", "")
			)
            
        is_av_val = form_data.get('is_available')
        is_available_bool = (
            is_av_val if isinstance(is_av_val, bool)
            else str(is_av_val).lower().startswith("disponible")
        )

        product_dto = ProductDTO(
			product_id=autoincrement_id(),
			name=form_data['name'],
			description=form_data['description'],
			stock=int(form_data['stock']),
			price=int(form_data['price']),
			sku=form_data['sku'],
			is_available=is_available_bool,
			category=category_dto,
			brand=brand_dto
		)

        product_added = self.product_service.create_product(product_dto)

        if product_added:
            log.info(f"[AddProductFormController.on_submit] Producto creado: {getattr(product_added, 'name', '')}.")
            self.show_success_dialog(f"Producto creado: {getattr(product_added, 'name', '')}.")
        else:
            log.error("[AddProductFormController.on_submit] Error al crear producto (posible SKU duplicado).")
            sku_val = form_data.get("sku", "")
            if sku_val:
                sku_conflict_dialog(self.page, sku_val)
            else:
                log.error("[AddProductFormController.on_submit] No se pudo crear el producto. Intente nuevamente.")
                self.show_validate_error_dialog(["No se pudo crear el producto. Intente nuevamente."])
            
    def show_error_dialog(self, errors: list[str]):
        error_msg = "\n".join(errors)
        error_dialog(self.page, error_msg, on_close=lambda: self.page.go("/"))
        
    def show_validate_error_dialog(self, errors: list[str]):
        error_msg = "\n".join(errors)
        error_dialog(self.page, error_msg) 
        
    def show_success_dialog(self, msg: str):
        success_dialog(self.page, msg, on_close=lambda: self.page.go("/"))
        
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

    def update_nav_buttons(self) -> None:
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
        self.update_nav_buttons()
        
        return ft.Container(
			content=main_content,
			expand=True,
			padding=ft.Padding(20, 20, 20, 20)
		)