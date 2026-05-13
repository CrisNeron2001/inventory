from datetime import datetime
from core.models.dto.product_dto import ProductDTO
from core.models.dto.category_dto import CategoryDTO
from core.models.dto.brand_dto import BrandDTO
from core.models.entity.product_entity import Product
from core.models.mapper.category_mapper import (
    category_dto_to_entity,
    category_entity_to_dto,
)
from core.models.mapper.brand_mapper import brand_dto_to_entity, brand_entity_to_dto
from typing import Any, List


def dto_to_entity(dto: ProductDTO) -> Product:
    return Product(
        product_id=dto.product_id,
        name=dto.name,
        description=dto.description,
        stock=dto.stock,
        price=dto.price,
        sku=dto.sku,
        category=category_dto_to_entity(dto.category) if dto.category else None,
        brand=brand_dto_to_entity(dto.brand) if dto.brand else None,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


def entity_to_dto(entity: Product) -> ProductDTO:
    if entity.category and isinstance(entity.category, str):
        cat_dto = CategoryDTO(category_id=None, name=entity.category)
    else:
        cat_dto = category_entity_to_dto(entity.category) if entity.category else None

    if entity.brand and isinstance(entity.brand, str):
        br_dto = BrandDTO(brand_id=None, name=entity.brand)
    else:
        br_dto = brand_entity_to_dto(entity.brand) if entity.brand else None

    return ProductDTO(
        product_id=entity.product_id,
        name=entity.name,
        description=entity.description,
        stock=entity.stock,
        price=entity.price,
        sku=entity.sku,
        category=cat_dto,
        brand=br_dto,
    )


def row_to_entity(row: List[Any]) -> Product:
    return Product(
        product_id=row[0],
        name=row[1],
        description=row[2],
        stock=row[3],
        price=row[4],
        sku=row[5],
        created_at=row[6],
        updated_at=row[7],
        category=row[8],
        brand=row[9],
    )


def product_dto_to_entity(dto: ProductDTO) -> Product:
    return dto_to_entity(dto)


def product_entity_to_dto(entity: Product) -> ProductDTO:
    return entity_to_dto(entity)

