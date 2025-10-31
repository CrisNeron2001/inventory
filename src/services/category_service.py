from core.models.dao.category_dao import CategoryDAO
from core.models.dto.category_dto import CategoryDTO
from core.models.mapper.category_mapper import dto_to_entity, entity_to_dto
from typing import List
from config.settings import log

class CategoryService:
    def __init__(self):
        self.dao = CategoryDAO()
        
    def create_category(self, category_dto: CategoryDTO) -> CategoryDTO | None:
        category = dto_to_entity(category_dto)
        new_category = self.dao.create_category(category=category)
        log.info(f"Nueva categoria creada: {new_category}")
        return entity_to_dto(new_category) if new_category else None
    
    def get_category_by_id(self, category_id: int) -> CategoryDTO | None:
        category = self.dao.get_category_by_id(category_id=category_id)
        log.info(f"Categoria obtenida por id: {category}")
        return entity_to_dto(category) if category else None
    
    def get_all_categories(self) -> List[CategoryDTO]:
        categorys = self.dao.get_all_categories()
        log.info(f"Obtenido todas las categorias: {categorys}")
        return [entity_to_dto(category) for category in categorys]
    
    def update_category(self, category_dto: CategoryDTO) -> CategoryDTO | None:
        category = dto_to_entity(category_dto)
        updated_category = self.dao.edit_category(category=category)
        log.info(f"Categoria modificada: {updated_category}")
        return entity_to_dto(updated_category) if updated_category else None
    
    def delete_category(self, category_id: int) -> bool | None:
        category = self.dao.delete_category(category_id=category_id)
        log.info(f"Categoria eliminada: {category}")
        return True if category else False 