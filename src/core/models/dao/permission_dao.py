from typing import Optional, List, Any
from core.database.connections import DatabaseConnection
from core.database.queries import (
    insert_permission,
    select_permission_by_key,
    select_all_permissions,
    insert_role_permission,
    select_permissions_by_role,
    delete_role_permission,
    delete_permission,
)
from core.models.mapper.permission_mapper import row_to_entity
from core.models.entity.permission_entity import Permission
from config.settings import log


class PermissionDAO:
    def __init__(self):
        self.db_conn = DatabaseConnection.get_connection_db()
        self.cursor = self.db_conn.cursor() if self.db_conn else None

    def create_permission(self, permission_key: str, description: Optional[str] = None) -> bool:
        if self.cursor and self.db_conn:
            log.info(f"[PermissionDAO.create_permission] Insertando permiso {permission_key}.")
            self.cursor.execute(insert_permission, (permission_key, description))
            self.db_conn.commit()
            return True
        log.error("[PermissionDAO.create_permission] No hay conexión para crear permiso.")
        return False

    def get_permission(self, permission_key: str) -> Optional[Permission]:
        if self.cursor and self.db_conn:
            self.cursor.execute(select_permission_by_key, (permission_key,))
            row: Any = self.cursor.fetchone()
            if not row:
                return None
            return row_to_entity(list(row))
        return None

    def get_all_permissions(self) -> List[Permission]:
        if self.cursor and self.db_conn:
            self.cursor.execute(select_all_permissions)
            rows: List[Any] = self.cursor.fetchall()
            return [row_to_entity(list(r)) for r in rows]
        return []

    def assign_permission_to_role(self, role_inv_id: int, permission_key: str) -> bool:
        if self.cursor and self.db_conn:
            self.cursor.execute(insert_role_permission, (role_inv_id, permission_key))
            self.db_conn.commit()
            return True
        return False

    def get_permissions_by_role(self, role_inv_id: int) -> List[str]:
        if self.cursor and self.db_conn:
            self.cursor.execute(select_permissions_by_role, (role_inv_id,))
            rows: List[Any] = self.cursor.fetchall()
            return [r[0] for r in rows]
        return []

    def remove_permission_from_role(self, role_inv_id: int, permission_key: str) -> bool:
        if self.cursor and self.db_conn:
            self.cursor.execute(delete_role_permission, (role_inv_id, permission_key))
            self.db_conn.commit()
            return self.cursor.rowcount > 0
        return False

    def delete_permission(self, permission_key: str) -> bool:
        if self.cursor and self.db_conn:
            self.cursor.execute(delete_permission, (permission_key,))
            self.db_conn.commit()
            return self.cursor.rowcount > 0
        return False
