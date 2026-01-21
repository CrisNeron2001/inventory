from core.models.dao.permission_dao import PermissionDAO
from core.models.dto.permission_dto import PermissionDTO
from core.models.mapper.permission_mapper import dto_to_entity, entity_to_dto
from typing import List
from config.settings import log
from services.role_service import RoleService


class PermissionService:
    def __init__(self):
        self.dao = PermissionDAO()

    def create_permission(self, permission_dto: PermissionDTO) -> bool:
        created = self.dao.create_permission(permission_key=permission_dto.permission_key, description=permission_dto.description)
        log.info(f"[PermissionService.create_permission] Creando un nuevo permiso: {permission_dto.permission_key} -> {created}")
        return created

    def get_permission(self, permission_key: str) -> PermissionDTO | None:
        perm = self.dao.get_permission(permission_key=permission_key)
        log.info(f"[PermissionService.get_permission] Obteniendo permiso: {perm}")
        return entity_to_dto(perm) if perm else None

    def get_all_permissions(self) -> List[PermissionDTO]:
        perms = self.dao.get_all_permissions()
        return [entity_to_dto(p) for p in perms]

    def assign_permission(self, role_inv_id: int, permission_key: str) -> bool:
        assigned = self.dao.assign_permission_to_role(role_inv_id=role_inv_id, permission_key=permission_key)
        log.info(f"[PermissionService.assign_permission] Asignando un permiso {permission_key} al rol {role_inv_id}: {assigned}")
        return assigned

    def get_permissions_for_role(self, role_inv_id: int) -> List[str]:
        return self.dao.get_permissions_by_role(role_inv_id=role_inv_id)

    def remove_permission(self, role_inv_id: int, permission_key: str) -> bool:
        removed = self.dao.remove_permission_from_role(role_inv_id=role_inv_id, permission_key=permission_key)
        log.info(f"[PermissionService.remove_permission] Removiendo permiso {permission_key} del rol {role_inv_id}: {removed}")
        return removed

    def assign_permissions(self, role_inv_id: int, permission_keys: List[str]) -> bool:
        results: List[bool] = []
        for pk in permission_keys:
            try:
                res = self.assign_permission(role_inv_id=role_inv_id, permission_key=pk)
                results.append(bool(res))
            except Exception as e:
                log.error(f"[PermissionService.assign_permissions] Error al asignar el permiso {pk} a rol {role_inv_id}: {e}")
                results.append(False)
        all_ok = all(results)
        log.info(f"[PermissionService.assign_permissions] Permiso asignado en el rol {role_inv_id}: {permission_keys} -> {all_ok}")
        return all_ok

    def replace_permissions(self, role_inv_id: int, permission_keys: List[str]) -> bool:
        try:
            current = self.get_permissions_for_role(role_inv_id=role_inv_id)
            for existing in current:
                if existing not in permission_keys:
                    try:
                        self.remove_permission(role_inv_id=role_inv_id, permission_key=existing)
                    except Exception as e:
                        log.error(f"[PermissionService.replace_permissions] Error al remover permiso {existing} del rol {role_inv_id}: {e}")
            for pk in permission_keys:
                if pk not in current:
                    try:
                        self.assign_permission(role_inv_id=role_inv_id, permission_key=pk)
                    except Exception as e:
                        log.error(f"[PermissionService.replace_permissions] Error al asignar permiso {pk} al rol {role_inv_id}: {e}")
            log.info(f"[PermissionService.replace_permissions] Permiso reemplazado por el rol {role_inv_id} -> {permission_keys}")
            return True
        except Exception as e:
            log.error(f"[PermissionService.replace_permissions] Error al reemplazar los permisos por rol {role_inv_id}: {e}")
            return False

    def assign_permissions_by_role_name(self, role_name: str, permission_keys: List[str]) -> bool:
        try:
            rs = RoleService()
            roles = rs.get_all_roles()
            target = None
            for r in roles:
                if getattr(r, 'name', '').strip().lower() == role_name.strip().lower():
                    target = r
                    break
            if not target or getattr(target, 'role_inv_id', None) is None:
                log.error(f"[PermissionService.assign_permissions_by_role_name] Rol no encontrado por rol: {role_name}")
                return False
            role_id = int(getattr(target, 'role_inv_id'))
            return self.assign_permissions(role_inv_id=role_id, permission_keys=permission_keys)
        except Exception as e:
            log.error(f"[PermissionService.assign_permissions_by_role_name] Error al asignar el rol {role_name}: {e}")
            return False

    def replace_permissions_by_role_name(self, role_name: str, permission_keys: List[str]) -> bool:
        try:
            rs = RoleService()
            roles = rs.get_all_roles()
            target = None
            for r in roles:
                if getattr(r, 'name', '').strip().lower() == role_name.strip().lower():
                    target = r
                    break
            if not target or getattr(target, 'role_inv_id', None) is None:
                log.error(f"[PermissionService.replace_permissions_by_role_name] Rol no encontrado por rol: {role_name}")
                return False
            role_id = int(getattr(target, 'role_inv_id'))
            return self.replace_permissions(role_inv_id=role_id, permission_keys=permission_keys)
        except Exception as e:
            log.error(f"[PermissionService.replace_permissions_by_role_name] Error al reemplazar por el rol {role_name}: {e}")
            return False
