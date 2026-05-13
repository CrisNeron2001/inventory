from core.models.entity.cart_entity import Cart
from core.models.dto.cart_dto import CartDTO
from core.models.dto.user_dto import UserDTO
from core.models.mapper.user_mapper import (
    user_inv_dto_to_entity,
    user_inv_entity_to_dto,
)
from typing import Any, List
from datetime import datetime
from dateutil import parser as _parser  # type: ignore


def dto_to_entity(dto: CartDTO) -> Cart:
    return Cart(
        cart_id=dto.cart_id,
        user_inv_id=dto.user_inv_id,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        user_inv=user_inv_dto_to_entity(dto.user_inv) if dto.user_inv else None,
    )


def entity_to_dto(entity: Cart) -> CartDTO:
    user_dto = None
    if entity.user_inv:
        try:
            user_dto = user_inv_entity_to_dto(entity.user_inv)
        except Exception:
            try:
                user_dto = UserDTO(
                    user_inv_id=None,
                    first_name="",
                    middle_name="",
                    last_name="",
                    rut="",
                    password="",
                    created_at=None,
                    updated_at=None,
                )
            except Exception:
                user_dto = None

    return CartDTO(
        cart_id=entity.cart_id,
        user_inv_id=entity.user_inv_id,
        user_inv=user_dto,
    )


def row_to_entity(row: List[Any]) -> Cart:
    cart_id = row[0] if len(row) > 0 else None
    user_inv_id = row[1] if len(row) > 1 else None
    raw_created_at = row[2] if len(row) > 2 else None
    raw_updated_at = row[3] if len(row) > 3 else None
    user_inv = row[4] if len(row) > 4 else None

    def _to_datetime(val: Any) -> datetime:
        if isinstance(val, datetime):
            return val
        if val is None:
            return datetime.now()
        if isinstance(val, (int, float)):
            try:
                return datetime.fromtimestamp(val)
            except Exception:
                return datetime.now()
        if isinstance(val, str):
            try:
                return datetime.fromisoformat(val)
            except Exception:
                try:
                    return _parser.parse(val)
                except Exception:
                    return datetime.now()
        return datetime.now()

    created_at = _to_datetime(raw_created_at)
    updated_at = _to_datetime(raw_updated_at)

    return Cart(
        cart_id=cart_id,
        user_inv_id=user_inv_id,
        created_at=created_at,
        updated_at=updated_at,
        user_inv=user_inv,
    )


def cart_dto_to_entity(dto: CartDTO) -> Cart:
    return dto_to_entity(dto)


def cart_entity_to_dto(entity: Cart) -> CartDTO:
    return entity_to_dto(entity)

