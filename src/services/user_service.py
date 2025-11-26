from core.models.dao.user_dao import UserDAO
from core.models.dto.user_dto import UserDTO
from core.models.mapper.user_mapper import dto_to_entity, entity_to_dto
from typing import List
from config.settings import log
import bcrypt

class UserService:
    def __init__(self):
        self.dao = UserDAO()

    def _hash_password(self, plain: str) -> str:
        if isinstance(plain, str):
            hashed = bcrypt.hashpw(plain.encode('utf-8'), bcrypt.gensalt())
            return hashed.decode('utf-8')
        return plain

    def _verify_password(self, plain: str, hashed: str) -> bool:
        try:
            return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False

    def create_user(self, user_dto: UserDTO) -> UserDTO | None:
        user_dto.password = self._hash_password(user_dto.password)
        user = dto_to_entity(user_dto)
        new_user = self.dao.create_user(user=user)
        log.info(f"Nuevo usuario creado: {new_user}")
        dto = entity_to_dto(new_user) if new_user else None
        if dto:
            dto.password = ""
        return dto

    def get_user_by_id(self, user_id: int) -> UserDTO | None:
        user = self.dao.get_user_by_id(user_id=user_id)
        log.info(f"Usuario obtenido por id: {user}")
        dto = entity_to_dto(user) if user else None
        if dto:
            dto.password = ""
        return dto

    def get_user_by_username(self, username: str) -> UserDTO | None:
        user = self.dao.get_user_by_username(username=username)
        log.info(f"Usuario obtenido por username: {user}")
        dto = entity_to_dto(user) if user else None
        if dto:
            dto.password = ""
        return dto

    def login(self, username: str, password: str) -> UserDTO | None:
        user_entity = self.dao.get_user_by_username(username=username)
        if not user_entity:
            log.info(f"Login fallido: usuario {username} no existe")
            return None
        if self._verify_password(password, user_entity.password):
            dto = entity_to_dto(user_entity)
            dto.password = ""
            log.info(f"Login exitoso: {username}")
            return dto
        else:
            log.info(f"Login fallido: credenciales invalidas para {username}")
            return None

    def get_all_users(self) -> List[UserDTO]:
        users = self.dao.get_all_users()
        log.info(f"Obtenidos todos los usuarios: {users}")
        dtos = [entity_to_dto(user) for user in users]
        for d in dtos:
            d.password = ""
        return dtos

    def update_user(self, user_dto: UserDTO) -> UserDTO | None:
        if user_dto.password:
            user_dto.password = self._hash_password(user_dto.password)
        user = dto_to_entity(user_dto)
        updated_user = self.dao.edit_user(user=user)
        log.info(f"Usuario actualizado: {updated_user}")
        dto = entity_to_dto(updated_user) if updated_user else None
        if dto:
            dto.password = ""
        return dto

    def delete_user(self, user_id: int) -> bool | None:
        deleted = self.dao.delete_user(user_id=user_id)
        log.info(f"Usuario eliminado: {deleted}")
        return True if deleted else False
