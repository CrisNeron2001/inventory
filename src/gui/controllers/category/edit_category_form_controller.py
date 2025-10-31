from gui.components.form.category_form import CategoryForm
from gui.validators.name_field_validator import NameFieldValidator
from services.category_service import CategoryService
from config.settings import log
from typing import cast
from core.models.dto.category_dto import CategoryDTO
import flet as ft

class EditCategoryFormController:
    def __init__(self, category_id: int):
        self.category_service = CategoryService()
        self.category_form = CategoryForm(self.on_submit)
        self.validator = NameFieldValidator()
        self.form_data: dict = {}
        self.category_id = category_id
        try:
            category = self.category_service.get_category_by_id(category_id)
            if category:
                self.form_data = {"name": getattr(category, "name", "")}
        except Exception as e:
            log.error(f"No se pudo cargar la categoría {category_id}: {e}")
    
    def on_submit(self, form_data: dict):
        is_valid, errors = self.validator.validate_name_field(form_data)
        
        if not is_valid:
            log.error(f"Error al validar el formulario: {errors}")
            return
        
        try:
            category_dto = CategoryDTO(
				self.category_id,
				name=form_data["name"]
			)
            
            category_edited = self.category_service.update_category(category_dto)
            log.info(f"Categoria editada: {category_edited}")
            return category_edited
        
        except Exception as e:
            return log.error(f"Hubo un error inesperado: {e}")
        
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