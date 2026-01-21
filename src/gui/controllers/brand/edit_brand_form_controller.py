from gui.components.form.brand_form import BrandForm
from gui.validators.name_field_validator import NameFieldValidator
from services.brand_service import BrandService
from config.settings import log
from core.models.dto.brand_dto import BrandDTO
from gui.components.dialog.validate.success.success_dialog import success_dialog
from gui.components.dialog.validate.error.error_dialog import error_dialog
import flet as ft

class EditBrandFormController:
    def __init__(self, page: ft.Page, brand_id: int):
        self.brand_service = BrandService()
        self.brand_form = BrandForm(self.on_submit)
        self.validator = NameFieldValidator()
        self.form_data: dict = {}
        self.brand_id = brand_id
        self.page = page

        brand = self.brand_service.get_brand_by_id(brand_id)
        brand_name = getattr(brand, "name", "")
        if brand:
            self.form_data = {"name": brand_name}
        else:
            log.error(f"[EditBrandFormController.__init__] No se pudo cargar la marca {brand_name}")
            return self.show_error_dialog([f"No se pudo cargar la marca {brand_name}"])
    
    def on_submit(self, form_data: dict):
        is_valid, errors = self.validator.validate_name_field(form_data)
        
        if not is_valid:
            log.error(f"[EditBrandFormController.on_submit] Error al validar el formulario: {errors}")
            self.show_validate_error_dialog(errors)
            return

        brand_dto = BrandDTO(
			self.brand_id,
			name=form_data["name"]
		)
        
        brand_edited = self.brand_service.update_brand(brand_dto)
        if brand_edited:
            log.info(f"[EditBrandFormController.on_submit] Marca editada: {getattr(brand_edited, 'name', '')}.")
            self.show_success_dialog(f"Marca editada: {getattr(brand_edited, 'name', '')}.")
            return brand_edited
        else:
            log.error("[EditBrandFormController.on_submit] No se pudo editar la marca. Intente nuevamente.")
            return self.show_validate_error_dialog(["No se pudo editar la marca. Intente nuevamente."])
        
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
    
    def show_error_dialog(self, errors: list[str]):
        error_msg = "\n".join(errors)
        error_dialog(self.page, error_msg, on_close=lambda: self.page.go("/brands"))
        
    def show_validate_error_dialog(self, errors: list[str]):
        error_msg = "\n".join(errors)
        error_dialog(self.page, error_msg) 
        
    def show_success_dialog(self, msg: str):
        success_dialog(self.page, msg, on_close=lambda: self.page.go("/brands"))