from abc import ABC, abstractmethod
from services import get_db_connection
from mysql.connector import Error as MySQLError


class BaseModel(ABC):
    """Clase base para todos los modelos con operaciones CRUD comunes"""

    table_name = None

    @classmethod
    def get_all(cls, conditions=None):
        """Obtiene todos los registros con condiciones opcionales"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = f"SELECT * FROM {cls.table_name}"
        params = []

        if conditions:
            where_clauses = []
            for key, value in conditions.items():
                where_clauses.append(f"{key} = %s")
                params.append(value)

            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)

        try:
            cursor.execute(query, tuple(params))
            result = cursor.fetchall()
            return result
        except MySQLError as e:
            raise Exception(f"Error al obtener datos: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def get_by_id(cls, id):
        """Obtiene un registro por su ID"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(
                f"SELECT * FROM {cls.table_name} WHERE id = %s", (id,))
            result = cursor.fetchone()
            return result
        except MySQLError as e:
            raise Exception(f"Error al obtener por ID: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def create(cls, data):
        """Crea un nuevo registro"""
        conn = get_db_connection()
        cursor = conn.cursor()

        placeholders = ", ".join(["%s"] * len(data))
        columns = ", ".join(data.keys())
        values = tuple(data.values())

        try:
            query = f"INSERT INTO {cls.table_name} ({columns}) VALUES ({placeholders})"
            cursor.execute(query, values)
            conn.commit()
            return cursor.lastrowid
        except MySQLError as e:
            conn.rollback()
            raise Exception(f"Error al crear: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def update(cls, id, data):
        """Actualiza un registro existente"""
        conn = get_db_connection()
        cursor = conn.cursor()

        set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
        values = list(data.values())
        values.append(id)

        try:
            query = f"UPDATE {cls.table_name} SET {set_clause} WHERE id = %s"
            cursor.execute(query, tuple(values))
            conn.commit()
            return cursor.rowcount
        except MySQLError as e:
            conn.rollback()
            raise Exception(f"Error al actualizar: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def delete(cls, id):
        """Elimina un registro por su ID"""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                f"DELETE FROM {cls.table_name} WHERE id = %s", (id,))
            conn.commit()
            return cursor.rowcount
        except MySQLError as e:
            conn.rollback()
            raise Exception(f"Error al eliminar: {str(e)}")
        finally:
            cursor.close()
            conn.close()
