from models import BaseModel
from services import get_db_connection
from mysql.connector.errors import IntegrityError


class ShoppingCart(BaseModel):
    """Modelo para la tabla shopping_cart y shopping_cart_item"""

    table_name = "shopping_cart"

    @classmethod
    def get_or_create_cart(cls, user_id):
        """Obtiene el carrito del usuario o crea uno nuevo si no existe"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            # Verificar si el usuario ya tiene un carrito
            cursor.execute(
                "SELECT * FROM shopping_cart WHERE user_id = %s",
                (user_id,)
            )
            cart = cursor.fetchone()

            # Si no existe, crear uno nuevo
            if not cart:
                cursor.execute(
                    "INSERT INTO shopping_cart (user_id) VALUES (%s)",
                    (user_id,)
                )
                conn.commit()
                cart_id = cursor.lastrowid

                # Obtener el carrito recién creado
                cursor.execute(
                    "SELECT * FROM shopping_cart WHERE id = %s",
                    (cart_id,)
                )
                cart = cursor.fetchone()

            return cart
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error getting or creating cart: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def get_cart_with_items(cls, user_id):
        """Obtiene el carrito del usuario con todos sus items"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            # Obtener o crear el carrito
            cart = cls.get_or_create_cart(user_id)

            # Obtener los items del carrito con detalles del contenido
            query = """
                SELECT sci.*, c.title, c.classification, c.release_date, 
                    c.summary, c.url_image, c.status, c.type
                FROM shopping_cart_item sci
                JOIN content c ON sci.content_id = c.id
                WHERE sci.cart_id = %s
            """
            cursor.execute(query, (cart["id"],))
            items = cursor.fetchall()

            # Formatear los resultados
            cart_data = {
                "id": cart["id"],
                "user_id": cart["user_id"],
                "date_creation": cart["date_creation"].strftime('%d-%m-%Y %H:%M:%S'),
                "items": []
            }

            total_price = 0
            for item in items:
                # La cantidad siempre es 1, pero usamos item["amount"] para mantener la consistencia
                item_total = item["unit_price"] * item["amount"]
                total_price += item_total

                cart_data["items"].append({
                    "id": item["id"],
                    "content_id": item["content_id"],
                    "title": item["title"],
                    "classification": item["classification"],
                    "release_date": item["release_date"].strftime('%d-%m-%Y'),
                    "summary": item["summary"],
                    "url_image": item["url_image"],
                    "status": item["status"],
                    "type": item["type"],
                    "unit_price": item["unit_price"],
                    "amount": item["amount"],
                    "item_total": item_total
                })

            cart_data["total_price"] = total_price
            cart_data["item_count"] = len(items)

            return cart_data
        except Exception as e:
            raise Exception(f"Error getting cart: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def add_item_to_cart(cls, user_id, content_id):
        """Añade un item al carrito - solo se permite 1 unidad por item"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            # Obtener o crear el carrito
            cart = cls.get_or_create_cart(user_id)
            cart_id = cart["id"]

            # Verificar si el contenido existe y obtener su precio
            cursor.execute(
                "SELECT id, price, status FROM content WHERE id = %s",
                (content_id,)
            )
            content = cursor.fetchone()
            if not content:
                raise Exception("Content not found")
            
            # Verificar si el contenido está disponible
            if content["status"] != "available":
                raise Exception(
                    "Content is unavailable and cannot be added to cart")

            unit_price = content["price"]

            # Verificar si el item ya está en el carrito
            cursor.execute(
                "SELECT * FROM shopping_cart_item WHERE cart_id = %s AND content_id = %s",
                (cart_id, content_id)
            )
            existing_item = cursor.fetchone()

            if existing_item:
                # No permitir agregar más de una unidad
                raise Exception(
                    "Item already exists in cart, cannot add duplicates")
            else:
                # Agregar nuevo item al carrito (cantidad fija = 1)
                cursor.execute(
                    """INSERT INTO shopping_cart_item 
                       (cart_id, content_id, unit_price, amount) 
                       VALUES (%s, %s, %s, 1)""",
                    (cart_id, content_id, unit_price)
                )
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error adding item to cart: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def remove_item_from_cart(cls, user_id, content_id):
        """Elimina un item del carrito basado en el content_id"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Obtener el carrito del usuario
            cart = cls.get_or_create_cart(user_id)

            # Eliminar el item
            cursor.execute(
                "DELETE FROM shopping_cart_item WHERE cart_id = %s AND content_id = %s",
                (cart["id"], content_id)
            )
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error removing item from cart: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def clear_cart(cls, user_id):
        """Elimina todos los items del carrito del usuario"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Obtener el carrito del usuario
            cart = cls.get_or_create_cart(user_id)

            # Eliminar todos los items
            cursor.execute(
                "DELETE FROM shopping_cart_item WHERE cart_id = %s",
                (cart["id"],)
            )
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error clearing cart: {str(e)}")
        finally:
            cursor.close()
            conn.close()
