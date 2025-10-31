from gui.components.form.brand_form import BrandForm
from gui.validators.name_field_validator import NameFieldValidator
from services.brand_service import BrandService
from config.settings import log
from typing import cast
from core.models.dto.brand_dto import BrandDTO
from utils.helpers import autoincrement_id
import flet as ft

class AddBrandFormController:
    def __init__(self):
        self.brand_service = BrandService()
        self.brand_form = BrandForm(self.on_submit)
        self.validator = NameFieldValidator()
        self.form_data: dict = {}
    
    def on_submit(self, form_data: dict):
        is_valid, errors = self.validator.validate_name_field(form_data)
        
        if not is_valid:
            log.error(f"Error al validar el formulario: {errors}")
            return
        
        try:
            brand_dto = BrandDTO(
				brand_id=autoincrement_id(),
				name=form_data["name"]
			)
            
            brand_added = self.brand_service.create_brand(brand_dto)
            log.info(f"Nueva marca creada: {brand_added}")
            return brand_added
        
        except Exception as e:
            return log.error(f"Hubo un error inesperado: {e}")
        
    def create_form_layout(self) -> ft.Container:
        main_content = ft.Row([
			ft.Container(
				content=ft.Column([
					cast(ft.Control, self.brand_form),
				]),
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