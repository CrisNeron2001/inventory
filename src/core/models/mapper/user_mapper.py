from datetime import datetime as _dt
from datetime import datetime
from core.models.dto.user_dto import UserDTO
from core.models.entity.user_entity import User
from core.models.dto.role_dto import RoleDTO
from core.models.mapper.role_mapper import role_dto_to_entity, role_entity_to_dto
from typing import Any, List, cast

def dto_to_entity(dto: UserDTO) -> User:
	return User(
		user_inv_id=dto.user_inv_id,
		role_inv_id=dto.role_inv_id if dto.role_inv_id is not None else 0,
		first_name=dto.first_name,
		last_name=dto.last_name,
		username=dto.username,
		password=dto.password,
		created_at=cast(datetime, dto.created_at) if getattr(dto, 'created_at', None) is not None else datetime.now(),
		updated_at=cast(datetime, dto.updated_at) if getattr(dto, 'updated_at', None) is not None else datetime.now(),
		role_inv=role_dto_to_entity(dto.role_inv) if dto.role_inv else None
	)
    
def entity_to_dto(entity: User) -> UserDTO:
    if entity.role_inv and isinstance(entity.role_inv, str):
        role_dto = RoleDTO(role_inv_id=None, name=entity.role_inv)
    else:
        role_dto = role_entity_to_dto(entity.role_inv) if entity.role_inv else None
        
    return UserDTO(
		user_inv_id=entity.user_inv_id,
		role_inv_id=entity.role_inv_id,
		first_name=entity.first_name,
		last_name=entity.last_name,
		username=entity.username,
		password=entity.password,
		role_inv=role_dto,
		created_at=getattr(entity, 'created_at', None),
		updated_at=getattr(entity, 'updated_at', None)
	)
    
def row_to_entity(row: List[Any]) -> User:

	if len(row) >= 9:
		user_inv_id = row[0]
		role_inv_id = row[1]
		first_name = row[2]
		last_name = row[3]
		username = row[4]
		password = row[5]
		created_at = row[6] if row[6] is not None else _dt.now()
		updated_at = row[7] if row[7] is not None else _dt.now()
		role_val = row[8]
	else:
		user_inv_id = row[0] if len(row) > 0 else None
		role_inv_id = row[1] if len(row) > 1 else 0
		first_name = row[2] if len(row) > 2 else ""
		last_name = row[3] if len(row) > 3 else None
		username = row[4] if len(row) > 4 else ""
		password = ""
		created_at = row[5] if len(row) > 5 and row[5] is not None else _dt.now()
		updated_at = row[6] if len(row) > 6 and row[6] is not None else _dt.now()
		role_val = row[7] if len(row) > 7 else None

	role = role_val

	return User(
		user_inv_id=user_inv_id,
		role_inv_id=role_inv_id,
		first_name=first_name,
		last_name=last_name,
		username=username,
		password=password,
		created_at=created_at,
		updated_at=updated_at,
		role_inv=role,
	)

def user_inv_dto_to_entity(dto: UserDTO) -> User:
    return dto_to_entity(dto)

def user_inv_entity_to_dto(entity: User) -> UserDTO:
    return entity_to_dto(entity)