from typing import Optional, List, Any
from core.database.connections import DatabaseConnection
from core.database.queries import (
	insert_role_inv,
	select_role_by_id,
	select_all_roles,
	update_role_inv,
	delete_role_inv
)
from core.models.mapper.role_mapper import row_to_entity
from core.models.entity.role_entity import Role
from config.settings import log


class RoleDAO:
	def __init__(self):
		self.db_conn = DatabaseConnection.get_connection_db()
		self.cursor = self.db_conn.cursor() if self.db_conn else None

	def create_role(self, role: Role) -> Optional[Role]:
		if self.cursor and self.db_conn:
			log.info("[RoleDAO.create_role] Creando un nuevo rol.")
			self.cursor.execute(insert_role_inv, (role.name,))
			self.db_conn.commit()
			row: Any = self.cursor.fetchone()
			role_created = row_to_entity(row=list(row))
			log.info(f"[RoleDAO.create_role] Role creado: {role_created}")
			return role_created
		else:
			log.error("[RoleDAO.create_role] Error al crear rol.")
			return None

	def get_role_by_id(self, role_id: int) -> Optional[Role]:
		if self.cursor and self.db_conn:
			log.info("[RoleDAO.get_role_by_id] Obteniendo rol por id.")
			self.cursor.execute(select_role_by_id, (role_id,))
			row: Any = self.cursor.fetchone()
			if not row:
				return None
			role = row_to_entity(row=list(row))
			log.info(f"[RoleDAO.get_role_by_id] Rol obtenido: {role}")
			return role
		else:
			log.error("[RoleDAO.get_role_by_id] Error al obtener rol por id.")
			return None

	def get_all_roles(self) -> List[Role]:
		if self.cursor and self.db_conn:
			log.info("[RoleDAO.get_all_roles] Obteniendo todos los roles.")
			self.cursor.execute(select_all_roles)
			rows: List[Any] = self.cursor.fetchall()
			roles = [row_to_entity(list(r)) for r in rows]
			log.info(f"[RoleDAO.get_all_roles] Roles obtenidos: {roles}.")
			return roles
		else:
			log.error("[RoleDAO.get_all_roles] Error al obtener roles.")
			return []

	def edit_role(self, role: Role) -> Optional[Role]:
		if self.cursor and self.db_conn:
			log.info("[RoleDAO.edit_role] Editando rol.")
			self.cursor.execute(update_role_inv, (role.name, role.role_inv_id))
			self.db_conn.commit()
			row: Any = self.cursor.fetchone()
			if not row:
				return None
			role_updated = row_to_entity(row=list(row))
			log.info(f"[RoleDAO.edit_role] Role actualizado: {role_updated}.")
			return role_updated
		else:
			log.error("[RoleDAO.edit_role] Error al editar rol.")
			return None

	def delete_role(self, role_id: int) -> bool:
		if self.cursor and self.db_conn:
			log.info("[RoleDAO.delete_role] Eliminando rol.")
			self.cursor.execute(delete_role_inv, (role_id,))
			self.db_conn.commit()
			deleted = self.cursor.rowcount > 0
			log.info(f"[RoleDAO.delete_role] Rol eliminado: {deleted}.")
			return deleted
		else:
			log.error("[RoleDAO.delete_role] Error al eliminar rol.")
			return False

