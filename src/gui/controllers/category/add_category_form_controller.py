from gui.components.form.category_form import CategoryForm
from gui.validators.name_field_validator import NameFieldValidator
from services.category_service import CategoryService
from config.settings import log
from core.models.dto.category_dto import CategoryDTO
from utils.helpers import autoincrement_id
from gui.components.dialog.validate.success.success_dialog import success_dialog
from gui.components.dialog.validate.error.error_dialog import error_dialog
import flet as ft

class AddCategoryFormController:
    def __init__(self, page: ft.Page):
        self.category_service = CategoryService()
        self.category_form = CategoryForm(self.on_submit)
        self.validator = NameFieldValidator()
        self.form_data: dict = {}
        self.page = page
    
    def on_submit(self, form_data: dict):
        is_valid, errors = self.validator.validate_name_field(form_data)
        
        if not is_valid:
            log.error(f"[AddCategoryFormController.on_submit] Error al validar el formulario: {errors}")
            self.show_validate_error_dialog(errors)
            return
        
        category_dto = CategoryDTO(
			category_id=autoincrement_id(),
			name=form_data["name"]
		)
        
        category_added = self.category_service.create_category(category_dto)
        if category_added:
              log.info(f"[AddCategoryFormController.on_submit] Categoria creada: {getattr(category_added, 'name', '')}.")
              self.show_success_dialog(f"Categoria creada: {getattr(category_added, 'name', '')}.")
              return category_added
        else:
            log.error("[AddCategoryFormController.on_submit] No se pudo crear la categoría. Intente nuevamente.")
            return self.show_validate_error_dialog(["No se pudo crear una nueva categoría. Intente nuevamente."])
        
    def create_form_layout(self) -> ft.Container:
        form_controls = self.category_form.create_controls(self.form_data)
        main_content = ft.Row([
            ft.Container(
                content=ft.Column(form_controls),
                    width=300,
                    padding=ft.Padding(20, 20, 20, 20),
                    border_radius=10,
            )
        ], alignment=ft.MainAxisAlignment.START
        )
        return ft.Container(
			content=main_content,
			padding=ft.Padding(20, 20, 20, 20),
		)
    
    def show_error_dialog(self, errors: list[str]):
        error_msg = "\n".join(errors)
        error_dialog(self.page, error_msg, on_close=lambda: self.page.go("/categories"))
        
    def show_validate_error_dialog(self, errors: list[str]):
        error_msg = "\n".join(errors)
        error_dialog(self.page, error_msg) 
        
    def show_success_dialog(self, msg: str):
        success_dialog(self.page, msg, on_close=lambda: self.page.go("/categories"))