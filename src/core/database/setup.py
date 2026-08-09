import os
from core.database.connections import DatabaseConnection
from core.database.queries import (
    create_category,
    create_brand,
    create_product,
    create_cart,
    create_cart_product,
    create_user_inv,
    create_sale,
    create_indexes,
    checks_tables,
)
from config.settings import log
from core.exceptions.exception import PermanentFailure


class DatabaseSetup:
    def __init__(self):
        self.db_conn = DatabaseConnection()
        self.conn = self.db_conn.get_connection_db()
        self.cursor = self.conn.cursor() if self.conn else None

    def execute_create_entities(self):
        try:
            log.info(
                "[DatabaseSetup.execute_create_entities] Procedimiento de creación de tablas."
            )
            if self.db_conn and self.cursor:
                self.cursor.execute(create_user_inv)
                self.cursor.execute(create_category)
                self.cursor.execute(create_brand)
                self.cursor.execute(create_product)
                self.cursor.execute(create_cart)
                self.cursor.execute(create_cart_product)
                self.cursor.execute(create_sale)
                self.cursor.execute(create_indexes)
                self.conn.commit()
                log.info(
                    "[DatabaseSetup.execute_create_entities] Todas las tablas han sido creadas exitosamente."
                )
            else:
                log.error(
                    "[DatabaseSetup.execute_create_entities] La conexión hacia la base de datos no ha sido establecida."
                )
        except Exception as e:
            log.critical(
                "[DatabaseSetup.execute_create_entities] Un error desconocido ha ocurrido durante el procedimiento: %s",
                e,
            )
            raise PermanentFailure("non-retryable") from e
        finally:
            log.info("[DatabaseSetup.execute_create_entities] Cerrando conexión.")
            self.db_conn.close_connection_db()

    def execute_check_entities(self):
        try:
            log.info(
                "[DatabaseSetup.execute_check_entities] Procedimiento de comprobar tablas existentes."
            )
            if self.cursor:
                self.cursor.execute(checks_tables)
                tables_name: list[str] = [
                    "category",
                    "brand",
                    "product",
                    "role_inv",
                    "user_inv",
                    "cart",
                    "cart_product",
                    "sale",
                    "permission",
                    "role_permission",
                ]
                existing = {row[0] for row in self.cursor.fetchall()}
                missing = set(tables_name) - existing
                if missing:
                    log.info(
                        "[DatabaseSetup.execute_check_entities] Faltan tablas: %s. Procediendo a crearlas.",
                        ", ".join(missing),
                    )
                    self.execute_create_entities()
                else:
                    log.info(
                        "[DatabaseSetup.execute_check_entities] Las tablas ya existen."
                    )
            else:
                log.error(
                    "[DatabaseSetup.execute_check_entities] La conexión hacia la base de datos no ha sido establecida."
                )
        except Exception as e:
            log.critical(
                "[DatabaseSetup.execute_check_entities] Un error desconocido ha ocurrido durante el procedimiento: %s.",
                e,
            )
            raise PermanentFailure("non-retryable") from e
        finally:
            log.info("[DatabaseSetup.execute_check_entities] Cerrando conexión.")
            self.db_conn.close_connection_db()

    def get_db_path(self):
        user_data_dir = os.path.expanduser("~/.MiPuntoVenta")
        if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir)
        return os.path.join(user_data_dir, "inventario.db")
