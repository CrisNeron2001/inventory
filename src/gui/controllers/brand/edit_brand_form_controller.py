from gui.components.form.brand_form import BrandForm
from gui.validators.name_field_validator import NameFieldValidator
from services.brand_service import BrandService
from config.settings import log
from typing import cast, Optional, Callable
from core.models.dto.brand_dto import BrandDTO
import flet as ft

class EditBrandFormController:
    def __init__(self, brand_id: int, on_saved: Optional[Callable[[], None]] = None):
        self.brand_service = BrandService()
        self.brand_form = BrandForm(self.on_submit)
        self.validator = NameFieldValidator()
        self.form_data: dict = {}
        self.brand_id = brand_id
        self.on_saved = on_saved
        try:
            brand = self.brand_service.get_brand_by_id(brand_id)
            if brand:
                self.form_data = {"name": getattr(brand, "name", "")}
        except Exception as e:
            log.error(f"No se pudo cargar la marca {brand_id}: {e}")
    
    def on_submit(self, form_data: dict):
        is_valid, errors = self.validator.validate_name_field(form_data)
        
        if not is_valid:
            log.error(f"Error al validar el formulario: {errors}")
            return
        
        try:
            brand_dto = BrandDTO(
                self.brand_id,
                name=form_data["name"]
            )
            
            brand_edited = self.brand_service.update_brand(brand_dto)
            log.info(f"Marca editada: {brand_edited}")
            if brand_edited and self.on_saved:
                try:
                    self.on_saved()
                except Exception:
                    pass
            return brand_edited
        
        except Exception as e:
            return log.error(f"Hubo un error inesperado: {e}")
        
    def create_form_layout(self) -> ft.Container:
        form_controls = self.brand_form.create_controls(self.form_data)
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