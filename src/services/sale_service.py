from core.models.dao.sale_dao import SaleDAO
from core.models.dto.sale_dto import SaleDTO
from core.models.mapper.sale_mapper import dto_to_entity, entity_to_dto
from typing import List
from config.settings import log
from services.session_service import SessionService
from core.exceptions.exception import AuthorizationFailure

class SaleService:
    def __init__(self):
        self.dao = SaleDAO()

    def create_sale(self, sale_dto: SaleDTO) -> SaleDTO | None:
        if not SessionService().has_permission("sale.create"):
            log.warning("Intento de crear venta sin permiso 'sale.create'.")
            raise AuthorizationFailure("No tienes permisos para registrar ventas.")

        sale = dto_to_entity(sale_dto)
        new_sale = self.dao.create_sale(sale=sale)
        log.info(f"Nueva venta creada: {new_sale}")
        return entity_to_dto(new_sale) if new_sale else None

    def get_sale_by_id(self, sale_id: int) -> SaleDTO | None:
        sale = self.dao.get_sale_by_id(sale_id=sale_id)
        log.info(f"Venta obtenida por id: {sale}")
        return entity_to_dto(sale) if sale else None

    def update_sale(self, sale_dto: SaleDTO) -> SaleDTO | None:
        if not SessionService().has_permission("sale.update"):
            log.warning("Intento de actualizar venta sin permiso 'sale.update'.")
            raise AuthorizationFailure("No tienes permisos para editar ventas.")

        sale = dto_to_entity(sale_dto)
        updated = self.dao.update_sale(sale=sale)
        log.info(f"Venta actualizada: {updated}")
        return entity_to_dto(updated) if updated else None

    def get_all_sales(self) -> List[SaleDTO]:
        sales = self.dao.get_all_sales()
        log.info(f"Obtenidas todas las ventas: {sales}")
        return [entity_to_dto(s) for s in sales]

    def delete_sale(self, sale_id: int) -> bool | None:
        deleted = self.dao.delete_sale(sale_id=sale_id)
        log.info(f"Venta eliminada: {deleted}")
        return True if deleted else False
