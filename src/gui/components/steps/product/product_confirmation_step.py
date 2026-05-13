from gui.components.steps.product.product_category_brand_step import CategoryBrandStep
from core.abstracts.form import Form
from typing import Callable, Any
import flet as ft


class ConfirmationStep(Form):
    def __init__(self, on_submit: Callable):
        super().__init__("Confirmación", "confirmation")
        self.on_submit = on_submit
        self.form_data: dict = {}
        self.parent: Any = None

    def create_controls(self, form_data: dict) -> list[ft.Control]:
        self.form_data = form_data
        category = form_data.get("category")
        brand = form_data.get("brand")

        ctg_name = "N/A"
        brand_name = "N/A"
        prev_step = None
        if hasattr(self, "parent") and self.parent:
            for step in getattr(self.parent, "steps", []):
                if isinstance(step, CategoryBrandStep):
                    prev_step = step
                    break
        if (
            prev_step
            and hasattr(prev_step, "field_category")
            and prev_step.field_category
        ):
            options = getattr(prev_step.field_category, "options", [])
            for opt in options:
                if str(opt.key) == str(category):
                    ctg_name = opt.text
                    break
        if prev_step and hasattr(prev_step, "field_brand") and prev_step.field_brand:
            options = getattr(prev_step.field_brand, "options", [])
            for opt in options:
                if str(opt.key) == str(brand):
                    brand_name = opt.text
                    break
        if ctg_name == "N/A":
            if isinstance(category, dict):
                ctg_name = category.get("name", "N/A")
            else:
                ctg_name = (
                    getattr(category, "name", None) if category is not None else "N/A"
                )
            if not ctg_name:
                ctg_name = "N/A"
        if brand_name == "N/A":
            if isinstance(brand, dict):
                brand_name = brand.get("name", "N/A")
            else:
                brand_name = (
                    getattr(brand, "name", None) if brand is not None else "N/A"
                )
            if not brand_name:
                brand_name = "N/A"

        summary = [
            self.summary_item("Nombre producto", form_data.get("name", "N/A")),
            self.summary_item("Descripción", form_data.get("description", "N/A")),
            self.summary_item("Stock", str(form_data.get("stock", "0"))),
            self.summary_item("Precio", f"${form_data.get('price', '0')}"),
            self.summary_item("Código", form_data.get("sku", "N/A")),
            self.summary_item("Categoría", ctg_name),
            self.summary_item("Marca", brand_name),
        ]

        return [
            ft.Text(self.title, size=18, weight=ft.FontWeight.BOLD),
            ft.Divider(height=20),
            ft.Text("Revise los datos antes de crear", size=14),
            ft.Container(
                content=ft.Column(summary),
                padding=ft.Padding(20, 20, 20, 20),
                margin=ft.Margin(0, 20, 0, 20),
                border_radius=10,
                border=ft.border.all(1, ft.Colors.OUTLINE),
            ),
        ]

    def summary_item(self, label: str, value: str) -> ft.Container:
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(f"{label}:", weight=ft.FontWeight.W_500, expand=1),
                    ft.Text(value=value, expand=2),
                ]
            ),
            padding=ft.Padding(0, 5, 0, 5),
        )

    def get_data(self) -> dict:
        return self.form_data

    def validate(self) -> tuple[bool, list[str]]:
        return True, []

    def reset(self) -> None:
        pass

