from models.base_model import BaseModel
from services import get_db_connection
from mysql.connector.errors import IntegrityError

class WishList(BaseModel):
    """Modelo para la tabla wish_list"""

    table_name = "wish_list"

    @classmethod
    def get_user_wish_lists(cls, user_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
                SELECT 
                    name,
                    COUNT(*) AS content_count,
                    MAX(date_creation) AS latest_addition,
                    MIN(date_creation) AS first_addition
                FROM wish_list
                WHERE user_id = %s
                GROUP BY name
                ORDER BY latest_addition DESC
            """
            cursor.execute(query, (user_id,))
            results = cursor.fetchall()
            for row in results:
                row["latest_addition"] = row["latest_addition"].strftime(
                    '%d-%m-%Y %H:%M:%S')
                row["first_addition"] = row["first_addition"].strftime(
                    '%d-%m-%Y %H:%M:%S')
                row["content_count"] = int(row["content_count"])
            return results
        except Exception as e:
            raise Exception(f"Error getting wish lists: {str(e)}")
        finally:
            cursor.close()
            conn.close()


    @classmethod
    def get_wish_list_with_content(cls, wish_list_name=None, user_id=None):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            where_clauses = []
            params = []

            if wish_list_name:
                where_clauses.append("wl.name LIKE %s")
                params.append(f"%{wish_list_name}%")

            if user_id is not None:
                where_clauses.append("wl.user_id = %s")
                params.append(user_id)

            if not where_clauses:
                raise Exception("You must provide either wish_list_name")

            where_clause = " AND ".join(where_clauses)

            query = f"""
                SELECT wl.*, c.id as content_id, c.title, c.classification, 
                    c.release_date, c.summary, c.url_image, c.status, 
                    c.price, c.type
                FROM wish_list wl
                JOIN content c ON wl.content_id = c.id
                WHERE {where_clause}
            """

            cursor.execute(query, tuple(params))
            results = cursor.fetchall()
            if not results:
                return None

            wish_list_data = {
                "user_id": results[0]["user_id"],
                "name": results[0]["name"],
                "date_creation": results[0]["date_creation"].strftime('%d-%m-%Y %H:%M:%S'),
                "content_items": []
            }

            for row in results:
                wish_list_data["content_items"].append({
                    "title": row["title"],
                    "classification": row["classification"],
                    "release_date": row["release_date"].strftime('%d-%m-%Y'),
                    "summary": row["summary"],
                    "url_image": row["url_image"],
                    "status": row["status"],
                    "price": row["price"],
                    "type": row["type"]
                })
            return wish_list_data

        except Exception as e:
            raise Exception(f"Error getting wish list: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def delete(cls, name, user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "DELETE FROM wish_list WHERE name = %s AND user_id = %s",
                (name, user_id)
            )
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error deleting wish list: {str(e)}")
        finally:
            cursor.close()
            conn.close()
    
    @classmethod
    def update(cls, old_name, new_name, user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE wish_list SET name = %s WHERE name = %s AND user_id = %s",
                (new_name, old_name, user_id)
            )
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error updating wish list: {str(e)}")
        finally:
            cursor.close()
            conn.close()


    @classmethod
    def add_content_to_wish_list(cls, wish_list_name, content_id, user_id=None):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
                # Verificar si la lista de deseos existe
                cursor.execute(
                    "SELECT * FROM wish_list WHERE name = %s AND user_id = %s",
                    (wish_list_name, user_id)
                )
                original_wish_list = cursor.fetchone()
                if not original_wish_list:
                    raise Exception(
                        "Wish list not found or does not belong to user")

                # Verificar si el contenido ya está en la lista de deseos
                cursor.execute(
                    "SELECT * FROM wish_list WHERE name = %s AND content_id = %s AND user_id = %s",
                    (wish_list_name, content_id, user_id)
                )
                existing_content = cursor.fetchone()
                if existing_content:
                    raise Exception("Content is already in this wish list")

                # Verificar si el contenido existe en la base de datos
                cursor.execute(
                    "SELECT id FROM content WHERE id = %s", (content_id,))
                if not cursor.fetchone():
                    raise Exception("Content not found")

                # Insertar el contenido en la lista de deseos
                cursor.execute(
                    "INSERT INTO wish_list (user_id, name, content_id, date_creation) VALUES (%s, %s, %s, NOW())",
                    (user_id, original_wish_list["name"], content_id)
                )
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
                conn.rollback()
                raise Exception(f"Error adding content to wish list: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def remove_content_from_wish_list(cls, wish_list_name, content_id, user_id=None):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            where_clause = "name = %s AND content_id = %s"
            params = [wish_list_name, content_id]
            if user_id:
                where_clause += " AND user_id = %s"
                params.append(user_id)

            query = f"DELETE FROM wish_list WHERE {where_clause}"
            cursor.execute(query, tuple(params))
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error removing content from wish list: {str(e)}")
        finally:
            cursor.close()
            conn.close()
