import os
from dotenv import load_dotenv
from config.settings import log
from psycopg2 import (
	connect,
	OperationalError
)
from core.exceptions.exception import (
	PermanentFailure,
	DatabaseFailure,
	ConnectionFailure
)

class DatabaseConnection:
    db_conn= None
    load_dotenv()
    
    @classmethod
    def get_connection_db(cls):
        if cls.db_conn is None or getattr(cls.db_conn, "closed", 1) != 0:
            cls.db_conn = cls.create_connection_db()
        return cls.db_conn
    
    @classmethod
    def create_connection_db(cls):
        try:
            log.info("[DatabaseConnection.create_connection_db] Conectando base de datos.")
            db_conn = connect(
                host=os.environ.get('PG_HOST'),
                port=os.environ.get('PG_PORT'),
                user=os.environ.get('PG_USER'),
                password=os.environ.get('PG_PASSWORD'),
                database=os.environ.get('PG_DATABASE')
			)
            cls.db_conn = db_conn
            log.info(f"[DatabaseConnection.create_connection_db] Conección exitosa: \n{db_conn}.")
            return db_conn
        except OperationalError as e:
            error_msg = str(e).lower()
            if 'authentication' in error_msg:
                log.error("[DatabaseConnection.create_connection_db] Credenciales de la base de datos incorrectas: %s", e)
                raise DatabaseFailure("non-retryable") from e
            else:
                log.error("[DatabaseConnection.create_connection_db] Error operacional: %s", e)
                raise ConnectionFailure("non-retryable") from e
        except Exception as e:
            log.critical(" [DatabaseConnection.create_connection_db] Un error desconocido: %s", e)
            raise PermanentFailure("non-retryable") from e
        
    @classmethod
    def close_connection_db(cls):
        if cls.db_conn and not cls.db_conn.close():
            cls.db_conn.close()
            log.info("[DatabaseConnection.close_connection_db] Conección cerrada.")
            cls.db_conn = None
