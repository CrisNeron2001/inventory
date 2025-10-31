from datetime import datetime
from core.models.dto.product_dto import ProductDTO
from core.models.dto.category_dto import CategoryDTO
from core.models.dto.brand_dto import BrandDTO
from core.models.entity.product_entity import Product
from core.models.mapper.category_mapper import category_dto_to_entity, category_entity_to_dto
from core.models.mapper.brand_mapper import brand_dto_to_entity, brand_entity_to_dto
from typing import Any, List

def dto_to_entity(dto: ProductDTO) -> Product:
    return Product(
        product_id=dto.product_id,
        name=dto.name,
        description=dto.description,
        quantity=dto.quantity,
        price=dto.price,
        sku=dto.sku,
        is_available=dto.is_available,
        category=category_dto_to_entity(dto.category) if dto.category else None,
        brand=brand_dto_to_entity(dto.brand) if dto.brand else None,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

def entity_to_dto(entity: Product) -> ProductDTO:
    # Convertir categorías y marcas que puedan venir como string desde consultas que devuelven solo nombres
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
        quantity=entity.quantity,
        price=entity.price,
        sku=entity.sku,
        is_available=entity.is_available,
        category=cat_dto,
        brand=br_dto
    )

def row_to_entity(row: List[Any]) -> Product:
    return Product(
        product_id=row[0],
        name=row[1],
        description=row[2],
        quantity=row[3],
        price=row[4],
        sku=row[5],
        is_available=row[6],
        created_at=row[7],
        updated_at=row[8],
        category=row[9],
        brand=row[10]
    )
