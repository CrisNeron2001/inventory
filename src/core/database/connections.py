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
            log.info("Attempting the connection to database")
            db_conn = connect(
                host=os.environ.get('PG_HOST'),
                port=os.environ.get('PG_PORT'),
                user=os.environ.get('PG_USER'),
                password=os.environ.get('PG_PASSWORD'),
                database=os.environ.get('PG_DATABASE')
			)
            cls.db_conn = db_conn
            log.info(f"Connection to database successful: \n{db_conn}")
            return db_conn
        except OperationalError as e:
            error_msg = str(e).lower()
            if 'authentication' in error_msg:
                log.error("Authentication failed: incorrect password or user: %s", e)
                raise DatabaseFailure("non-retryable") from e
            else:
                log.error("Operational error occurred: %s", e)
                raise ConnectionFailure("non-retryable") from e
        except Exception as e:
            log.critical("An error unknown occurred: %s", e)
            raise PermanentFailure("non-retryable") from e
        
    @classmethod
    def close_connection_db(cls):
        if cls.db_conn and not cls.db_conn.close():
            cls.db_conn.close()
            log.info("Database connection closed")
            cls.db_conn = None
