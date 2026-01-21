from core.models.dao.product_dao import ProductDAO
from core.models.dto.product_dto import ProductDTO
from core.models.mapper.product_mapper import dto_to_entity, entity_to_dto
from typing import List
from config.settings import log
from services.session_service import SessionService

class ProductService:
    def __init__(self):
        self.dao = ProductDAO()
    def create_product(self, product_dto: ProductDTO) -> ProductDTO | None:
        product = dto_to_entity(product_dto)
        new_product = self.dao.create_product(product)
        if new_product is None:
            log.error("[ProductService.create_product] No se pudo crear el producto (posible SKU duplicado u otro error).")
            return None
        log.info(f"[ProductService.create_product] Creando un nuevo producto: {new_product}")
        return entity_to_dto(new_product)
    
    def get_product_by_id(self, product_id: int) -> ProductDTO | None:
        product = self.dao.get_product_by_id(product_id=product_id)
        log.info(f"[ProductService.get_product_by_id] Obteniendo producto por id: {product}")
        return entity_to_dto(product) if product else None
    
    def get_all_products(self) -> List[ProductDTO]:
        products = self.dao.get_all_products()
        log.info(f"[ProductService.get_all_products] Obteniendo todos los productos: {products}")
        return [entity_to_dto(product) for product in products]
    
    def update_product(self, product_dto: ProductDTO) -> ProductDTO | None:
        session = SessionService()
        pid_raw = getattr(product_dto, 'product_id', None)
        pid = int(pid_raw) if pid_raw is not None else None
        if pid is None:
            log.error(f"[ProductService.update_product] Falta id de producto: {product_dto}")
            return None

        current = self.dao.get_product_by_id(pid)
        if current is None:
            log.error(f"[ProductService.update_product] Producto no encontrado: {product_dto.product_id}")
            return None

        try:
            changed_details = any([
                str(getattr(current, 'name', '') or '') != str(product_dto.name or ''),
                str(getattr(current, 'description', '') or '') != str(product_dto.description or ''),
                str(getattr(current, 'sku', '') or '') != str(product_dto.sku or ''),
                str(getattr(getattr(current, 'category', None), 'category_id', None) or '') != str(getattr(getattr(product_dto, 'category', None), 'category_id', None) or ''),
                str(getattr(getattr(current, 'brand', None), 'brand_id', None) or '') != str(getattr(getattr(product_dto, 'brand', None), 'brand_id', None) or ''),
            ])
            curr_stock = getattr(current, 'stock', None)
            if curr_stock is None:
                curr_stock = getattr(current, 'stock', 0)
            dto_stock = getattr(product_dto, 'stock', None)
            if dto_stock is None:
                dto_stock = getattr(product_dto, 'stock', 0)
            changed_stock = int(curr_stock or 0) != int(dto_stock or 0)
            changed_price = int(getattr(current, 'price', 0) or 0) != int(product_dto.price or 0)
        except Exception:
            changed_details = True
            changed_stock = True
            changed_price = True

        if session.has_permission('product.update'):
            allowed = True
        else:
            perm_map = {
                'details': 'product.update_details',
                'stock': 'product.update_stock',
                'price': 'product.update_price',
            }
            changes = {'details': changed_details, 'stock': changed_stock, 'price': changed_price}
            allowed = True
            for key, changed in changes.items():
                if changed and not session.has_permission(perm_map[key]):
                    allowed = False
                    break

        if not allowed:
            log.error(f"[ProductService.update_product] Usuario sin permisos para modificar producto {product_dto.product_id}")
            return None

        product = dto_to_entity(product_dto)
        updated_product = self.dao.edit_product(product=product)
        log.info(f"[ProductService.update_product] Modificando producto: {updated_product}")
        return entity_to_dto(updated_product) if updated_product else None

    def edit_product_stock_by_name(self, name: str) -> ProductDTO | None:
        product_stock = self.dao.edit_product_stock_by_name(name)
        log.info(f"[ProductService.edit_product_stock_by_name] Modificando disponibilidad del producto: {product_stock}")
        return entity_to_dto(product_stock) if product_stock else None

    def decrease_stock(self, product_id: int, qty: int) -> bool:
        try:
            pid = int(product_id) if product_id is not None else None
        except Exception:
            return False

        if pid is None:
            log.error(f"[ProductService.decrease_stock] Producto no encontrado o inválido={product_id}")
            return False

        product = self.get_product_by_id(pid)
        if not product:
            log.error(f"[ProductService.decrease_stock] Producto no encontrado para disminuir stock: product_id={pid}")
            return False

        try:
            current_stock = int(getattr(product, 'stock', 0) or 0)
        except Exception:
            current_stock = 0

        try:
            decrease = int(qty or 0)
        except Exception:
            decrease = 0

        if decrease <= 0:
            log.info(f"[ProductService.decrease_stock] Cantidad a disminuir inválida: {decrease}")
            return False

        new_stock = current_stock - decrease
        if new_stock < 0:
            new_stock = 0

        try:
            setattr(product, 'stock', new_stock)
            updated = self.update_product(product)
            if updated:
                log.info(f"[ProductService.decrease_stock] Creando stock para el producto={pid}: {current_stock} -> {new_stock}")
                return True
            else:
                log.error(f"[ProductService.decrease_stock] No se pudo actualizar el stock para product_id={pid}")
                return False
        except Exception as e:
            log.error(f"[ProductService.decrease_stock] Error disminuyendo stock para product_id={pid}: {e}")
            return False
    
    def delete_product(self, product_id: int) -> bool | None:
        if not SessionService().has_permission('product.delete'):
            log.error(f"[ProductService.delete_product] Usuario sin permiso para eliminar producto {product_id}")
            return False
        product = self.dao.delete_product(product_id=product_id)
        log.info(f"[ProductService.delete_product] Removiendo producto: {product}")
        return True if product else False 