from typing import Optional, List, Any
from core.database.connections import DatabaseConnection
from core.database.queries import (
    insert_sale,
    select_sale_by_id,
    select_all_sales,
    update_sale,
    delete_sale,
)
from core.models.mapper.sale_mapper import row_to_entity
from core.models.entity.sale_entity import Sale
from config.settings import log

class SaleDAO:
    def __init__(self):
        self.db_conn = DatabaseConnection.get_connection_db()
        self.cursor = self.db_conn.cursor() if self.db_conn else None

    def create_sale(self, sale: Sale) -> Optional[Sale]:
        if not (self.cursor and self.db_conn):
            log.error("[SaleDAO.create_sale] Error al crear una venta: sin conexión DB")
            return None

        try:
            log.info("[SaleDAO.create_sale] Creando una nueva venta.")
            cart_id = sale.cart_id

            params = (
                cart_id,
                sale.notes,
            )

            self.cursor.execute(insert_sale, params)
            row: Any = self.cursor.fetchone()
            try:
                self.db_conn.commit()
            except Exception:
                try:
                    self.db_conn.rollback()
                except Exception:
                    pass

            if not row:
                log.error("[SaleDAO.create_sale] No se obtuvo fila creada para sale.")
                return None

            sale_created = row_to_entity(row=list(row))
            log.info(f"[SaleDAO.create_sale] Venta creada con éxito: {sale_created}.")
            return sale_created
        except Exception as ex:
            try:
                self.db_conn.rollback()
            except Exception:
                pass
            log.error(f"[SaleDAO.create_sale] Error creando venta: {ex}.")
            return None

    def get_sale_by_id(self, sale_id: int) -> Optional[Sale]:
        if self.cursor and self.db_conn:
            log.info("[SaleDAO.get_sale_by_id] Obteniendo venta por id.")
            self.cursor.execute(select_sale_by_id, (sale_id,))
            row: Any = self.cursor.fetchone()
            if not row:
                return None
            sale = row_to_entity(list(row))
            log.info(f"[SaleDAO.get_sale_by_id] Venta por id obtenida: {sale}.")
            return sale
        else:
            return log.error("[SaleDAO.get_sale_by_id] Error al obtener venta por id.")

    def get_all_sales(self) -> List[Sale]:
        if self.cursor and self.db_conn:
            log.info("[SaleDAO.get_all_sales] Obteniendo todas las ventas.")
            self.cursor.execute(select_all_sales)
            rows: List[Any] = self.cursor.fetchall()
            sales = [row_to_entity(list(row)) for row in rows]
            log.info(f" Ventas obtenidas: {sales}.")
            return sales
        else:
            log.error("[SaleDAO.get_all_sales] Error al traer todas las ventas.")
            return []

    def delete_sale(self, sale_id: int) -> bool:
        if self.cursor and self.db_conn:
            log.info("[SaleDAO.delete_sale] Eliminando una venta.")
            self.cursor.execute(delete_sale, (sale_id,))
            self.db_conn.commit()
            deleted = self.cursor.rowcount > 0
            log.info(f"[SaleDAO.delete_sale] Venta eliminada: {deleted}.")
            return deleted
        else:
            log.error("[SaleDAO.delete_sale] La venta no existe o ya fue eliminada.")
            return False

    def update_sale(self, sale: Sale) -> Optional[Sale]:
        if self.cursor and self.db_conn:
            try:
                log.info("[SaleDAO.update_sale] Actualizando venta.")
                self.cursor.execute(
                    update_sale,
                    (
                        sale.notes,
                        sale.sale_id,
                    ),
                )
                row = self.cursor.fetchone()
                try:
                    self.db_conn.commit()
                except Exception:
                    self.db_conn.rollback()
                if not row:
                    return None
                updated = row_to_entity(list(row))
                log.info(f"[SaleDAO.update_sale] Venta actualizada: {updated}.")
                return updated
            except Exception as ex:
                log.error(f"[SaleDAO.update_sale] Error actualizando venta: {ex}.")
                return None
        else:
            log.error("[SaleDAO.update_sale] No hay conexión para actualizar la venta.")
            return None
