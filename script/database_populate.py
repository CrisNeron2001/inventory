import os
import sys
import json
from typing import Dict

CURRENT_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "src"))
if SRC_DIR not in sys.path:
	sys.path.insert(0, SRC_DIR)

from services.category_service import CategoryService
from services.brand_service import BrandService
from services.cart_service import CartService
from services.role_service import RoleService
from services.user_service import UserService
from services.sale_service import SaleService
from services.session_service import SessionService
from services.product_service import ProductService
from config.settings import log
from core.models.dto.category_dto import CategoryDTO
from core.models.dto.brand_dto import BrandDTO
from core.models.dto.product_dto import ProductDTO
from core.models.dto.role_dto import RoleDTO
from core.models.dto.user_dto import UserDTO
from core.database.connections import DatabaseConnection
from core.database.queries import insert_permission, insert_role_permission
from core.models.dao.user_dao import UserDAO
from core.models.dto.sale_dto import SaleDTO


def load_seed_data(path: str) -> Dict:
	with open(path, "r", encoding="utf-8") as f:
		return json.load(f)


def ensure_categories(svc: CategoryService, items: list[Dict]) -> Dict[str, CategoryDTO]:
	existing = {c.name.lower(): c for c in svc.get_all_categories()}
	result: Dict[str, CategoryDTO] = {}
	for it in items:
		name = it["name"].strip()
		key = name.lower()
		if key in existing:
			result[key] = existing[key]
			continue
		created = svc.create_category(CategoryDTO(category_id=None, name=name))
		if created:
			result[key] = created
	final = {c.name.lower(): c for c in svc.get_all_categories()}
	return final


def ensure_brands(svc: BrandService, items: list[Dict]) -> Dict[str, BrandDTO]:
	existing = {b.name.lower(): b for b in svc.get_all_brands()}
	result: Dict[str, BrandDTO] = {}
	for it in items:
		name = it["name"].strip()
		key = name.lower()
		if key in existing:
			result[key] = existing[key]
			continue
		created = svc.create_brand(BrandDTO(brand_id=None, name=name))
		if created:
			result[key] = created
	final = {b.name.lower(): b for b in svc.get_all_brands()}
	return final


def seed_products(prod_svc: ProductService, cat_map: Dict[str, CategoryDTO], br_map: Dict[str, BrandDTO], items: list[Dict]) -> None:
	existing = {p.sku: p for p in prod_svc.get_all_products() if p.sku}

	for it in items:
		sku = it.get("sku")
		if sku and sku in existing:
			continue

		category_name = (it.get("category_name") or "").strip().lower()
		brand_name = (it.get("brand_name") or "").strip().lower()
		cat_dto = cat_map.get(category_name)
		br_dto = br_map.get(brand_name)

		product_dto = ProductDTO(
			product_id=None,
			name=it["name"],
			description=it.get("description", ""),
			stock=int(it.get("stock", 0)),
			price=int(it.get("price", 0)),
			sku=sku,
			is_available=bool(it.get("is_available", True)),
			category=CategoryDTO(category_id=cat_dto.category_id, name=cat_dto.name) if cat_dto else None,
			brand=BrandDTO(brand_id=br_dto.brand_id, name=br_dto.name) if br_dto else None,
		)

		prod_svc.create_product(product_dto)


def ensure_roles(svc: RoleService, items: list[Dict]) -> Dict[str, RoleDTO]:
	existing = {}
	for r in svc.get_all_roles():
		name = getattr(r, "name", "")
		if isinstance(name, str):
			existing[name.strip().lower()] = r

	result: Dict[str, RoleDTO] = {}
	for it in items:
		name = it["name"].strip()
		key = name.lower()
		if key in existing:
			result[key] = existing[key]
			continue
		created = svc.create_role(RoleDTO(role_inv_id=None, name=name))
		if created:
			result[key] = created
	final = {}
	for r in svc.get_all_roles():
		name = getattr(r, "name", "")
		if isinstance(name, str):
			final[name.strip().lower()] = r
	return final


