import flet as ft
from typing import Optional, List
from services.cart_service import CartService
from services.sale_service import SaleService
from services.product_service import ProductService
from services.ticket_printer_service import TicketPrinterService, TicketPrinterConfig
from core.models.dto.cart_dto import CartDTO
from core.models.dto.cart_product_dto import CartProductDTO
from core.models.dto.sale_dto import SaleDTO
from config.settings import log
from services.user_service import UserService
from utils.helpers import autoincrement_id
from gui.components.dialog.validate.error.error_dialog import error_dialog


class POSCartManager:
    def __init__(self, controller, page: ft.Page):
        self.controller = controller
        self.cart_service: CartService = controller.cart_service
        self.sale_service: SaleService = controller.sale_service
        self.product_service: ProductService = controller.product_service
        self.cart: List[dict] = controller.cart
        self.page = page
        self.user_service: UserService = controller.user_service

        if getattr(self.controller, "user_inv_id", None) is None:
            user_data = self.page.session.get("user_inv")
            if user_data:
                uid = (
                    getattr(user_data, "user_inv_id", None)
                    if not isinstance(user_data, dict)
                    else user_data.get("user_inv_id")
                )
                self.controller.user_inv_id = uid
                log.info(
                    f"[POSCartManager.__init__] user_inv_id establecido desde sesión: {uid}"
                )

        self._ticket_printer = TicketPrinterService(
            TicketPrinterConfig(
                backend="usb",
                vendor_id=None,
                product_id=None,
            )
        )

    def add_to_cart(
        self, product_id: int, user_inv_id: int, qty: int
    ) -> CartProductDTO | None:
        if qty <= 0:
            return None

        prod = next(
            (
                p
                for p in self.controller.products
                if getattr(p, "product_id", None) == product_id
            ),
            None,
        )
        if not prod:
            return None

        created_cart = None

        uid = getattr(self.controller, "user_inv_id", None)

        if self.controller.current_cart_id is None:
            if not uid:
                self.show_validate_error_dialog(
                    ["Debe iniciar sesión para crear un carrito."]
                )
                log.error(
                    "[POSCartManager.add_to_cart] Intento de crear carrito sin usuario autenticado."
                )
                return None

            cart_dto = CartDTO(cart_id=None, user_inv_id=uid, user_inv=None)
            created_cart = self.cart_service.create_cart(cart_dto)
            if not created_cart:
                self.show_error_dialog(
                    [
                        "No se pudo crear el carrito. Intenta iniciar sesión o intenta de nuevo."
                    ]
                )
                log.error("[POSCartManager.add_to_cart] No se pudo agregar carrito.")
                return None

            self.controller.current_cart_id = getattr(created_cart, "cart_id", None)
            log.info(
                f"[POSCartManager.add_to_cart] Carrito creado y asignado current_cart_id={self.controller.current_cart_id}"
            )

        else:
            current_stock = getattr(prod, "stock", None)
            if current_stock is None:
                current_stock = getattr(prod, "quantity", None)
            current_stock = int(current_stock or 0)
            log.info(
                f"[POSCartManager.add_to_cart] Validando stock para product_id={product_id}: requested={qty}, available={current_stock}"
            )
            if qty > current_stock:
                self.show_validate_error_dialog(
                    [f"Stock insuficiente. Disponible: {current_stock}"]
                )
                return None

        if (
            getattr(self, "controller", None)
            and getattr(self.controller, "current_cart_id", None) is None
        ):
            log.error(
                "[POSCartManager.add_to_cart] No existe carrito disponible, abortando."
            )
            self.show_error_dialog(["Error interno: carrito no disponible."])
            return None

        cp_dto = CartProductDTO(
            cart_product_id=autoincrement_id(),
            cart_id=self.controller.current_cart_id,
            product_id=product_id,
            quantity=qty,
            cart=None,
            product=None,
        )
        log.info(
            f"[POSCartManager.add_to_cart] generando un carrito con decremento desde dto: {cp_dto}"
        )
        created_cp = self.cart_service.create_cart_product_with_decrement(cp_dto)
        if created_cp:
            log.info(
                f"[POSCartManager.add_to_cart] generado carrito con producto devolvió: {created_cp}"
            )
        else:
            log.warning(
                f"[POSCartManager.add_to_cart] no ha generado carrito para cart_id={self.controller.current_cart_id}, product_id={product_id}, quantity={qty}"
            )

        display_price = None
        display_name = None
        if created_cp:
            prod_info = (
                getattr(created_cp, "product", None)
                if not isinstance(created_cp, dict)
                else created_cp.get("product")
            )
            if prod_info:
                display_name = (
                    getattr(prod_info, "name", None)
                    if not isinstance(prod_info, dict)
                    else prod_info.get("name")
                )
                display_price = (
                    getattr(prod_info, "price", None)
                    if not isinstance(prod_info, dict)
                    else prod_info.get("price")
                )
        if display_price is None and prod is not None:
            display_price = getattr(prod, "price", 0)
        if display_name is None and prod is not None:
            display_name = getattr(prod, "name", None)

        line = {
            "product": prod,
            "qty": qty,
            "line_total": qty * (display_price or 0),
            "cart_product": created_cp,
        }
        self.cart.append(line)
        return created_cp

    def remove_from_cart(self, index: int) -> None:
        if 0 <= index < len(self.cart):
            self.cart.pop(index)

    def cart_total(self) -> int:
        return sum(item["line_total"] for item in self.cart)

    def confirm_sale(
        self, payment_method: Optional[str] = None, payment_amount: Optional[int] = None
    ) -> Optional[List]:
        if not self.cart:
            return None

        uid = getattr(self.controller, "user_inv_id", None)

        use_cart_id = getattr(self.controller, "current_cart_id", None)

        if uid is None or use_cart_id is None:
            log.error(
                f"[POSCartManager.confirm_sale] No se puede confirmar venta sin usuario autenticado o carrito activo. user_inv_id={uid}, current_cart_id={use_cart_id}"
            )
            self.show_validate_error_dialog(
                ["Debe iniciar sesión para confirmar la venta."]
            )
            return None

        sale_dto = SaleDTO(
            sale_id=None,
            cart_id=use_cart_id,
            sale_date=None,
            notes=f"Metodo: {payment_method}, Monto: {payment_amount}",
        )
        created_sale = self.sale_service.create_sale(sale_dto)

        if created_sale:
            try:
                self._ticket_printer.print_sale_ticket(
                    sale=created_sale,
                    cart_items=self.cart,
                    business_name="Mi Comercio",
                    business_rut=None,
                )
                self.cart.clear()
                self.controller.current_cart_id = None
                return [created_sale]
            except Exception as ex:
                log.error(
                    f"[POSCartManager.confirm_sale] Error al imprimir ticket: {ex}"
                )
        return None

    def on_select_cart_line(self, idx: int, checked: bool) -> None:
        if checked:
            self.controller.selected_indices.add(idx)
        else:
            self.controller.selected_indices.discard(idx)
        self.controller.update_content()

    def remove_product_by_cart(self) -> None:
        selected = self.controller.selected_indices
        if not selected:
            return

        if self.controller.current_cart_id is not None:
            pids = [
                getattr(self.cart[i]["product"], "product_id", None)
                for i in selected
                if i < len(self.cart)
            ]
            log.info(
                f"[POSCartManager.remove_product_by_cart] indices seleccionados={selected}, cart_id={self.controller.current_cart_id}, product_ids={pids}"
            )
            cp_dto = CartProductDTO(
                cart_product_id=autoincrement_id(),
                cart_id=self.controller.current_cart_id,
                product_id=0,
                quantity=0,
                cart=None,
                product=None,
            )
            setattr(cp_dto, "product_id", pids)
            self.cart_service.remove_products_by_cart(cp_dto)

        for i in sorted(selected, reverse=True):
            if 0 <= i < len(self.cart):
                self.cart.pop(i)

        self.controller.selected_indices.clear()
        self.controller.update_content()

    def show_error_dialog(self, errors: list[str]):
        error_msg = "\n".join(errors)
        error_dialog(self.page, error_msg, on_close=lambda: self.page.go("/sales"))

    def show_validate_error_dialog(self, errors: list[str]):
        error_msg = "\n".join(errors)
        error_dialog(self.page, error_msg)
