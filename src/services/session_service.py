from typing import Optional, Set
import os
import json
from datetime import datetime, timedelta
from config.settings import log
from services.permission_service import PermissionService
from services.user_service import UserService
from services.role_service import RoleService
from core.models.dto.user_dto import UserDTO

class SessionService:
	_instance = None

	def __new__(cls):
		if cls._instance is None:
			cls._instance = super(SessionService, cls).__new__(cls)
			cls._instance._initialized = False
		return cls._instance

	def __init__(self):
		if getattr(self, "_initialized", False):
			return
		self._initialized = True
		self.current_user: Optional[UserDTO] = None
		self._permissions: Set[str] = set()
		self._perm_service = PermissionService()
		try:
			self._session_file = os.path.join(os.getcwd(), ".session.json")
		except (OSError, PermissionError) as ex:
			log.error(f"[SessionService.__init__] No se pudo determinar el directorio de trabajo actual, volviendo al nombre de archivo local: {ex}")
			self._session_file = ".session.json"

		try:
			self._load_persistent_session()
		except (FileNotFoundError, json.JSONDecodeError, ValueError, OSError, TypeError) as ex:
			log.info(f"[SessionService.__init__] No se cargó ninguna sesión persistente: {ex}")

	def set_current_user(self, user: Optional[UserDTO]) -> None:
		self.current_user = user
		self._permissions = set()
		if user:
			try:
				if not getattr(user, "role_inv", None) and getattr(user, "role_inv_id", None) is not None:
					rs = RoleService()
					role_id_val = getattr(user, "role_inv_id", None)
					if role_id_val is not None:
						resolved = rs.get_role_by_id(int(role_id_val))
						if resolved:
							user.role_inv = resolved
				raw_role_id = None
				if getattr(user, "role_inv", None):
					raw_role_id = getattr(user.role_inv, "role_inv_id", None)
				if raw_role_id is None:
					raw_role_id = getattr(user, "role_inv_id", None)

				role_id: int = int(raw_role_id) if raw_role_id is not None else 0
				perms = self._perm_service.get_permissions_for_role(role_id)
				if perms:
					self._permissions = set(perms)
				log.info(f"Cargando permiso por el rol {role_id}: {self._permissions}")
			except (AttributeError, ValueError, TypeError) as ex:
				rid = getattr(getattr(user, "role_inv", None), "role_inv_id", getattr(user, "role_inv_id", None))
				log.error(f"[SessionService.set_current_user] Error al cargar permisos para el rol {rid}: {ex}")
		try:
			if user:
				self._persist_session(user_id=user.user_inv_id, days=14)
			else:
				if os.path.exists(self._session_file):
					os.remove(self._session_file)
		except (OSError, TypeError, ValueError) as ex:
			log.error(f"[SessionService.set_current_user] Error en la sesión persistente: {ex}")

	def clear(self) -> None:
		self.current_user = None
		self._permissions = set()
		try:
			if hasattr(self, "_session_file") and os.path.exists(self._session_file):
				os.remove(self._session_file)
		except OSError as ex:
			log.error(f"[SessionService.clear] Error al eliminar el archivo de sesión: {ex}")

	def logout(self) -> None:
		try:
			self.clear()
			log.info("[SessionService.logout] El usuario cerró sesión y se borró la sesión persistente.")
		except OSError as ex:
			log.error(f"[SessionService.logout] Error al cerrar sesión: {ex}")

	def get_current_user(self) -> Optional[UserDTO]:
		return self.current_user

	def has_permission(self, permission_key: str) -> bool:
		if not permission_key:
			return False
		return permission_key in self._permissions

	def _persist_session(self, user_id: Optional[int], days: int = 14) -> None:
		try:
			if user_id is None:
				return
			data = {
				"user_inv_id": int(user_id),
				"expires_at": (datetime.now() + timedelta(days=days)).isoformat(),
			}
			with open(self._session_file, "w", encoding="utf-8") as f:
				json.dump(data, f)
		except (OSError, TypeError, ValueError) as ex:
			log.error(f"[SessionService._persist_session] No se pudo escribir el archivo de sesión: {ex}")

	def _load_persistent_session(self) -> None:
		if not hasattr(self, "_session_file"):
			return
		if not os.path.exists(self._session_file):
			return
		try:
			with open(self._session_file, "r", encoding="utf-8") as f:
				data = json.load(f)
			expires_at = data.get("expires_at")
			if not expires_at:
				return
			exp = datetime.fromisoformat(expires_at)
			if datetime.now() > exp:
				try:
					os.remove(self._session_file)
				except OSError as ex_rm:
					log.error(f"[SessionService._load_persistent_session] No se pudo eliminar el archivo de sesión caducado: {ex_rm}")
				return
			user_id = data.get("user_inv_id")
			if user_id is None:
				return
			svc = UserService()
			user = svc.get_user_by_id(int(user_id))
			if user:
				self.current_user = user
				try:
					if not getattr(user, "role_inv", None) and getattr(user, "role_inv_id", None) is not None:
						rs = RoleService()
						role_id_val = getattr(user, "role_inv_id", None)
						if role_id_val is not None:
							resolved = rs.get_role_by_id(int(role_id_val))
							if resolved:
								user.role_inv = resolved

					raw_role_id = None
					if getattr(user, "role_inv", None):
						raw_role_id = getattr(user.role_inv, "role_inv_id", None)
					if raw_role_id is None:
						raw_role_id = getattr(user, "role_inv_id", None)

					role_id: int = int(raw_role_id) if raw_role_id is not None else 0
					perms = self._perm_service.get_permissions_for_role(role_id)
					if perms:
						self._permissions = set(perms)
					log.info(f"[SessionService._load_persistent_session] Cargando permisos para la función de sesión restaurada {role_id}: {self._permissions}")
				except (AttributeError, ValueError, TypeError) as ex:
					log.error(f"[SessionService._load_persistent_session] Error al cargar permisos para la sesión restaurada: {ex}")
				log.info(f"[SessionService._load_persistent_session] Restaurando sesión persistente para el usuario {user_id}")
		except (OSError, json.JSONDecodeError, ValueError, TypeError, AttributeError) as ex:
			log.error(f"[SessionService._load_persistent_session] No se pudo cargar el archivo de sesión: {ex}")
