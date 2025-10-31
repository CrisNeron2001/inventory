from datetime import datetime
from core.models.dto.brand_dto import BrandDTO
from core.models.entity.brand_entity import Brand
from typing import Any

def dto_to_entity(dto: BrandDTO) -> Brand:
    return Brand(
        brand_id=dto.brand_id,
        name=dto.name,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

def entity_to_dto(entity: Brand) -> BrandDTO:
    return BrandDTO(
        brand_id=entity.brand_id,
        name=entity.name
    )

def row_to_entity(row: list[Any]) -> Brand:
    return Brand(
		brand_id=row[0],
		name=row[1],
		created_at=row[2],
		updated_at=row[3]
	)

def brand_dto_to_entity(dto: BrandDTO) -> Brand:
    return dto_to_entity(dto)

def brand_entity_to_dto(entity: Brand) -> BrandDTO:
    return entity_to_dto(entity)