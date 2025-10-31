from typing import Optional, List, Any
from core.database.connections import DatabaseConnection
from core.database.queries import (
    insert_category,
    select_category_name_by_id,
    select_all_categories_names,
    update_category,
    delete_category
)
from core.models.mapper.category_mapper import row_to_entity
from core.models.entity.category_entity import Category
from config.settings import log

class CategoryDAO:
    def __init__(self):
        self.db_conn = DatabaseConnection.get_connection_db()
        self.cursor = self.db_conn.cursor() if self.db_conn else None
    
    def create_category(self, category: Category) -> Optional[Category]:
        if self.cursor and self.db_conn:
            log.info("Creando una nueva categoria.")
            self.cursor.execute(insert_category, (category.name,))
            self.db_conn.commit()
            row: Any = self.cursor.fetchone()
            category_created = row_to_entity(row=list(row))
            log.info(f"Categoria creada: {category_created}")
            return category_created
        else:
            return log.error("Error al crear una catrgoria.")
    
    def get_category_by_id(self, category_id: int) -> Optional[Category]:
        if self.cursor and self.db_conn:
            log.info("Obteniendo por el id de categoria.")
            self.cursor.execute(select_category_name_by_id,(category_id,))
            row: Any = self.cursor.fetchone()
            getted_category_id = row_to_entity(row=list(row))
            log.info(f"Categoria obtenido por id: {getted_category_id}")
            return getted_category_id
        else:
            return log.error("Error al obtener por el id de categoria.")
    
    def get_all_categories(self) -> List[Category]:
        if self.cursor and self.db_conn:
            log.info("Obteniendo a todas las categorias.")
            self.cursor.execute(select_all_categories_names)
            rows: List[Any] = self.cursor.fetchall() 
            categories = [row_to_entity(list(row)) for row in rows ]
            log.info(f"Todas las categorias obtenidas: {categories}")
            return categories
        else:
            log.error("Error al obtener todas las categorias.")
            return []
    
    def edit_category(self, category: Category) -> Optional[Category]:
        if self.cursor and self.db_conn:
            log.info("Editando una categoria.")
            self.cursor.execute(
				update_category,
				(
					category.name,
					category.category_id
				))
            self.db_conn.commit()
            row: Any = self.cursor.fetchone()
            category_updated = row_to_entity(row=list(row))
            log.info(f"Categoria editada: {category_updated}")
            return category_updated
        else:
            return log.error("Error al editar un producto.")
    
    def delete_category(self, category_id: int) -> bool:
        if self.cursor and self.db_conn:
            log.info("Eliminando una categoria.")
            self.cursor.execute(delete_category, (category_id,)) 
            self.db_conn.commit() 
            category_delected = self.cursor.rowcount > 0 
            log.info(f"Categoria eliminada: {category_delected}")
            return category_delected
        else:
            log.error("No existe la categoria o ya se ha eliminado")
            return False