from core.models.dto.permission_dto import PermissionDTO
from core.models.entity.permission_entity import Permission
from typing import Any, List
from datetime import datetime


def dto_to_entity(dto: PermissionDTO) -> Permission:
    return Permission(
        permission_key=dto.permission_key,
        description=dto.description,
        created_at=datetime.now()
    )


def entity_to_dto(entity: Permission) -> PermissionDTO:
    return PermissionDTO(permission_key=entity.permission_key, description=entity.description)


def row_to_entity(row: List[Any]) -> Permission:
    return Permission(permission_key=row[0], description=row[1], created_at=row[2])
