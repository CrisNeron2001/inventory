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
from services.user_service import UserService
from services.sale_service import SaleService
from services.product_service import ProductService
from config.settings import log
from core.models.dto.category_dto import CategoryDTO
from core.models.dto.brand_dto import BrandDTO
from core.models.dto.product_dto import ProductDTO
from core.models.dto.user_dto import UserDTO
from core.database.connections import DatabaseConnection
from core.models.dao.user_dao import UserDAO
from core.models.dto.sale_dto import SaleDTO


def load_seed_data(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_categories(
    svc: CategoryService, items: list[Dict]
) -> Dict[str, CategoryDTO]:
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


def seed_products(
    prod_svc: ProductService,
    cat_map: Dict[str, CategoryDTO],
    br_map: Dict[str, BrandDTO],
    items: list[Dict],
) -> None:
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
            category=CategoryDTO(category_id=cat_dto.category_id, name=cat_dto.name)
            if cat_dto
            else None,
            brand=BrandDTO(brand_id=br_dto.brand_id, name=br_dto.name)
            if br_dto
            else None,
        )

        prod_svc.create_product(product_dto)


def seed_users(user_svc: UserService, items: list[Dict]) -> None:
    existing = {}
    for u in user_svc.get_all_users():
        un = getattr(u, "rut", "")
        if isinstance(un, str):
            existing[un.strip().lower()] = u

    for it in items:
        rut_raw = it.get("rut")
        rut = str(rut_raw).strip() if rut_raw is not None else ""
        if not rut:
            continue
        if rut.lower() in existing:
            continue

        user_dto = UserDTO(
            user_inv_id=None,
            first_name=str(it.get("first_name") or ""),
            middle_name=str(it.get("middle_name") or ""),
            last_name=str(it.get("last_name") or ""),
            rut=rut,
            password=str(it.get("password") or ""),
        )

        user_svc.create_user(user_dto)


def _str_is_int_like(s: str) -> bool:
    if not isinstance(s, str):
        return False
    return s.lstrip("-").isdigit()


def main() -> None:
    data_path = os.path.join(CURRENT_DIR, "script.json")
    data = load_seed_data(data_path)

    cat_svc = CategoryService()
    br_svc = BrandService()
    pr_svc = ProductService()

    cat_map = ensure_categories(cat_svc, data.get("categories", []))
    br_map = ensure_brands(br_svc, data.get("brands", []))
    seed_products(pr_svc, cat_map, br_map, data.get("products", []))

    user_svc = UserService()
    sale_svc = SaleService()
    cart_svc = CartService()

    cajero = user_svc.get_user_by_rut("cajero")
    carts = cart_svc.get_all_carts()
    if cajero and carts:
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

    print("Seeding completado.")


if __name__ == "__main__":
    main()
