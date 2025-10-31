from datetime import datetime
from core.models.dto.category_dto import CategoryDTO
from core.models.entity.category_entity import Category
from typing import Any

def dto_to_entity(dto: CategoryDTO) -> Category:
    return Category(
        category_id=dto.category_id,
        name=dto.name,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

def entity_to_dto(entity: Category) -> CategoryDTO:
    return CategoryDTO(
        category_id=entity.category_id,
        name=entity.name
    )

def row_to_entity(row: list[Any]) -> Category:
    return Category(
		category_id=row[0],
		name=row[1],
		created_at=row[2],
		updated_at=row[3]
	)

def category_dto_to_entity(dto: CategoryDTO) -> Category:
	return dto_to_entity(dto)

def category_entity_to_dto(entity: Category) -> CategoryDTO:
    return entity_to_dto(entity)