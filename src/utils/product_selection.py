from typing import Any, Optional
import flet as ft

from core.models.dto.cart_product_dto import CartProductDTO


class ProductSelection:
    def __init__(self, page: ft.Page):
        self.page = page
        self.ddl: Optional[ft.Dropdown] = None
        self.qty: Optional[ft.TextField] = None
        self.add_button: Optional[ft.ElevatedButton] = None
        self.added_container: Optional[ft.Column] = None
        self.added_products: list[dict] = []
        self.qty_row: Optional[ft.Row] = None
        self.stock_label: Optional[ft.Text] = None
        self._products: list[dict] = []
        self._products_by_id: dict = {}
        self._on_add_callback = None
        self._cart_service = None
        self._cart_id: Any = None

    def _reload_lines(self):
        if self.added_products is None:
            self.added_products = []
        if self.added_container is None:
            self.added_container = ft.Column(spacing=6)

        self.added_products.clear()
        self.added_container.controls.clear()

        if getattr(self, "_cart_service", None) and getattr(self, "_cart_id", None):
            get_cart = getattr(self._cart_service, "get_cart_by_id", None)
            lines = []

            cart_id_int = int(self._cart_id)

            if callable(get_cart):
                if cart_id_int is not None:
                    lines = get_cart(cart_id_int) or []
                else:
                    lines = []
            else:
                get_all = getattr(self._cart_service, "get_all_carts", None)
                if callable(get_all):
                    all_c = get_all() or []
                    if not isinstance(all_c, (list, tuple, set)):
                        all_c = [all_c]
                    for cp in all_c:
                        cid = (
                            cp.get("cart_id")
                            if isinstance(cp, dict)
                            else getattr(cp, "cart_id", None)
                        )
                        if (
                            cid is not None
                            and cart_id_int is not None
                            and int(str(cid)) == cart_id_int
                        ):
                            lines.append(cp)

            if not isinstance(lines, list):
                if isinstance(lines, (tuple, set)):
                    lines = list(lines)
                else:
                    lines = [lines]

            for cp in lines:
                if isinstance(cp, dict):
                    pid = cp.get("product_id")
                    qty = cp.get("quantity")
                    prod = cp.get("product")
                else:
                    pid = getattr(cp, "product_id", None)
                    qty = getattr(cp, "quantity", None)
                    prod = getattr(cp, "product", None)

                pid_int: Optional[int] = None
                if pid is not None:
                    try:
                        pid_int = int(str(pid))
                    except Exception:
                        pid_int = None

                pname = None
                pprice = None
                if prod:
                    if isinstance(prod, dict):
                        pname = prod.get("name")
                        pprice = prod.get("price")
                    else:
                        pname = getattr(prod, "name", None)
                        pprice = getattr(prod, "price", None)
                else:
                    p = self._products_by_id.get(pid_int)
                    if p:
                        pname = getattr(p, "name", None)
                        pprice = getattr(p, "price", None)

                label = f"{pname} - ${pprice}" if pname is not None else None
                item = {"product_id": pid_int, "quantity": qty, "label": label}
                self.added_products.append(item)
                remove_btn = ft.IconButton(
                    icon=ft.Icons.DELETE,
                    tooltip="Quitar",
                    on_click=lambda ev, pid=pid_int: (
                        self._remove_by_product_id(pid) if pid is not None else None
                    ),
                )

                clickable = ft.GestureDetector(
                    mouse_cursor=ft.MouseCursor.CLICK,
                    content=ft.Text(
                        f"{item.get('label') or f'Producto {pid_int}'} x{qty}",
                        expand=True,
                    ),
                    on_tap=lambda ev, pid=pid_int: (
                        self._select_by_product_id(pid) if pid is not None else None
                    ),
                )
                row = ft.Row(
                    [clickable, remove_btn],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
                self.added_container.controls.append(row)

        page = getattr(self.added_container, "page", None)
        if page is not None:
            page.update()

    def _on_product_change(self, e: ft.ControlEvent) -> None:
        if not self.ddl or not self.ddl.value:
            if self.stock_label is not None:
                self.stock_label.value = ""
                self.stock_label.update()
            return

        try:
            pid = int(self.ddl.value)
        except Exception:
            pid = None

        stock_text = ""
        if pid is not None:
            prod = self._products_by_id.get(pid)
            if prod is not None:
                stock_val = None
                for attr in ("stock", "quantity", "available", "available_quantity"):
                    if hasattr(prod, attr):
                        stock_val = getattr(prod, attr)
                        break
                if stock_val is not None:
                    try:
                        stock_int = int(stock_val)
                        stock_text = f"Disponible: {stock_int}"
                    except Exception:
                        stock_text = f"Disponible: {stock_val}"

        if self.stock_label is not None:
            self.stock_label.value = stock_text
            self.stock_label.update()

    def _on_add_click(self, e: ft.ControlEvent) -> None:
        if not self.ddl or not self.ddl.value:
            return
        pid = int(self.ddl.value)
        qty = int(self.qty.value) if self.qty and self.qty.value else 0
        if qty <= 0:
            idx_to_remove = next(
                (
                    i
                    for i, it in enumerate(self.added_products)
                    if it.get("product_id") == pid
                ),
                None,
            )
            if idx_to_remove is not None:
                self._remove_item(idx_to_remove)
            return

        text = None
        for opt in self.ddl.options or []:
            if str(opt.key) == str(pid):
                text = opt.text
                break

        item = {"product_id": pid, "quantity": qty, "label": text}
        created = None

        if hasattr(self, "_on_add_callback") and callable(self._on_add_callback):
            created = self._on_add_callback(pid, qty)

        pname = None
        pprice = None
        if created:
            prod_info = (
                getattr(created, "product", None)
                if not isinstance(created, dict)
                else created.get("product")
            )
            if prod_info:
                if not isinstance(prod_info, dict):
                    pname = getattr(prod_info, "name", None)
                    pprice = getattr(prod_info, "price", None)
                else:
                    pname = prod_info.get("name")
                    pprice = prod_info.get("price")

        if not pname:
            p = self._products_by_id.get(pid)
            if p:
                pname = getattr(p, "name", None)
                pprice = getattr(p, "price", None)

        if pname:
            item["label"] = f"{pname} - ${pprice}"

        existing_index = next(
            (
                i
                for i, it in enumerate(self.added_products)
                if it.get("product_id") == pid
            ),
            None,
        )
        if existing_index is not None:
            self.added_products[existing_index]["quantity"] = qty
        else:
            self.added_products.append(item)

        if getattr(self, "_cart_service", None) and getattr(self, "_cart_id", None):
            self._reload_lines()
            return

        if self.added_container is not None:
            self.added_container.controls.clear()
            for it in self.added_products:
                ppid = it.get("product_id")
                qqty = it.get("quantity")
                label = it.get("label")
                remove_btn = ft.IconButton(
                    icon=ft.Icons.DELETE,
                    tooltip="Quitar",
                    on_click=lambda ev, pid=ppid: (
                        self._remove_by_product_id(int(pid))
                        if pid is not None
                        else None
                    ),
                )
                clickable = ft.GestureDetector(
                    mouse_cursor=ft.MouseCursor.CLICK,
                    content=ft.Text(
                        f"{label} x{qqty}",
                        expand=True,
                    ),
                    on_tap=lambda ev, pid=ppid: (
                        self._select_by_product_id(int(pid))
                        if pid is not None
                        else None
                    ),
                )
                row = ft.Row(
                    [clickable, remove_btn],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
                self.added_container.controls.append(row)
            self.added_container.update()

    def _select_item(self, index: int) -> None:
        if index < 0 or index >= len(self.added_products):
            return
        item_sel = self.added_products[index]
        if self.ddl is not None:
            self.ddl.value = str(item_sel.get("product_id"))
            self.ddl.update()
        if self.qty is not None:
            self.qty.value = str(item_sel.get("quantity") or 1)
            self.qty.update()

    def _select_by_product_id(self, product_id: int) -> None:
        for idx, it in enumerate(self.added_products):
            if it.get("product_id") == product_id:
                self._select_item(idx)
                break

    def _remove_by_product_id(self, product_id: int) -> None:
        for idx, it in enumerate(self.added_products):
            if it.get("product_id") == product_id:
                self._remove_item(idx)
                break

    def _remove_item(self, index: int) -> None:
        if index < 0 or index >= len(self.added_products):
            return
        if getattr(self, "_cart_service", None) and getattr(self, "_cart_id", None):
            item = self.added_products[index]
            pid = item.get("product_id")
            cpid = item.get("cart_product_id")
            cart_id_int = int(self._cart_id)
            if pid is not None and cart_id_int is not None:
                cp = CartProductDTO(
                    cart_product_id=cpid,
                    cart_id=cart_id_int,
                    product_id=pid,
                    quantity=0,
                    cart=None,
                    product=None,
                )
                svc = getattr(self, "_cart_service", None)
                remove_fn = getattr(svc, "remove_products_by_cart", None)
                if callable(remove_fn):
                    remove_fn(cp)

            if getattr(self, "_cart_service", None) and getattr(self, "_cart_id", None):
                self._reload_lines()
                return

        self.added_products.pop(index)
        if self.added_container is not None:
            self.added_container.controls.clear()
            for idx, item in enumerate(self.added_products):
                remove_btn = ft.IconButton(
                    icon=ft.Icons.DELETE,
                    tooltip="Quitar",
                    on_click=lambda ev, i=idx: self._remove_item(i),
                )
                row = ft.Row(
                    [
                        ft.Text(
                            f"{item.get('label')} x{item.get('quantity')}", expand=True
                        ),
                        remove_btn,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
                self.added_container.controls.append(row)
            self.added_container.update()
