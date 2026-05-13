from core.abstracts.form import Form
from gui.validators.product_form_validator import FormProductValidator
from utils.helpers import field_category, field_brand
from utils.constants import ALLOWED_FIELD
from typing import Optional
import flet as ft


class CategoryBrandStep(Form):
    def __init__(self):
        super().__init__("Categoría y marca", "category_brand")
        self.field_category: Optional[ft.Dropdown] = None
        self.field_brand: Optional[ft.Dropdown] = None
        self.validator = FormProductValidator()

    def create_controls(self, form_data: dict) -> list[ft.Control]:
        self.field_category = field_category()
        self.field_brand = field_brand()
        return [
            ft.Text(self.title, size=18, weight=ft.FontWeight.BOLD),
            ft.Divider(height=10),
            ft.Text("Clasificación del producto:", size=16, weight=ft.FontWeight.W_500),
            ft.Row(
                [
                    ft.Container(self.field_category, expand=1),
                    ft.Container(self.field_brand, expand=1),
                ]
            ),
        ]

    def get_data(self) -> dict:
        category_obj = None
        brand_obj = None
        if self.field_category is not None and self.field_category.value:
            for opt in getattr(self.field_category, "options", []):
                if str(opt.key) == str(self.field_category.value):
                    category_obj = {"category_id": opt.key, "name": opt.text}
                    break
        if self.field_brand is not None and self.field_brand.value:
            for opt in getattr(self.field_brand, "options", []):
                if str(opt.key) == str(self.field_brand.value):
                    brand_obj = {"brand_id": opt.key, "name": opt.text}
                    break
        return {
            "category": category_obj,
            "brand": brand_obj,
        }

    def validate(self) -> tuple[bool, list[str]]:
        data = self.get_data()
        return self.validator.validate_step_product_form_data("category_brand", data)

    def reset(self) -> None:
        for field in ALLOWED_FIELD["field_category_brand_data"]:
            setattr(self, field, None)
