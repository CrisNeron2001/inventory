from core.models.dao.sale_dao import SaleDAO
from core.models.dto.sale_dto import SaleDTO
from core.models.mapper.sale_mapper import dto_to_entity, entity_to_dto
from typing import List
from config.settings import log


class SaleService:
    def __init__(self):
        self.dao = SaleDAO()

    def create_sale(self, sale_dto: SaleDTO) -> SaleDTO | None:
        sale = dto_to_entity(sale_dto)
        new_sale = self.dao.create_sale(sale=sale)
        log.info(f"[SaleService.create_sale] Creando una nueva venta: {new_sale}")
        return entity_to_dto(new_sale) if new_sale else None

    def get_sale_by_id(self, sale_id: int) -> SaleDTO | None:
        sale = self.dao.get_sale_by_id(sale_id=sale_id)
        log.info(f"[SaleService.get_sale_by_id] Obteniendo una venta por id: {sale}")
        return entity_to_dto(sale) if sale else None

    def update_sale(self, sale_dto: SaleDTO) -> SaleDTO | None:
        sale = dto_to_entity(sale_dto)
        updated = self.dao.update_sale(sale=sale)
        log.info(f"[SaleService.update_sale] Modificando venta: {updated}")
        return entity_to_dto(updated) if updated else None

    def get_all_sales(self) -> List[SaleDTO]:
        sales = self.dao.get_all_sales()
        log.info(f"[SaleService.get_all_sales] Obteniendo todas las ventas: {sales}")
        return [entity_to_dto(s) for s in sales]

    def delete_sale(self, sale_id: int) -> bool | None:
        deleted = self.dao.delete_sale(sale_id=sale_id)
        log.info(f"[SaleService.delete_sale] Removiendo venta: {deleted}")
        return True if deleted else False
