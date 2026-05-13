import flet as ft
from gui.router.app_router import AppRouter
from core.database.setup import DatabaseSetup


def main(page: ft.Page):
    db_setup = DatabaseSetup()
    db_setup.execute_check_entities()
    page.title = "Inventario"
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
    router = AppRouter(page)
    router.start()


ft.app(main)
