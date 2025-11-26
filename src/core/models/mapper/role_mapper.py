from datetime import datetime
from core.models.dto.role_dto import RoleDTO
from core.models.entity.role_entity import Role
from typing import Any

def dto_to_entity(dto: RoleDTO) -> Role:
    return Role(
        role_inv_id=dto.role_inv_id,
        name=dto.name,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

def entity_to_dto(entity: Role) -> RoleDTO:
    return RoleDTO(
        role_inv_id=entity.role_inv_id,
        name=entity.name
    )

def row_to_entity(row: list[Any]) -> Role:
    return Role(
		role_inv_id=row[0],
		name=row[1],
		created_at=row[2],
		updated_at=row[3]
	)

def role_dto_to_entity(dto: RoleDTO) -> Role:
	return dto_to_entity(dto)

def role_entity_to_dto(entity: Role) -> RoleDTO:
    return entity_to_dto(entity)