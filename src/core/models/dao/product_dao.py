from typing import Optional, List, Any
from core.database.connections import DatabaseConnection
from core.database.queries import (
    insert_product,
    select_product_by_id,
	select_all_products,
	update_product,
	delete_product
)
from core.models.mapper.product_mapper import row_to_entity
from core.models.entity.product_entity import Product
from config.settings import log

class ProductDAO:
    def __init__(self):
        self.db_conn = DatabaseConnection.get_connection_db()
        self.cursor = self.db_conn.cursor() if self.db_conn else None
        
    def create_product(self, product: Product) -> Optional[Product]:
        if self.cursor and self.db_conn:
            log.info("Creando un nuevo producto.")
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
                    product.is_available
				))
            self.db_conn.commit()
            row: Any = self.cursor.fetchone()
            product_created = row_to_entity(row=list(row))
            log.info(f"Producto creado con éxito: {product_created}")
            return product_created
        else:
            return log.error("Error al crear un producto")
    
    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        if self.cursor and self.db_conn:
            log.info("Obteniendo por el id del producto.")
            self.cursor.execute(select_product_by_id,(product_id,))
            row: Any = self.cursor.fetchone()
            getted_product_id = row_to_entity(list(row))
            log.info(f"Producto por id obtenido: {getted_product_id}")
            return getted_product_id
        else: 
            return log.error("Error al obtener por el id del producto.")
    
    def get_all_products(self) -> List[Product]:
        if self.cursor and self.db_conn:
            log.info("Obteniendo a todos los productos")
            self.cursor.execute(select_all_products) 
            rows: List[Any] = self.cursor.fetchall() 
            products = [row_to_entity(list(row)) for row in rows]
            log.info(f"Productos obtenidos: {products}")
            return products
        else:
            log.error("Error al traer todos los productos")
            return []
    
    def edit_product(self, product: Product) -> Optional[Product]:
        if self.cursor and self.db_conn:
            log.info("Editando un producto")
            self.cursor.execute(
				update_product,
				(
                    product.name,
                    product.description,
                    product.stock,
                    product.price,
                    (product.category.category_id if product.category else None),
                    (product.brand.brand_id if product.brand else None),
                    product.sku,
                    product.is_available,
                    product.product_id
				)) 
            self.db_conn.commit() 
            row: Any = self.cursor.fetchone()
            product_updated = row_to_entity(row=list(row))
            log.info(f"Producto editado: {product_updated}")
            return product_updated
        else:
            return log.error("Error al editar el producto")
    
    def delete_product(self, product_id: int) -> bool:
        if self.cursor and self.db_conn:
            log.info("Eliminando un producto")
            self.cursor.execute(delete_product, (product_id,))
            self.db_conn.commit()
            product_deleted = self.cursor.rowcount > 0
            log.info(f"Producto eliminado: {product_deleted}")
            return product_deleted 
        else:
            log.error("El producto no existe o ya fue eliminado.")
            return False