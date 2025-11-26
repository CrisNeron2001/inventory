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
	existing = {r.name.lower(): r for r in svc.get_all_roles()}
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
	final = {r.name.lower(): r for r in svc.get_all_roles()}
	return final


def seed_users(user_svc: UserService, role_map: Dict[str, RoleDTO], items: list[Dict]) -> None:
	existing = {u.username: u for u in user_svc.get_all_users()}
	for it in items:
		username = it.get("username")
		if not username:
			continue
		if username in existing:
			continue

		role_name = (it.get("role_name") or "").strip().lower()
		role_dto = role_map.get(role_name)

		user_dto = UserDTO(
			user_inv_id=None,
			role_inv_id=(int(role_dto.role_inv_id) if role_dto and role_dto.role_inv_id is not None else 0),
			first_name=it.get("first_name", ""),
			last_name=it.get("last_name", ""),
			username=username,
			password=it.get("password", ""),
			role_inv=None,
		)

		user_svc.create_user(user_dto)


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

	# Intentar asignar rol administrador a usuario del archivo de sesión (si aplica)
	try:
		roles = role_svc.get_all_roles()
		admin_role = next((r for r in roles if getattr(r, 'name', '').strip().lower() in ('administrador', 'admin', 'administrator')), None)
		if admin_role:
			admin_id = getattr(admin_role, 'role_inv_id', None)
			print(f'Rol Administrador id: {admin_id}')

			us = user_svc
			session_file = os.path.join(os.getcwd(), '.session.json')
			user_id = 1
			if os.path.exists(session_file):
				try:
					with open(session_file, 'r', encoding='utf-8') as f:
						j = json.load(f)
						user_id = int(j.get('user_inv_id', user_id))
				except Exception:
					pass
			print(f'Actualizar usuario id: {user_id} -> role_id={admin_id}')
			user = us.get_user_by_id(user_id)
		if user:
			try:
				if admin_id is not None:
					try:
						user.role_inv_id = int(admin_id)
					except Exception:
						user.role_inv_id = admin_id
				updated = us.update_user(user)
				print('Usuario actualizado:', updated)
			except Exception as ex:
				print('Error actualizando usuario:', ex)
				try:
					log.error(f'assign_role_to_user error: {ex}')
				except Exception:
					pass
			else:
				print('Usuario no encontrado')
		else:
			print('No se encontró rol Administrador')
	except Exception as e:
		print('Error assign_role_to_user:', e)
		try:
			log.error(f'assign_role_to_user error: {e}')
		except Exception:
			pass

	conn = DatabaseConnection.get_connection_db()
	if conn:
		cursor = conn.cursor()
		for p in data.get("permissions", []):
			key = p.get("permission_key")
			desc = p.get("description")
			try:
				cursor.execute(insert_permission, (key, desc))
			except Exception:
				pass
		role_permissions = data.get("role_permissions", {})
		for role_name, perms in role_permissions.items():
			role = role_map.get(role_name.lower())
			if not role or not getattr(role, 'role_inv_id', None):
				continue
			for pk in perms:
				try:
					rid = getattr(role, 'role_inv_id', None)
					if rid is not None:
						try:
							cursor.execute(insert_role_permission, (int(rid), pk))
						except Exception:
							pass
				except Exception:
					pass
		try:
			conn.commit()
		except Exception:
			pass


	sale_svc = SaleService()
	session = SessionService()
	cart_svc = CartService()
	
	cajero = user_svc.get_user_by_username("cajero")
	carts = cart_svc.get_all_carts()
	if cajero and carts:
		session.set_current_user(cajero)
		for i, c in enumerate(carts[:3], start=1):
			cart_id = getattr(c, "cart_id", getattr(c, "cart_inv_id", None))
			unit_price = getattr(c, "price", getattr(c, "unit_price", 0))
			dto = {
				"sale_id": None,
				"cart_id": cart_id,
				"quantity": i,
				"unit_price": unit_price,
				"total_price": i * unit_price,
				"notes": "Seed sale",
			}
			from core.models.dto.sale_dto import SaleDTO
			sd = SaleDTO(**dto)
			try:
				sale_svc.create_sale(sd)
			except Exception:
				pass
		session.clear()

	print("Seeding completado.")


if __name__ == "__main__":
	main()
