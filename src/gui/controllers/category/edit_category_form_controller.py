from gui.components.form.category_form import CategoryForm
from gui.validators.name_field_validator import NameFieldValidator
from services.category_service import CategoryService
from config.settings import log
from typing import cast
from core.models.dto.category_dto import CategoryDTO
from gui.components.dialog.validate.success.success_dialog import success_dialog
from gui.components.dialog.validate.error.error_dialog import error_dialog
import flet as ft

class EditCategoryFormController:
    def __init__(self, page: ft.Page, category_id: int):
        self.category_service = CategoryService()
        self.category_form = CategoryForm(self.on_submit)
        self.validator = NameFieldValidator()
        self.form_data: dict = {}
        self.category_id = category_id
        self.page = page
        
        category = self.category_service.get_category_by_id(category_id)
        category_name = getattr(category, "name", "")
        if category:
                self.form_data = {"name": category_name}
        else:
            log.error(f"No se pudo cargar la categoría {category_name} [editCategoryFormController]")
            self.show_error_dialog([f"No se pudo cargar la categoría {category_name}"])
    
    def on_submit(self, form_data: dict):
        is_valid, errors = self.validator.validate_name_field(form_data)
        
        if not is_valid:
            log.error(f"[EditCategoryFormController.on_submit] Error al validar el formulario: {errors}")
            self.show_validate_error_dialog(errors)
            return
        
        category_dto = CategoryDTO(
			self.category_id,
			name=form_data["name"]
		)
            
        category_edited = self.category_service.update_category(category_dto)
        if category_edited:
            log.info(f"[EditCategoryFormController.on_submit] Categoria editada: {getattr(category_edited, 'name', '')}.")
            self.show_success_dialog(f"Categoria editada: {getattr(category_edited, 'name', '')}.")
            return category_edited
        else:
            log.error("[EditCategoryFormController.on_submit] No se pudo editar la categoría. Intente nuevamente.")
            self.show_validate_error_dialog([f"No se pudo editar la categoría. Intente nuevamente."])
        
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