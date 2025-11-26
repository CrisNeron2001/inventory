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
			log.info("Creando un nuevo role.")
			self.cursor.execute(insert_role_inv, (role.name,))
			self.db_conn.commit()
			row: Any = self.cursor.fetchone()
			role_created = row_to_entity(row=list(row))
			log.info(f"Role creado: {role_created}")
			return role_created
		else:
			log.error("Error al crear role.")
			return None

	def get_role_by_id(self, role_id: int) -> Optional[Role]:
		if self.cursor and self.db_conn:
			log.info("Obteniendo role por id.")
			self.cursor.execute(select_role_by_id, (role_id,))
			row: Any = self.cursor.fetchone()
			if not row:
				return None
			role = row_to_entity(row=list(row))
			log.info(f"Role obtenido: {role}")
			return role
		else:
			log.error("Error al obtener role por id.")
			return None

	def get_all_roles(self) -> List[Role]:
		if self.cursor and self.db_conn:
			log.info("Obteniendo todos los roles.")
			self.cursor.execute(select_all_roles)
			rows: List[Any] = self.cursor.fetchall()
			roles = [row_to_entity(list(r)) for r in rows]
			log.info(f"Roles obtenidos: {roles}")
			return roles
		else:
			log.error("Error al obtener roles.")
			return []

	def edit_role(self, role: Role) -> Optional[Role]:
		if self.cursor and self.db_conn:
			log.info("Editando role.")
			self.cursor.execute(update_role_inv, (role.name, role.role_inv_id))
			self.db_conn.commit()
			row: Any = self.cursor.fetchone()
			if not row:
				return None
			role_updated = row_to_entity(row=list(row))
			log.info(f"Role actualizado: {role_updated}")
			return role_updated
		else:
			log.error("Error al editar role.")
			return None

	def delete_role(self, role_id: int) -> bool:
		if self.cursor and self.db_conn:
			log.info("Eliminando role.")
			self.cursor.execute(delete_role_inv, (role_id,))
			self.db_conn.commit()
			deleted = self.cursor.rowcount > 0
			log.info(f"Role eliminado: {deleted}")
			return deleted
		else:
			log.error("Error al eliminar role.")
			return False

