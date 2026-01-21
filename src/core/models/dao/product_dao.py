from typing import Optional, List, Any
from core.database.connections import DatabaseConnection
from core.database.queries import (
    insert_product,
    select_product_by_id,
    select_all_products,
    update_product,
    update_product_stock_by_name,
    delete_product
)
from core.models.mapper.product_mapper import row_to_entity
from core.models.entity.product_entity import Product
from config.settings import log
from psycopg2 import errors

class ProductDAO:
    def __init__(self):
        self.db_conn = DatabaseConnection.get_connection_db()
        self.cursor = self.db_conn.cursor() if self.db_conn else None
        
    def create_product(self, product: Product) -> Optional[Product]:
        if self.cursor and self.db_conn:
            log.info("[ProductDAO.create_product] Creando un nuevo producto.")
            try:
                self.cursor.execute(
                    insert_product,
                    (
                        product.name,
                        product.description,
                        product.stock,
                        product.price,
                        (product.category.category_id if product.category else None),
                        (product.brand.brand_id if product.brand else None),
                        product.sku,
                        product.is_available,
                        (product.category.name if product.category else None),
                        (product.brand.name if product.brand else None)
                    ))
                self.db_conn.commit()
                row: Any = self.cursor.fetchone()
                product_created = row_to_entity(row=list(row))
                log.info(f"[ProductDAO.create_product] Producto creado con éxito: {product_created}.")
                return product_created
            except errors.UniqueViolation:
                self.db_conn.rollback()
                log.error(f"[ProductDAO.create_product] SKU duplicado al crear producto: {product.sku}.")
                return None
            except Exception as ex:
                self.db_conn.rollback()
                log.error(f"[ProductDAO.create_product] Error al crear un producto: {ex}.")
                return None
        else:
            return log.error("[ProductDAO.create_product] Error al crear un producto.")
    
    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        if self.cursor and self.db_conn:
            log.info("[ProductDAO.get_product_by_id] Obteniendo por el id del producto.")
            self.cursor.execute(select_product_by_id,(product_id,))
            row: Any = self.cursor.fetchone()
            getted_product_id = row_to_entity(list(row))
            log.info(f"[ProductDAO.get_product_by_id] Producto por id obtenido: {getted_product_id}.")
            return getted_product_id
        else: 
            return log.error("[ProductDAO.get_product_by_id] Error al obtener por el id del producto.")
    
    def get_all_products(self) -> List[Product]:
        if self.cursor and self.db_conn:
            log.info("[ProductDAO.get_all_products] Obteniendo a todos los productos.")
            self.cursor.execute(select_all_products) 
            rows: List[Any] = self.cursor.fetchall() 
            products = [row_to_entity(list(row)) for row in rows]
            log.info(f"[ProductDAO.get_all_products] Productos obtenidos: {products}.")
            return products
        else:
            log.error("[ProductDAO.get_all_products] Error al traer todos los productos.")
            return []
    
    def edit_product(self, product: Product) -> Optional[Product]:
        if self.cursor and self.db_conn:
            log.info("[ProductDAO.edit_product] Editando un producto.")
            self.cursor.execute(
				update_product,
				(
                    product.product_id,
                    product.name,
                    product.description,
                    product.stock,
                    product.price,
                    (product.category.category_id if product.category else None),
                    (product.brand.brand_id if product.brand else None),
                    product.sku,
                    product.is_available,
                    (product.category.name if product.category else None),
                    (product.brand.name if product.brand else None)
				)) 
            self.db_conn.commit() 
            row: Any = self.cursor.fetchone()
            product_updated = row_to_entity(row=list(row))
            log.info(f"[ProductDAO.edit_product] Producto editado: {product_updated}.")
            return product_updated
        else:
            return log.error("[ProductDAO.edit_product] Error al editar el producto.")
            
    def edit_product_stock_by_name(self, name: str) -> Optional[Product]:
        if self.cursor and self.db_conn:
            log.info("[ProductDAO.edit_product_stock_by_name] Editando disponibilidad.")
            self.cursor.execute(update_product_stock_by_name, (name))
            self.db_conn.commit()
            row: Any = self.cursor.fetchone()
            product_stock_updated = row_to_entity(row=list(row))
            log.info(f"[ProductDAO.edit_product_stock_by_name] Disponibilidad de producto editado: {product_stock_updated}.")
            return product_stock_updated
        else:
            return log.error("[ProductDAO.edit_product_stock_by_name] Error al editar la disponibilidad del producto.")
				
    
    def delete_product(self, product_id: int) -> bool:
        if self.cursor and self.db_conn:
            log.info("[ProductDAO.delete_product] Eliminando un producto.")
            self.cursor.execute(delete_product, (product_id,))
            self.db_conn.commit()
            product_deleted = self.cursor.rowcount > 0
            log.info(f"[ProductDAO.delete_product] Producto eliminado: {product_deleted}.")
            return product_deleted 
        else:
            log.error("[ProductDAO.delete_product] El producto no existe o ya fue eliminado.")
            return False