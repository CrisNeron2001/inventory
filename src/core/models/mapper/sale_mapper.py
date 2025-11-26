from typing import Any, List
from core.models.dto.sale_dto import SaleDTO
from core.models.entity.sale_entity import Sale
from datetime import datetime
from core.models.mapper.cart_mapper import cart_dto_to_entity, cart_entity_to_dto

def dto_to_entity(dto: SaleDTO) -> Sale:
    return Sale(
        sale_id=dto.sale_id,
        cart_id=dto.cart_id,
        unit_price=dto.unit_price,
        total_price=dto.total_price,
        sale_date=dto.sale_date or datetime.now(),
        notes=dto.notes,
        amount_price=dto.amount_price,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        cart=cart_dto_to_entity(dto.cart) if dto.cart else None,
    )


def entity_to_dto(entity: Sale) -> SaleDTO:
    return SaleDTO(
        sale_id=entity.sale_id,
        cart_id=entity.cart_id,
        unit_price=entity.unit_price,
        total_price=entity.total_price,
        sale_date=entity.sale_date,
        notes=entity.notes,
        amount_price=entity.amount_price,
        cart=cart_entity_to_dto(entity.cart) if entity.cart else None
    )


def row_to_entity(row: List[Any]) -> Sale:
    sale_id = row[0]
    cart_id = row[1] if len(row) > 1 else None
    unit_price = row[2] if len(row) > 2 else 0
    total_price = row[3] if len(row) > 3 else 0
    sale_date = row[4] if len(row) > 4 else None
    notes = row[5] if len(row) > 5 else None
    amount_price = int(row[6]) if len(row) > 6 and row[6] is not None else 0
    created_at = row[7] if len(row) > 7 else None
    updated_at = row[8] if len(row) > 8 else None
    cart = row[9] if len(row) > 9 else (row[6] if len(row) == 7 else None)
    if created_at is None:
        created_at = datetime.now()
    if updated_at is None:
        updated_at = datetime.now()

    return Sale(
        sale_id=sale_id,
        cart_id=cart_id,
        unit_price=unit_price,
        total_price=total_price,
        sale_date=sale_date,
        notes=notes,
        amount_price=amount_price,
        created_at=created_at,
        updated_at=updated_at,
        cart=cart,
    )
