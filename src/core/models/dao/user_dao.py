from typing import Optional, List, Any
from core.database.connections import DatabaseConnection
from core.database.queries import (
    insert_user_inv,
    select_user_by_id,
    select_user_by_rut,
    select_all_users,
    update_user_inv,
    delete_user_inv,
)
from core.models.mapper.user_mapper import row_to_entity
from core.models.entity.user_entity import User
from config.settings import log


class UserDAO:
    def __init__(self):
        self.db_conn = DatabaseConnection.get_connection_db()
        self.cursor = self.db_conn.cursor() if self.db_conn else None

    def create_user(self, user: User) -> Optional[User]:
        if self.cursor and self.db_conn:
            log.info("[UserDAO.create_user] Creando un nuevo usuario.")
            self.cursor.execute(
                insert_user_inv,
                (
                    user.first_name,
                    user.middle_name,
                    user.last_name,
                    user.rut,
                    user.password,
                ),
            )
            self.db_conn.commit()
            row: Any = self.cursor.fetchone()
            user_created = row_to_entity(row=list(row))
            log.info(f"[UserDAO.create_user] Usuario creado: {user_created}.")
            return user_created
        else:
            log.error("[UserDAO.create_user] Error al crear usuario.")
            return None

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        if self.cursor and self.db_conn:
            log.info("[UserDAO.get_user_by_id] Obteniendo usuario por id.")
            self.cursor.execute(select_user_by_id, (user_id,))
            row: Any = self.cursor.fetchone()
            if not row:
                return None
            user = row_to_entity(row=list(row))
            log.info(f"[UserDAO.get_user_by_id] Usuario obtenido: {user}")
            return user
        else:
            log.error("[UserDAO.get_user_by_id] Error al obtener usuario por id.")
            return None

    def get_user_by_rut(self, rut: str) -> Optional[User]:
        if self.cursor and self.db_conn:
            log.info("[UserDAO.get_user_by_rut] Obteniendo usuario por rut.")
            self.cursor.execute(select_user_by_rut, (rut,))
            row: Any = self.cursor.fetchone()
            if not row:
                return None
            user = row_to_entity(row=list(row))
            log.info(f"[UserDAO.get_user_by_rut] Usuario obtenido por rut: {user}.")
            return user
        else:
            log.error("[UserDAO.get_user_by_rut] Error al obtener usuario por rut.")
            return None

    def get_all_users(self) -> List[User]:
        if self.cursor and self.db_conn:
            log.info("[UserDAO.get_all_users] Obteniendo todos los usuarios.")
            self.cursor.execute(select_all_users)
            rows: List[Any] = self.cursor.fetchall()
            users = [row_to_entity(list(r)) for r in rows]
            log.info(f"[UserDAO.get_all_users] Usuarios obtenidos: {users}.")
            return users
        else:
            log.error("[UserDAO.get_all_users] Error al obtener usuarios.")
            return []

    def edit_user(self, user: User) -> Optional[User]:
        if self.cursor and self.db_conn:
            log.info("[UserDAO.edit_user] Editando usuario.")
            self.cursor.execute(
                update_user_inv,
                (
                    user.first_name,
                    user.middle_name,
                    user.last_name,
                    user.rut,
                    user.password,
                    user.user_inv_id,
                ),
            )
            self.db_conn.commit()
            row: Any = self.cursor.fetchone()
            if not row:
                return None
            user_updated = row_to_entity(row=list(row))
            log.info(f"[UserDAO.edit_user] Usuario actualizado: {user_updated}.")
            return user_updated
        else:
            log.error("[UserDAO.edit_user] Error al editar usuario.")
            return None

    def delete_user(self, user_id: int) -> bool:
        if self.cursor and self.db_conn:
            log.info("[UserDAO.delete_user] Eliminando usuario.")
            self.cursor.execute(delete_user_inv, (user_id,))
            self.db_conn.commit()
            deleted = self.cursor.rowcount > 0
            log.info(f"[UserDAO.delete_user] Usuario eliminado: {deleted}.")
            return deleted
        else:
            log.error("[UserDAO.delete_user] Error al eliminar usuario.")
            return False
