from models.base_model import BaseModel
from services import get_db_connection
from mysql.connector.errors import IntegrityError
from datetime import timedelta


class Content(BaseModel):
    """Modelo para la tabla Content"""

    table_name = "content"

    @classmethod
    def search(cls, filters=None):
        """
        Busca contenido con filtros avanzados
        filters: dict con filtros (genre_id, tag_id, director_id, title, id)
        """
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT DISTINCT c.*
            FROM content c
        """

        params = []
        join_clauses = []
        where_clauses = []

        # Agregar joins según filtros
        if filters:
            if filters.get('genre_id'):
                join_clauses.append(
                    "LEFT JOIN content_genre cg ON c.id = cg.content_id")
                where_clauses.append("cg.genre_id = %s")
                params.append(filters['genre_id'])

            if filters.get('tag_id'):
                join_clauses.append(
                    "LEFT JOIN content_tag ct ON c.id = ct.content_id")
                where_clauses.append("ct.tag_id = %s")
                params.append(filters['tag_id'])

            if filters.get('director_id'):
                join_clauses.append(
                    "LEFT JOIN content_director cd ON c.id = cd.content_id")
                where_clauses.append("cd.director_id = %s")
                params.append(filters['director_id'])

            if filters.get('title'):
                where_clauses.append("c.title LIKE %s")
                params.append(f"%{filters['title']}%")

            if filters.get('id'):
                where_clauses.append("c.id = %s")
                params.append(filters['id'])

            if filters.get('status'):
                where_clauses.append("c.status = %s")
                params.append(filters['status'])

            if filters.get('min_price'):
                where_clauses.append("c.price >= %s")
                params.append(filters['min_price'])


            if filters.get('max_price'):
                where_clauses.append("c.price <= %s")
                params.append(filters['max_price'])

            def minutes_to_time_str(minutes):
                t = timedelta(minutes=minutes)
                total_seconds = int(t.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                return f"{hours:02}:{minutes:02}:{seconds:02}"

            if filters.get('min_duration'):
                where_clauses.append("c.duration >= %s")
                params.append(minutes_to_time_str(filters['min_duration']))

            if filters.get('max_duration'):
                where_clauses.append("c.duration <= %s")
                params.append(minutes_to_time_str(filters['max_duration']))


        # Agregar joins a la consulta
        if join_clauses:
            query += " " + " ".join(join_clauses)

        # Agregar condiciones where
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        query += " ORDER BY c.release_date DESC"

        try:
            cursor.execute(query, tuple(params))
            results = cursor.fetchall()
            return results
        except Exception as e:
            raise Exception(f"Error searching content: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_genre_id_by_name(name):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT id
            FROM genre Where name = %s
        """
        params = (name,)
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result[0]['id'] if result else None

    @staticmethod
    def get_tag_id_by_name(name):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT id
            FROM tag Where name = %s
        """
        params = (name,)
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result[0]['id'] if result else None

    @staticmethod
    def get_director_id_by_name(full_name):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Separar el nombre completo en nombre y apellido
        parts = full_name.strip().split()
        if len(parts) < 2:
            # Si solo es un nombre, buscar por el nombre o apellido
            query = "SELECT id FROM director WHERE name = %s OR surname = %s"
            params = (full_name, full_name)
        else:
            name = parts[0]
            surname = " ".join(parts[1:])
            query = "SELECT id FROM director WHERE name = %s AND surname = %s"
            params = (name, surname)

        cursor.execute(query, params)
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return result['id'] if result else None

    @classmethod
    def get_with_details(cls, content_id):
        """
        Obtiene un contenido con todos sus detalles asociados (géneros, etiquetas, directores)
        """
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            # Obtener el contenido base
            cursor.execute("""
                SELECT * FROM content WHERE id = %s
            """, (content_id,))

            content = cursor.fetchone()

            if not content:
                return None

            # Obtener géneros asociados
            cursor.execute("""
                SELECT g.id, g.name
                FROM genre g
                JOIN content_genre cg ON g.id = cg.genre_id
                WHERE cg.content_id = %s
            """, (content_id,))

            genres = cursor.fetchall()
            content['genres'] = genres

            # Obtener etiquetas asociadas
            cursor.execute("""
                SELECT t.id, t.name
                FROM tag t
                JOIN content_tag ct ON t.id = ct.tag_id
                WHERE ct.content_id = %s
            """, (content_id,))

            tags = cursor.fetchall()
            content['tags'] = tags

            # Obtener directores asociados
            cursor.execute("""
                SELECT d.id, d.name, d.surname
                FROM director d
                JOIN content_director cd ON d.id = cd.director_id
                WHERE cd.content_id = %s
            """, (content_id,))

            directors = cursor.fetchall()
            content['directors'] = directors

            return content

        except Exception as e:
            raise Exception(f"Error getting content details: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def create(cls, data):
        """Crea un nuevo contenido en la base de datos"""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            query = """
                INSERT INTO content (title, classification, release_date, duration,
                                    summary, url_image, status, price, type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                data["title"],
                data["classification"],
                data["release_date"],
                data["duration"],
                data["summary"],
                data["url_image"],
                data["status"],
                data["price"],
                data["type"]
            )

            cursor.execute(query, values)
            content_id = cursor.lastrowid  # Obtener el ID del nuevo contenido
            conn.commit()
            return content_id
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error creating content: {str(e)}")
        finally:
            cursor.close()
            conn.close()


    @classmethod
    def add_genre(cls, content_id, genre_id):
        """Asocia un género a un contenido"""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO content_genre (content_id, genre_id) VALUES (%s, %s)",
                (content_id, genre_id)
            )
            conn.commit()
            return True
        except IntegrityError:
            conn.rollback()
            return False  # Ya existe la relación
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error adding genre: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def add_tag(cls, content_id, tag_id):
        """Asocia una etiqueta a un contenido"""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO content_tag (content_id, tag_id) VALUES (%s, %s)",
                (content_id, tag_id)
            )
            conn.commit()
            return True
        except IntegrityError:
            conn.rollback()
            return False  # Ya existe la relación
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error adding tag: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def add_director(cls, content_id, director_id):
        """Asocia un director a un contenido"""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO content_director (content_id, director_id) VALUES (%s, %s)",
                (content_id, director_id)
            )
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error adding director: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def remove_all_relations(cls, content_id):
        """Elimina todas las asociaciones de género, etiqueta y director de un contenido"""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Eliminar asociaciones de géneros
            cursor.execute(
                "DELETE FROM content_genre WHERE content_id = %s", (content_id,))
            # Eliminar asociaciones de etiquetas
            cursor.execute(
                "DELETE FROM content_tag WHERE content_id = %s", (content_id,))
            # Eliminar asociaciones de directores
            cursor.execute(
                "DELETE FROM content_director WHERE content_id = %s", (content_id,))

            # Commit para que se apliquen los cambios
            conn.commit()

            # Retornar el número de filas eliminadas
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error removing all relations: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def remove_genre(cls, content_id, genre_id):
        """Elimina la asociación de un género a un contenido"""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "DELETE FROM content_genre WHERE content_id = %s AND genre_id = %s",
                (content_id, genre_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error removing genre: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def remove_tag(cls, content_id, tag_id):
        """Elimina la asociación de una etiqueta a un contenido"""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "DELETE FROM content_tag WHERE content_id = %s AND tag_id = %s",
                (content_id, tag_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error removing tag: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def remove_director(cls, content_id, director_id):
        """Elimina la asociación de un director a un contenido"""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "DELETE FROM content_director WHERE content_id = %s AND director_id = %s",
                (content_id, director_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error removing director: {str(e)}")
        finally:
            cursor.close()
            conn.close()
