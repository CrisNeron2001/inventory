import flet as ft
from gui.controllers.brand.edit_brand_form_controller import EditBrandFormController

def edit_brand_view(brand_id: int, page:ft.Page):
    controller = EditBrandFormController(brand_id=brand_id, page=page)
    return controller.create_form_layout()