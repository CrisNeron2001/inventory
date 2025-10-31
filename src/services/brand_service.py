from core.models.dao.brand_dao import BrandDAO
from core.models.dto.brand_dto import BrandDTO
from core.models.mapper.brand_mapper import dto_to_entity, entity_to_dto
from typing import List
from config.settings import log

class BrandService:
    def __init__(self):
        self.dao = BrandDAO()
        
    def create_brand(self, brand_dto: BrandDTO) -> BrandDTO | None:
        brand = dto_to_entity(brand_dto)
        new_brand = self.dao.create_brand(brand=brand)
        log.info(f"Nueva marca creada: {new_brand}")
        return entity_to_dto(new_brand) if new_brand else None
    
    def get_brand_by_id(self, brand_id: int) -> BrandDTO | None:
        brand = self.dao.get_brand_by_id(brand_id=brand_id)
        log.info(f"Marca obtenida por id: {brand}")
        return entity_to_dto(brand) if brand else None
    
    def get_all_brands(self) -> List[BrandDTO]:
        brands = self.dao.get_all_brands()
        log.info(f"Obtenido todas las marcas: {brands}")
        return [entity_to_dto(brand) for brand in brands]
    
    def update_brand(self, brand_dto: BrandDTO) -> BrandDTO | None:
        brand = dto_to_entity(brand_dto)
        updated_brand = self.dao.edit_brand(brand=brand)
        log.info(f"Marca modificada: {updated_brand}")
        return entity_to_dto(updated_brand) if updated_brand else None
    
    def delete_brand(self, brand_id: int) -> bool | None:
        brand = self.dao.delete_brand(brand_id=brand_id)
        log.info(f"Marca eliminada: {brand}")
        return True if brand else False 