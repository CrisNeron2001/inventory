from datetime import datetime as _dt
from datetime import datetime
from core.models.dto.user_dto import UserDTO
from core.models.entity.user_entity import User
from typing import Any, List, cast


def dto_to_entity(dto: UserDTO) -> User:
    return User(
        user_inv_id=dto.user_inv_id,
        first_name=dto.first_name,
        middle_name=dto.middle_name,
        last_name=dto.last_name,
        rut=dto.rut,
        password=dto.password,
        created_at=cast(datetime, dto.created_at)
        if getattr(dto, "created_at", None) is not None
        else datetime.now(),
        updated_at=cast(datetime, dto.updated_at)
        if getattr(dto, "updated_at", None) is not None
        else datetime.now(),
    )


def entity_to_dto(entity: User) -> UserDTO:
    return UserDTO(
        user_inv_id=entity.user_inv_id,
        first_name=entity.first_name,
        middle_name=entity.middle_name,
        last_name=entity.last_name,
        rut=entity.rut,
        password=entity.password,
        created_at=getattr(entity, "created_at", None),
        updated_at=getattr(entity, "updated_at", None),
    )


def row_to_entity(row: List[Any]) -> User:
    if len(row) >= 8:
        user_inv_id = row[0]
        first_name = row[1]
        middle_name = row[2]
        last_name = row[3]
        rut = row[4]
        password = row[5]
        created_at = row[6] if row[6] is not None else _dt.now()
        updated_at = row[7] if row[7] is not None else _dt.now()

    else:
        user_inv_id = row[0] if len(row) > 0 else None
        first_name = row[1] if len(row) > 1 else ""
        middle_name = row[2] if len(row) > 2 else ""
        last_name = row[3] if len(row) > 3 else None
        rut = row[4] if len(row) > 4 else ""
        password = ""
        created_at = row[5] if len(row) > 5 and row[5] is not None else _dt.now()
        updated_at = row[6] if len(row) > 6 and row[6] is not None else _dt.now()

    return User(
        user_inv_id=user_inv_id,
        first_name=first_name,
        middle_name=middle_name,
        last_name=last_name or "",
        rut=rut,
        password=password,
        created_at=created_at,
        updated_at=updated_at,
    )


def user_inv_dto_to_entity(dto: UserDTO) -> User:
    return dto_to_entity(dto)


def user_inv_entity_to_dto(entity: User) -> UserDTO:
    return entity_to_dto(entity)
