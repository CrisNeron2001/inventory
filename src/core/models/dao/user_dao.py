from typing import Optional, List, Any
from core.database.connections import DatabaseConnection
from core.database.queries import (
	insert_user_inv,
	select_user_by_id,
	select_user_by_username,
	select_all_users,
	update_user_inv,
	update_user_role,
	delete_user_inv
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
			log.info("Creando un nuevo usuario.")
			self.cursor.execute(
				insert_user_inv,
				(
					(user.role_inv.role_inv_id if user.role_inv else None),
					user.first_name,
					user.last_name,
					user.username,
					user.password,
				),
			)
			self.db_conn.commit()
			row: Any = self.cursor.fetchone()
			user_created = row_to_entity(row=list(row))
			log.info(f"Usuario creado: {user_created}")
			return user_created
		else:
			log.error("Error al crear usuario.")
			return None

	def get_user_by_id(self, user_id: int) -> Optional[User]:
		if self.cursor and self.db_conn:
			log.info("Obteniendo usuario por id.")
			self.cursor.execute(select_user_by_id, (user_id,))
			row: Any = self.cursor.fetchone()
			if not row:
				return None
			user = row_to_entity(row=list(row))
			log.info(f"Usuario obtenido: {user}")
			return user
		else:
			log.error("Error al obtener usuario por id.")
			return None

	def get_user_by_username(self, username: str) -> Optional[User]:
		if self.cursor and self.db_conn:
			log.info("Obteniendo usuario por username.")
			self.cursor.execute(select_user_by_username, (username,))
			row: Any = self.cursor.fetchone()
			if not row:
				return None
			user = row_to_entity(row=list(row))
			log.info(f"Usuario obtenido por username: {user}")
			return user
		else:
			log.error("Error al obtener usuario por username.")
			return None

	def get_all_users(self) -> List[User]:
		if self.cursor and self.db_conn:
			log.info("Obteniendo todos los usuarios.")
			self.cursor.execute(select_all_users)
			rows: List[Any] = self.cursor.fetchall()
			users = [row_to_entity(list(r)) for r in rows]
			log.info(f"Usuarios obtenidos: {users}")
			return users
		else:
			log.error("Error al obtener usuarios.")
			return []

	def edit_user(self, user: User) -> Optional[User]:
		if self.cursor and self.db_conn:
			log.info("Editando usuario.")
			self.cursor.execute(
				update_user_inv,
				(
					(user.role_inv.role_inv_id if user.role_inv else (getattr(user, 'role_inv_id', None))),
					user.first_name,
					user.last_name,
					user.username,
					user.password,
					user.user_inv_id,
				),
			)
			self.db_conn.commit()
			row: Any = self.cursor.fetchone()
			if not row:
				return None
			user_updated = row_to_entity(row=list(row))
			log.info(f"Usuario actualizado: {user_updated}")
			return user_updated
		else:
			log.error("Error al editar usuario.")
			return None

	def update_role(self, user_id: int, role_inv_id: int) -> Optional[User]:
		"""Update only role_inv_id for a user and return the updated User entity (including password).
		This avoids overwriting the password when only changing role."""
		if self.cursor and self.db_conn:
			log.info(f"Actualizando role_inv_id para user_id={user_id} -> role_inv_id={role_inv_id}")
			self.cursor.execute(update_user_role, (role_inv_id, user_id))
			self.db_conn.commit()
			row: Any = self.cursor.fetchone()
			if not row:
				log.warning(f"No se actualizó role para user_id={user_id}")
				return None
			user_updated = row_to_entity(row=list(row))
			log.info(f"Role actualizado para usuario: {user_updated}")
			return user_updated
		else:
			log.error("Error al actualizar role de usuario: sin conexión DB.")
			return None

	def delete_user(self, user_id: int) -> bool:
		if self.cursor and self.db_conn:
			log.info("Eliminando usuario.")
			self.cursor.execute(delete_user_inv, (user_id,))
			self.db_conn.commit()
			deleted = self.cursor.rowcount > 0
			log.info(f"Usuario eliminado: {deleted}")
			return deleted
		else:
			log.error("Error al eliminar usuario.")
			return False
