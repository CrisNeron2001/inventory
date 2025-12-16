from typing import Any, List
from core.models.dto.sale_dto import SaleDTO
from core.models.entity.sale_entity import Sale
from datetime import datetime

def dto_to_entity(dto: SaleDTO) -> Sale:
    return Sale(
        sale_id=dto.sale_id,
        cart_id=dto.cart_id or 0,
        sale_date=dto.sale_date or datetime.now(),
        notes=dto.notes,
        created_at=dto.created_at or datetime.now(),
        updated_at=dto.updated_at or datetime.now(),
        product_name=dto.product_name,
        quantity=dto.quantity,
        unit_price=dto.unit_price,
        total_price=dto.total_price,
    )

def entity_to_dto(entity: Sale) -> SaleDTO:
    return SaleDTO(
        sale_id=entity.sale_id,
        cart_id=entity.cart_id,
        sale_date=entity.sale_date,
        notes=entity.notes,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
        product_name=entity.product_name,
        quantity=entity.quantity,
        unit_price=entity.unit_price,
        total_price=entity.total_price,
    )

def row_to_entity(row: List[Any]) -> Sale:
    return Sale(
        sale_id=row[0],
        cart_id=row[1],
        sale_date=row[2],
        notes=row[3],
        created_at=row[4],
        updated_at=row[5],
        product_name=row[6] if len(row) > 6 and row[6] is not None else None,
        quantity=int(row[7]) if len(row) > 7 and row[7] is not None else None,
        unit_price=row[8] if len(row) > 8 and row[8] is not None else None,
        total_price=row[9] if len(row) > 9 and row[9] is not None else None,
    )
