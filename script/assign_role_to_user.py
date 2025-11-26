import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from services.role_service import RoleService
from services.user_service import UserService
from config.settings import log

if __name__ == '__main__':
    try:
        rs = RoleService()
        roles = rs.get_all_roles()
        admin_role = None
        for r in roles:
            if getattr(r, 'name', '').strip().lower() == 'administrador':
                admin_role = r
                break
        if not admin_role:
            print('No se encontró rol Administrador')
            sys.exit(1)
        admin_id = getattr(admin_role, 'role_inv_id')
        print(f'Rol Administrador id: {admin_id}')

        us = UserService()
        session_file = os.path.join(os.getcwd(), '.session.json')
        user_id = 1
        if os.path.exists(session_file):
            import json
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            user_id = int(data.get('user_inv_id', user_id))
        print(f'Actualizar usuario id: {user_id} -> role_id={admin_id}')
        user = us.get_user_by_id(user_id)
        if not user:
            print('Usuario no encontrado')
            sys.exit(1)
        user.role_inv_id = int(admin_id)
        updated = us.update_user(user)
        print('Usuario actualizado:', updated)
    except Exception as e:
        print('Error:', e)
        log.error(f'assign_role_to_user error: {e}')