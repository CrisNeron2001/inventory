from core.models.dao.product_dao import ProductDAO
from core.models.dto.product_dto import ProductDTO
from core.models.dto.category_dto import CategoryDTO
from core.models.dto.brand_dto import BrandDTO
from core.models.mapper.product_mapper import dto_to_entity, entity_to_dto
from typing import List
from config.settings import log
import pandas as pd
from services.category_service import CategoryService
from services.brand_service import BrandService


class ProductService:
    def __init__(self):
        self.dao = ProductDAO()
        self.category_service = CategoryService()
        self.brand_service = BrandService()

    def create_product(self, product_dto: ProductDTO) -> ProductDTO | None:
        product = dto_to_entity(product_dto)
        new_product = self.dao.create_product(product)
        if new_product is None:
            log.error(
                "[ProductService.create_product] No se pudo crear el producto (posible SKU duplicado u otro error)."
            )
            return None
        log.info(
            f"[ProductService.create_product] Creando un nuevo producto: {new_product}"
        )
        return entity_to_dto(new_product)

    def get_product_by_id(self, product_id: int) -> ProductDTO | None:
        product = self.dao.get_product_by_id(product_id=product_id)
        log.info(
            f"[ProductService.get_product_by_id] Obteniendo producto por id: {product}"
        )
        return entity_to_dto(product) if product else None

    def get_all_products(self) -> List[ProductDTO]:
        products = self.dao.get_all_products()
        log.info(
            f"[ProductService.get_all_products] Obteniendo todos los productos: {products}"
        )
        return [entity_to_dto(product) for product in products]

    def update_product(self, product_dto: ProductDTO) -> ProductDTO | None:
        pid_raw = getattr(product_dto, "product_id", None)
        pid = int(pid_raw) if pid_raw is not None else None
        if pid is None:
            log.error(
                f"[ProductService.update_product] Falta id de producto: {product_dto}"
            )
            return None

        current = self.dao.get_product_by_id(pid)
        if current is None:
            log.error(
                f"[ProductService.update_product] Producto no encontrado: {product_dto.product_id}"
            )
            return None

        try:
            changed_details = any(
                [
                    str(getattr(current, "name", "") or "")
                    != str(product_dto.name or ""),
                    str(getattr(current, "description", "") or "")
                    != str(product_dto.description or ""),
                    str(getattr(current, "sku", "") or "")
                    != str(product_dto.sku or ""),
                    str(
                        getattr(getattr(current, "category", None), "category_id", None)
                        or ""
                    )
                    != str(
                        getattr(
                            getattr(product_dto, "category", None), "category_id", None
                        )
                        or ""
                    ),
                    str(
                        getattr(getattr(current, "brand", None), "brand_id", None) or ""
                    )
                    != str(
                        getattr(getattr(product_dto, "brand", None), "brand_id", None)
                        or ""
                    ),
                ]
            )
            curr_stock = getattr(current, "stock", None)
            if curr_stock is None:
                curr_stock = getattr(current, "stock", 0)
            dto_stock = getattr(product_dto, "stock", None)
            if dto_stock is None:
                dto_stock = getattr(product_dto, "stock", 0)
            changed_stock = int(curr_stock or 0) != int(dto_stock or 0)
            changed_price = int(getattr(current, "price", 0) or 0) != int(
                product_dto.price or 0
            )
        except Exception:
            changed_details = True
            changed_stock = True
            changed_price = True

            allowed = True
        else:
            perm_map = {
                "details": "product.update_details",
                "stock": "product.update_stock",
                "price": "product.update_price",
            }
            changes = {
                "details": changed_details,
                "stock": changed_stock,
                "price": changed_price,
            }
            allowed = True
            for key, changed in changes.items():
                if changed:
                    perm_map[key]
                    allowed = False
                    break

        if not allowed:
            log.error(
                f"[ProductService.update_product] Usuario sin permisos para modificar producto {product_dto.product_id}"
            )
            return None

        product = dto_to_entity(product_dto)
        updated_product = self.dao.edit_product(product=product)
        log.info(
            f"[ProductService.update_product] Modificando producto: {updated_product}"
        )
        return entity_to_dto(updated_product) if updated_product else None

    def edit_product_stock_by_name(self, name: str) -> ProductDTO | None:
        product_stock = self.dao.edit_product_stock_by_name(name)
        log.info(
            f"[ProductService.edit_product_stock_by_name] Modificando disponibilidad del producto: {product_stock}"
        )
        return entity_to_dto(product_stock) if product_stock else None

    def decrease_stock(self, product_id: int, qty: int) -> bool:
        try:
            pid = int(product_id) if product_id is not None else None
        except Exception:
            return False

        if pid is None:
            log.error(
                f"[ProductService.decrease_stock] Producto no encontrado o inválido={product_id}"
            )
            return False

        product = self.get_product_by_id(pid)
        if not product:
            log.error(
                f"[ProductService.decrease_stock] Producto no encontrado para disminuir stock: product_id={pid}"
            )
            return False

        try:
            current_stock = int(getattr(product, "stock", 0) or 0)
        except Exception:
            current_stock = 0

        try:
            decrease = int(qty or 0)
        except Exception:
            decrease = 0

        if decrease <= 0:
            log.info(
                f"[ProductService.decrease_stock] Cantidad a disminuir inválida: {decrease}"
            )
            return False

        new_stock = current_stock - decrease
        if new_stock < 0:
            new_stock = 0

        try:
            setattr(product, "stock", new_stock)
            updated = self.update_product(product)
            if updated:
                log.info(
                    f"[ProductService.decrease_stock] Creando stock para el producto={pid}: {current_stock} -> {new_stock}"
                )
                return True
            else:
                log.error(
                    f"[ProductService.decrease_stock] No se pudo actualizar el stock para product_id={pid}"
                )
                return False
        except Exception as e:
            log.error(
                f"[ProductService.decrease_stock] Error disminuyendo stock para product_id={pid}: {e}"
            )
            return False

    def delete_product(self, product_id: int) -> bool | None:
        product = self.dao.delete_product(product_id=product_id)
        log.info(f"[ProductService.delete_product] Removiendo producto: {product}")
        return True if product else False

    def import_products_form_excel(self, file_path: str) -> List[ProductDTO]:
        df = pd.read_excel(file_path)
        categories = self.category_service.get_all_categories()
        brands = self.brand_service.get_all_brands()
        products = []
        if not isinstance(df, pd.DataFrame):
            log.error(
                f"[ProductService.import_products_form_excel] Error al leer el archivo Excel: {df}"
            )
            return products
        else:
            for _, row in df.iterrows():
                try:
                    category_name = str(row.get("category_name", "")).strip()
                    brand_name = str(row.get("brand_name", "")).strip()
                    catogory_id = int(row.get("category_id", 0) or 0)
                    brand_id = int(row.get("brand_id", 0) or 0)
                    category = next(
                        (c for c in categories if c.name == category_name), None
                    )
                    if not category and category_name:
                        log.info(f"Creando categoria inexistente: {category_name}")
                        new_category_dto = CategoryDTO(
                            category_id=catogory_id, name=category_name
                        )
                        category = self.category_service.create_category(
                            new_category_dto
                        )
                        if category:
                            categories.append(category)
                    brand = next((b for b in brands if b.name == brand_name), None)
                    if not brand and brand_name:
                        log.info(f"Creando marca inexistente: {brand_name}")
                        new_brand_dto = BrandDTO(brand_id=brand_id, name=brand_name)
                        brand = self.brand_service.create_brand(new_brand_dto)
                        if brand:
                            brands.append(brand)
                    stock_value: int | None = row.get("stock", 0)
                    price_value: int | None = row.get("price", 0)
                    product_dto = ProductDTO(
                        product_id=None,
                        name=str(row.get("name", "")).strip(),
                        description=str(row.get("description", "")).strip(),
                        stock=int(stock_value) if stock_value is not None else 0,
                        price=int(price_value) if price_value is not None else 0,
                        sku=str(row.get("sku", "")).strip(),
                        category=category,
                        brand=brand,
                    )
                    created_product = self.create_product(product_dto)
                    if created_product:
                        products.append(created_product)
                except Exception as e:
                    log.error(
                        f"[ProductService.import_products_form_excel] Error al procesar la fila: {e}"
                    )
            return products
