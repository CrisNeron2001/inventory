from gui.components.form.brand_form import BrandForm
from gui.validators.name_field_validator import NameFieldValidator
from services.brand_service import BrandService
from config.settings import log
from typing import cast
from core.models.dto.brand_dto import BrandDTO
from utils.helpers import autoincrement_id
from gui.components.dialog.validate.success.success_dialog import success_dialog
from gui.components.dialog.validate.error.error_dialog import error_dialog
import flet as ft

class AddBrandFormController:
    def __init__(self, page: ft.Page):
        self.brand_service = BrandService()
        self.brand_form = BrandForm(self.on_submit)
        self.validator = NameFieldValidator()
        self.form_data: dict = {}
        self.page = page
    
    def on_submit(self, form_data: dict):
        is_valid, errors = self.validator.validate_name_field(form_data)
        
        if not is_valid:
            log.error(f"[AddBrandFormController.on_submit] Error al validar el formulario: {errors}")
            self.show_validate_error_dialog(errors)
            return
        
        brand_dto = BrandDTO(
			brand_id=autoincrement_id(),
			name=form_data["name"]
		)
            
        brand_added = self.brand_service.create_brand(brand_dto)
        if brand_added:
              log.info(f"[AddBrandFormController.on_submit] Marca creada: {getattr(brand_added, 'name', '')}.")
              self.show_success_dialog(f"Marca editada: {getattr(brand_added, 'name', '')}.")
              return brand_added
        else:
            log.error("[AddBrandFormController.on_submit] No se pudo crear la marca. Intente nuevamente.")
            return self.show_validate_error_dialog(["No se pudo crear una nueva marca. Intente nuevamente."])
        
    def create_form_layout(self) -> ft.Container:
        form_controls = self.brand_form.create_controls({})
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
        error_dialog(self.page, error_msg, on_close=lambda: self.page.go("/brands"))
        
    def show_validate_error_dialog(self, errors: list[str]):
        error_msg = "\n".join(errors)
        error_dialog(self.page, error_msg) 
        
    def show_success_dialog(self, msg: str):
        success_dialog(self.page, msg, on_close=lambda: self.page.go("/brands"))