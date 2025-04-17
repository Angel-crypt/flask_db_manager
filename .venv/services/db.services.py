import os
import mysql.connector
from mysql.connector import Error as MySQLError
from contextlib import contextmanager
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos desde variables de entorno
db_config = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', '12345'),
    'database': os.environ.get('DB_NAME', 'filmHUB_db'),
    'port': int(os.environ.get('DB_PORT', 3360))
}


def get_db_connection():
    """
    Establece y retorna una conexión a la base de datos
    """
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except MySQLError as e:
        raise Exception(f"Error connecting to MySQL database: {e}")


@contextmanager
def db_transaction():
    """
    Context manager para manejar transacciones de base de datos
    
    Uso:
    with db_transaction() as cursor:
        cursor.execute("INSERT INTO...")
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()
