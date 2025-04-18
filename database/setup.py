import mysql.connector
from mysql.connector import errorcode
import os

# Configuración de la conexión a MySQL
config = {
    'host': 'localhost',
    'user': 'root',
    'port': 3360,
    'password': '12345'
}

DB_NAME = 'filmHUB_db'
SQL_FILE_PATH = os.path.join(os.path.dirname(
    __file__), 'schema.sql')


def create_database():
    """Crea la base de datos si no existe."""
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        print(f"✅ Base de datos '{DB_NAME}' creada o ya existe.")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("❌ Error de acceso: usuario o contraseña incorrectos.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("❌ La base de datos no existe.")
        else:
            print(f"❌ Error desconocido: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def execute_sql_from_file(file_path):
    """Ejecuta los comandos SQL desde el archivo .sql en la base de datos."""
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '12345',
        'database': DB_NAME,
        'port': 3360
    }

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        with open(file_path, 'r', encoding='utf-8') as sql_file:
            sql_commands = sql_file.read()

        # Ejecutar comandos individuales
        for command in sql_commands.split(';'):
            if command.strip():
                try:
                    cursor.execute(command)
                except mysql.connector.Error as err:
                    print(f"❌ Error al ejecutar: {command[:60]}... -> {err}")

        conn.commit()
        print(f"✅ Archivo '{os.path.basename(file_path)}' ejecutado correctamente.")
    except Exception as e:
        print(f"❌ Error ejecutando el archivo SQL '{file_path}': {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


if __name__ == '__main__':
    create_database()
    execute_sql_from_file(SQL_FILE_PATH)
