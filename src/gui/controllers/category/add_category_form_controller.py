from gui.components.form.category_form import CategoryForm
from gui.validators.name_field_validator import NameFieldValidator
from services.category_service import CategoryService
from config.settings import log
from typing import cast
from core.models.dto.category_dto import CategoryDTO
from utils.helpers import autoincrement_id
import flet as ft

class AddCategoryFormController:
    def __init__(self):
        self.category_service = CategoryService()
        self.category_form = CategoryForm(self.on_submit)
        self.validator = NameFieldValidator()
        self.form_data: dict = {}
    
    def on_submit(self, form_data: dict):
        is_valid, errors = self.validator.validate_name_field(form_data)
        
        if not is_valid:
            log.error(f"Error al validar el formulario: {errors}")
            return
        
        try:
            category_dto = CategoryDTO(
				category_id=autoincrement_id(),
				name=form_data["name"]
			)
            
            category_added = self.category_service.create_category(category_dto)
            log.info(f"Nueva categoria creada: {category_added}")
            return category_added
        
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