import flet as ft
from services.sale_service import SaleService
from services.cart_service import CartService
from services.product_service import ProductService
from gui.components.form.edit_sale_form import EditSaleForm
from core.models.dto.sale_dto import SaleDTO
from typing import Optional, Callable
from config.settings import log

class EditSaleFormController:
    def __init__(self, sale_id: int, on_saved: Optional[Callable[[], None]] = None) -> None:
        self.sale_service = SaleService()
        self.product_service = ProductService()
        self.cart_service = CartService()
        self.sale_id = sale_id
        self.on_saved = on_saved
        self.form_data: dict = {}
        self.sale_form = EditSaleForm(self.on_submit)
            
    def load_sale(self) -> dict:
        sale = self.sale_service.get_sale_by_id(self.sale_id)
        if sale is None:
            return {}
        if isinstance(sale, dict):
            return {
                'product_id': sale.get('product_id'),
                'cart_id': sale.get('cart_id'),
                'quantity': sale.get('quantity', 1),
                'unit_price': sale.get('unit_price', 0),
                'notes': sale.get('notes', ''),
            }
        else:
            return {
                'product_id': getattr(sale, 'product_id', None),
                'cart_id': getattr(sale, 'cart_id', None),
                'quantity': getattr(sale, 'quantity', 1),
                'unit_price': getattr(sale, 'unit_price', 0),
                'notes': getattr(sale, 'notes', ''),
            }
        
    def load_product(self):
        sale = self.sale_service.get_sale_by_id(self.sale_id)
        if sale is not None:
            products = self.product_service.get_all_products()
            product_options = [ft.DropdownOption(key=str(p.product_id), text=f"{p.name} - ${p.price}") for p in products]
            return product_options

    def on_submit(self, form_data: dict):
        try:
            product_id = form_data.get('product_id') or form_data.get('product_id')
            quantity = int(form_data.get('quantity', 0))
            unit_price = int(form_data.get('unit_price', 0))
            notes = form_data.get('notes', '')

            if not product_id:
                raise ValueError('Producto requerido')
            if quantity <= 0:
                raise ValueError('Cantidad inválida')
            cart_id = self.form_data.get('cart_id') if self.form_data else None
            sale_dto = SaleDTO(
                sale_id=self.sale_id,
                cart_id=cart_id,
                unit_price=unit_price,
                total_price=quantity * unit_price,
                sale_date=None,
                notes=notes,
            )
            updated = self.sale_service.update_sale(sale_dto)
            if updated:
                page = getattr(self.sale_form, 'page', None)
                if self.on_saved:
                    self.on_saved()
                elif page is not None:
                    page.go('/sales')
            return updated
        except Exception as e:
            log.error(f"Error al guardar la venta: {e}")
            page = getattr(self.sale_form, 'page', None)
            if page is not None:
                page.snack_bar = ft.SnackBar(ft.Text(str(e)), open=True)
                page.update()
            return None

    def create_form_layout(self) -> ft.Container:
        self.form_data = self.load_sale()
        product_options = self.load_product() or []
        self.sale_form.products_options = product_options
        form_controls = self.sale_form.create_controls(self.form_data)
        form_column = ft.Column(
            form_controls,
            scroll=ft.ScrollMode.ALWAYS,
            expand=True,
        )
        main_content = ft.Row([
            ft.Container(
                content=form_column,
                width=400,
                padding=ft.Padding(20, 20, 20, 20),
                border_radius=10,
                expand=True,
            )
        ], alignment=ft.MainAxisAlignment.START, expand=True)
        return ft.Container(
            content=main_content,
            padding=ft.Padding(20, 20, 20, 20),
            expand=True,
        )