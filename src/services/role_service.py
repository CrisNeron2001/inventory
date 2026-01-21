from core.models.dao.role_dao import RoleDAO
from core.models.dto.role_dto import RoleDTO
from core.models.mapper.role_mapper import dto_to_entity, entity_to_dto
from typing import List
from config.settings import log


class RoleService:
    def __init__(self):
        self.dao = RoleDAO()

    def create_role(self, role_dto: RoleDTO) -> RoleDTO | None:
        role = dto_to_entity(role_dto)
        new_role = self.dao.create_role(role=role)
        log.info(f"[RoleService.create_role] Creando un nuevo rol: {new_role}")
        return entity_to_dto(new_role) if new_role else None

    def get_role_by_id(self, role_id: int) -> RoleDTO | None:
        role = self.dao.get_role_by_id(role_id=role_id)
        log.info(f"[RoleService.get_role_by_id] Obteniendo un rol por id: {role}")
        return entity_to_dto(role) if role else None

    def get_all_roles(self) -> List[RoleDTO]:
        roles = self.dao.get_all_roles()
        log.info(f"[RoleService.get_all_roles] Obteniendo todos los roles: {roles}")
        return [entity_to_dto(role) for role in roles]

    def update_role(self, role_dto: RoleDTO) -> RoleDTO | None:
        role = dto_to_entity(role_dto)
        updated_role = self.dao.edit_role(role=role)
        log.info(f"[RoleService.update_role] Modificando un rol: {updated_role}")
        return entity_to_dto(updated_role) if updated_role else None

    def delete_role(self, role_id: int) -> bool | None:
        deleted = self.dao.delete_role(role_id=role_id)
        log.info(f"[RoleService.delete_role] Removiendo un rol: {deleted}")
        return True if deleted else False