def seed_users(user_svc: UserService, role_map: Dict[str, RoleDTO], items: list[Dict]) -> None:
	existing = {}
	for u in user_svc.get_all_users():
		un = getattr(u, "username", "")
		if isinstance(un, str):
			existing[un.strip().lower()] = u

	for it in items:
		username_raw = it.get("username")
		username = str(username_raw).strip() if username_raw is not None else ""
		if not username:
			continue
		if username.lower() in existing:
			continue

		role_name = (it.get("role_name") or "").strip().lower()
		role_dto = role_map.get(role_name)

		role_inv_id = None
		if role_dto is not None:
			raw_role_id = getattr(role_dto, 'role_inv_id', None)
			if raw_role_id is None:
				raw_role_id = getattr(role_dto, 'role_id', None)
			if raw_role_id is not None:
				try:
					role_inv_id = int(raw_role_id)
				except (TypeError, ValueError):
					role_inv_id = None

		user_dto = UserDTO(
			user_inv_id=None,
			role_inv_id=role_inv_id,
			first_name=str(it.get("first_name") or ""),
			last_name=str(it.get("last_name") or ""),
			username=username,
			password=str(it.get("password") or ""),
			role_inv=role_dto, 
		)

		user_svc.create_user(user_dto)


def _str_is_int_like(s: str) -> bool:
	if not isinstance(s, str):
		return False
	return s.lstrip('-').isdigit()


def main() -> None:
	data_path = os.path.join(CURRENT_DIR, "script.json")
	data = load_seed_data(data_path)

	cat_svc = CategoryService()
	br_svc = BrandService()
	pr_svc = ProductService()

	cat_map = ensure_categories(cat_svc, data.get("categories", []))
	br_map = ensure_brands(br_svc, data.get("brands", []))
	seed_products(pr_svc, cat_map, br_map, data.get("products", []))

	role_svc = RoleService()
	user_svc = UserService()
	role_map = ensure_roles(role_svc, data.get("roles", []))
	seed_users(user_svc, role_map, data.get("users", []))

	roles = role_svc.get_all_roles()
	admin_role = next((r for r in roles if getattr(r, 'name', '').strip().lower() in ('administrador', 'admin', 'administrator')), None)
	if admin_role:
		admin_id = getattr(admin_role, 'role_inv_id', None)
		print(f'Rol Administrador id: {admin_id}')

		dao = UserDAO()
		session_file = os.path.join(os.getcwd(), '.session.json')
		user_id = 1
		if os.path.exists(session_file):
			try:
				with open(session_file, 'r', encoding='utf-8') as f:
					j = json.load(f)
			except json.JSONDecodeError:
				j = {}
			user_id_raw = j.get('user_inv_id', user_id)
			if isinstance(user_id_raw, int):
				user_id = user_id_raw
			elif isinstance(user_id_raw, str) and _str_is_int_like(user_id_raw):
				user_id = int(user_id_raw)

		print(f'Actualizar usuario id: {user_id} -> role_id={admin_id}')
		try:
			if admin_id is not None:
				role_val = int(admin_id) if isinstance(admin_id, (int, str)) and (isinstance(admin_id, int) or _str_is_int_like(str(admin_id))) else None
				if role_val is not None:
					updated = dao.update_role(user_id=user_id, role_inv_id=role_val)
					print('Usuario actualizado:', updated)
				else:
					print('Admin id inválido, no se actualizó')
		except Exception as ex:
			print('Error actualizando role via DAO:', ex)
	else:
		print('No se encontró rol Administrador')

	conn = DatabaseConnection.get_connection_db()
	if conn:
		cursor = conn.cursor()
		for p in data.get("permissions", []):
			key = p.get("permission_key")
			desc = p.get("description")
			cursor.execute(insert_permission, (key, desc))
		role_permissions = data.get("role_permissions", {})
		for role_name, perms in role_permissions.items():
			role = role_map.get(role_name.lower())
			if not role or not getattr(role, 'role_inv_id', None):
				continue
			for pk in perms:
					rid = getattr(role, 'role_inv_id', None)
					if rid is not None:
						cursor.execute(insert_role_permission, (int(rid), pk))
			conn.commit()

	sale_svc = SaleService()
	session = SessionService()
	cart_svc = CartService()
	
	cajero = user_svc.get_user_by_username("cajero")
	carts = cart_svc.get_all_carts()
	if cajero and carts:
		session.set_current_user(cajero)
		for i, c in enumerate(carts[:3], start=1):
			cart_id = getattr(c, "cart_id", getattr(c, "cart_id", None))
			product_id = getattr(c, "product_id", getattr(c, "product_id", None))
			unit_price = getattr(c, "price", getattr(c, "unit_price", 0))
			dto = {
				"sale_id": None,
				"cart_id": cart_id,
				"product_id": product_id,
				"quantity": i,
				"unit_price": unit_price,
				"total_price": i * unit_price,
				"notes": "Seed sale",
			}
			sd = SaleDTO(**dto)
			sale_svc.create_sale(sd)
		session.clear()

	print("Seeding completado.")


if __name__ == "__main__":
	main()
