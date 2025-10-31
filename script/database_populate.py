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
from services.product_service import ProductService
from core.models.dto.category_dto import CategoryDTO
from core.models.dto.brand_dto import BrandDTO
from core.models.dto.product_dto import ProductDTO


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
			quantity=int(it.get("quantity", 0)),
			price=int(it.get("price", 0)),
			sku=sku,
			is_available=bool(it.get("is_available", True)),
			category=CategoryDTO(category_id=cat_dto.category_id, name=cat_dto.name) if cat_dto else None,
			brand=BrandDTO(brand_id=br_dto.brand_id, name=br_dto.name) if br_dto else None,
		)

		prod_svc.create_product(product_dto)


def main() -> None:
	data_path = os.path.join(CURRENT_DIR, "script.json")
	data = load_seed_data(data_path)

	cat_svc = CategoryService()
	br_svc = BrandService()
	pr_svc = ProductService()

	cat_map = ensure_categories(cat_svc, data.get("categories", []))
	br_map = ensure_brands(br_svc, data.get("brands", []))
	seed_products(pr_svc, cat_map, br_map, data.get("products", []))

	print("Seeding completado.")


if __name__ == "__main__":
	main()
