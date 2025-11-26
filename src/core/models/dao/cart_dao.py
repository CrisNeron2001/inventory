from typing import Any, List, Optional
from core.database.connections import DatabaseConnection
from core.database.queries import (
    insert_cart,
    select_all_carts,
    select_cart_by_id,
    insert_cart_product,
    remove_product_from_cart
)
from core.database.queries import update_product_decrease_if_enough
from core.models.mapper.cart_mapper import row_to_entity as c_r_t
from core.models.mapper.cart_product_mapper import row_to_entity as cp_r_t
from core.models.entity.cart_entity import Cart
from core.models.entity.cart_product_entity import CartProduct
from config.settings import log

class CartDAO:
    def __init__(self):
        self.db_conn = DatabaseConnection.get_connection_db()
        self.cursor = self.db_conn.cursor() if self.db_conn else None

    def create_cart(self, cart: Cart) -> Optional[Cart]:
        # Extract user_inv_id preferring explicit attribute; fall back to user object
        user_inv_id = getattr(cart, 'user_inv_id', None)
        if user_inv_id is None:
            temp_user = getattr(cart, 'user_inv', None)
            if temp_user is not None:
                try:
                    user_inv_id = getattr(temp_user, 'user_inv_id', None)
                except Exception:
                    user_inv_id = None

        params = (user_inv_id,)
        if user_inv_id is None:
            log.error(f"Attempted to create cart without user_inv_id: cart={cart}")
            return None
        if self.cursor and self.db_conn:
            log.info("Creando un nuevo carrito.")
            self.cursor.execute(insert_cart, params)
            self.db_conn.commit()
            row: Any = self.cursor.fetchone()
            if not row:
                log.error("No se pudo crear el carrito; no se devolvió fila.")
                return None
            cart_created = c_r_t(row=list(row))
            log.info(f"Carrito creado: {cart_created}")
            return cart_created
        else:
            log.error("Error al crear un carrito.")
            return None

    def create_cart_product(self, cart: CartProduct) -> Optional[CartProduct]:
        # Prefer direct id fields on the CartProduct entity (cart_id/product_id).
        # Fallback to nested objects if those are provided.
        params = (
            getattr(cart, 'cart_id', None) if getattr(cart, 'cart_id', None) is not None else (cart.cart.cart_id if cart.cart else None),
            getattr(cart, 'product_id', None) if getattr(cart, 'product_id', None) is not None else (cart.product.product_id if cart.product else None),
            cart.quantity,
        )
        if self.cursor and self.db_conn:
            log.info("Creando nuevo producto en carrito.")
            self.cursor.execute(insert_cart_product, params)
            self.db_conn.commit()
            row: Any = self.cursor.fetchone()
            if not row:
                log.error("No se pudo crear el producto en el carrito; no se devolvió fila.")
                return None
            cart_product_created = cp_r_t(row=list(row))
            log.info(f"Producto en carrito creado: {cart_product_created}")
            return cart_product_created
        else:
            log.error("Error al crear producto en carrito.")
            return None

    def create_cart_product_with_decrement(self, cart: CartProduct) -> Optional[CartProduct]:
        """Create or upsert cart_product and decrement product stock atomically.
        Returns created cart_product entity or None if not enough stock / error.
        """
        # Prefer direct id fields on the CartProduct entity (cart_id/product_id).
        # This covers cases where the CartProduct was created from a DTO with cart_id/product_id set
        # but nested cart/product objects are None.
        params = (
            getattr(cart, 'cart_id', None) if getattr(cart, 'cart_id', None) is not None else (cart.cart.cart_id if cart.cart else None),
            getattr(cart, 'product_id', None) if getattr(cart, 'product_id', None) is not None else (cart.product.product_id if cart.product else None),
            cart.quantity,
        )

        if not (self.cursor and self.db_conn):
            log.error("Error al crear producto en carrito con decremento: sin conexión DB")
            return None

        try:
            log.info(f"Creando/actualizando cart_product y decrementando stock en una transacción: params={params}")
            # Use the same cursor/connection for both statements and commit once
            self.cursor.execute(insert_cart_product, params)
            # Attempt to decrement stock only if enough stock exists
            dec_product_id = getattr(cart, 'product_id', None) if getattr(cart, 'product_id', None) is not None else (cart.product.product_id if cart.product else None)
            dec_params = (cart.quantity, dec_product_id, cart.quantity)
            self.cursor.execute(update_product_decrease_if_enough, dec_params)
            dec_row = self.cursor.fetchone()
            if not dec_row:
                # Not enough stock, rollback and return None
                try:
                    self.db_conn.rollback()
                except Exception:
                    pass
                log.warning(f"No hay stock suficiente para product_id={cart.product.product_id if cart.product else None}")
                return None

            # Fetch created/updated cart_product row
            # Depending on driver behavior, fetchone after first execute may still be available; to be safe re-run select
            use_cart_id = getattr(cart, 'cart_id', None) if getattr(cart, 'cart_id', None) is not None else (cart.cart.cart_id if cart.cart else None)
            self.cursor.execute(select_cart_by_id, (use_cart_id,))
            rows = self.cursor.fetchall()
            created = None
            if rows:
                # find the row that matches product_id. Support cases where CartProduct.entity
                # has direct product_id set, or where nested product object is present.
                expected_pid = getattr(cart, 'product_id', None) if getattr(cart, 'product_id', None) is not None else (cart.product.product_id if cart.product else None)
                for row in rows:
                    r = list(row)
                    try:
                        cp = cp_r_t(r)
                        if getattr(cp, 'product_id', None) == expected_pid:
                            created = cp
                            break
                    except Exception:
                        continue

            # commit transaction
            try:
                self.db_conn.commit()
            except Exception:
                try:
                    self.db_conn.rollback()
                except Exception:
                    pass
                log.error("Error comiteando transacción para create_cart_product_with_decrement")
                return None

            if created:
                log.info(f"Producto en carrito creado con decremento: {created}")
                return created
            else:
                log.warning("No se pudo obtener fila creada de cart_product tras decremento")
                return None
        except Exception as ex:
            try:
                self.db_conn.rollback()
            except Exception:
                pass
            log.error(f"Error en create_cart_product_with_decrement: {ex}")
            return None

    def get_cart_by_id(self, cart_id: int) -> List[CartProduct]:
        if self.cursor and self.db_conn:
            log.info("Obteniendo por el id de carrito.")
            self.cursor.execute(select_cart_by_id, (cart_id,))
            rows: List[Any] = self.cursor.fetchall()
            if not rows:
                log.info(f"No se encontraron productos para cart_id={cart_id}.")
                return []
            carts = [cp_r_t(list(row)) for row in rows]
            log.info(f"Carrito obtenido por id: {cart_id}, items={len(carts)}")
            return carts
        else:
            log.error("Error al obtener por el id de categoria.")
            return []

    def get_all_carts(self) -> List[CartProduct]:
        if self.cursor and self.db_conn:
            log.info("Obteniendo a todos los carritos.")
            self.cursor.execute(select_all_carts)
            rows: List[Any] = self.cursor.fetchall()
            carts = [cp_r_t(list(row)) for row in rows]
            log.info(f"Todos los carritos obtenidos: {carts}")
            return carts
        else:
            log.error("Error al obtener todas las categorias.")
            return []

    def remove_products_by_cart(self, cart: CartProduct) -> Optional[CartProduct]:
        if not (self.cursor and self.db_conn):
            log.error("Error al remover productos del carrito.")
            return None

        log.info("Removiendo productos del carrito.")
        pids = getattr(cart, "product_id", None)
        if pids is None:
            log.warning("No hay productos para remover en el carrito.")
            return cart

        if not isinstance(pids, (list, tuple, set)):
            pids = [pids]

        try:
            pids_list = list(pids) if not isinstance(pids, (str, bytes)) else [pids]
        except Exception:
            pids_list = [pids]

        log.info(f"Intentando remover product_ids={pids_list} desde cart_id={cart.cart_id}")

        for pid in pids_list:
            params = (pid, cart.cart_id)
            log.info(f"Ejecutando DELETE para product_id={pid} cart_id={cart.cart_id} params={params}")
            try:
                self.cursor.execute(remove_product_from_cart, params)
            except Exception as e:
                log.error(f"Error ejecutando DELETE para params={params}: {e}")
                raise
            try:
                row = self.cursor.fetchone()
                log.info(f"DELETE RETURNING row: {row}")
            except Exception:
                log.info("No RETURNING row disponible tras DELETE")
            try:
                rc = getattr(self.cursor, 'rowcount', None)
                log.info(f"Cursor rowcount after delete: {rc}")
            except Exception:
                pass
            self.db_conn.commit()
        log.info("Productos removidos del carrito.")
        return cart
