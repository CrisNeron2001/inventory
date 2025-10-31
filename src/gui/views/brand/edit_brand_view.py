from typing import Optional, Callable
from gui.controllers.brand.edit_brand_form_controller import EditBrandFormController

def edit_brand_view(brand_id: int, on_saved: Optional[Callable[[], None]] = None):
    controller = EditBrandFormController(brand_id, on_saved=on_saved)
    return controller.create_form_layout()