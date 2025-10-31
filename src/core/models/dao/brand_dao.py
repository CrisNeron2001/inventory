from typing import Optional, List, Any
from core.database.connections import DatabaseConnection
from core.database.queries import (
    insert_brand,
    select_brand_name_by_id,
    select_all_brands_names,
    update_brand,
    delete_brand
)
from core.models.mapper.brand_mapper import row_to_entity
from core.models.entity.brand_entity import Brand
from config.settings import log

class BrandDAO:
    def __init__(self):
        self.db_conn = DatabaseConnection.get_connection_db() 
        self.cursor = self.db_conn.cursor() if self.db_conn else None
    
    def create_brand(self, brand: Brand) -> Optional[Brand]:
        if self.cursor and self.db_conn:
            log.info("Creando una nueva marca.")
            self.cursor.execute(insert_brand, (brand.name,)) 
            self.db_conn.commit() 
            row: Any = self.cursor.fetchone() 
            brand_created = row_to_entity(row=list(row))
            log.info(f"Nueva categoria creada: {brand_created}")
            return brand_created
        else:
            return log.error("Error al crear una marca.")
    
    def get_brand_by_id(self, brand_id: int) -> Optional[Brand]:
        if self.cursor and self.db_conn:
            log.info("Obteniendo por el id de marca")
            self.cursor.execute(select_brand_name_by_id,(brand_id,)) 
            row: Any = self.cursor.fetchone() 
            getted_brand_id = row_to_entity(row=list(row)) 
            log.info(f"Obtenido por el id de marca: {getted_brand_id}")
            return getted_brand_id
        else:
            return log.error("Error al obtener por el id de marca.")
    
    def get_all_brands(self) -> List[Brand]:
        if self.cursor and self.db_conn:
            log.info("Obteniendo todas las marcas.")
            self.cursor.execute(select_all_brands_names)
            rows: List[Any] = self.cursor.fetchall() 
            brands = [row_to_entity(list(row)) for row in rows ]
            log.info(f"Todas las marcas obtenidas: {brands}")
            return brands
        else:
            log.error("Error al obtener todas las marcas.")
            return []
    
    def edit_brand(self, brand: Brand) -> Optional[Brand]:
        if self.cursor and self.db_conn:
            log.info("Editando una marca.")
            self.cursor.execute(
				update_brand,
				(
					brand.name,
					brand.brand_id
				))
            self.db_conn.commit()
            row: Any = self.cursor.fetchone()
            brand_updated = row_to_entity(row=list(row)) 
            log.info(f"Marca editada: {brand_updated}")
            return brand_updated
        else:
            return log.error("Error al editar una marca.")
    
    def delete_brand(self, brand_id: int) -> bool:
        if self.cursor and self.db_conn:
            log.info("Eliminando una marca.")
            self.cursor.execute(delete_brand, (brand_id,))
            self.db_conn.commit()
            brand_deleted = self.cursor.rowcount > 0 
            log.info(f"Marca eliminada: {brand_deleted}")
            return brand_deleted
        else:
            log.error("La marca no existe o ha sido eliminada.")
            return False