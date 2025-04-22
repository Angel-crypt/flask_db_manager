from models.base_model import BaseModel
from services import get_db_connection
from datetime import datetime, timedelta
import calendar


class Purchase(BaseModel):
    """Modelo para la tabla purchase"""

    table_name = "purchase"

    @classmethod
    def create_purchase(cls, user_id, user_payment_method_id=None):
        """
        Crea compras para todos los items en el carrito del usuario
        Si no se especifica un user_payment_method_id, se usa el método de pago principal del usuario
        """
        from models import ShoppingCart
        from models import UserPaymentMethod
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            # Obtener el carrito con items
            cart = ShoppingCart.get_cart_with_items(user_id)

            if not cart or not cart.get("items"):
                raise Exception("Shopping cart is empty")

            # Si no se especifica un método de pago, obtener el método principal
            if user_payment_method_id is None:
                payment_methods = UserPaymentMethod.get_user_payment_methods(
                    user_id)
                primary_methods = [
                    pm for pm in payment_methods if pm.get("is_primary")]

                if not primary_methods:
                    if not payment_methods:
                        raise Exception("No payment methods available")
                    user_payment_method_id = payment_methods[0]["payment_method_id"]
                else:
                    user_payment_method_id = primary_methods[0]["payment_method_id"]
            else:
                # Asegurarse de que el método de pago pertenezca al usuario
                payment_method = UserPaymentMethod.get_user_payment_method(
                    user_id, user_payment_method_id)
                if not payment_method:
                    raise Exception(
                        "Payment method not found or does not belong to user")

                user_payment_method_id = payment_method["id"]

            purchase_ids = []

            for item in cart.get("items", []):
                # Verificar disponibilidad
                cursor.execute(
                    "SELECT status FROM content WHERE id = %s",
                    (item["content_id"],)
                )
                content = cursor.fetchone()

                if not content or content["status"] != "available":
                    raise Exception(
                        f"Content '{item['title']}' is not available for purchase")

                # Crear compra
                cursor.execute(
                    """
                    INSERT INTO purchase (user_id, user_payment_method_id, content_id, unit_price, amount)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (user_id, user_payment_method_id,
                     item["content_id"], item["unit_price"], item["amount"])
                )
                purchase_ids.append(cursor.lastrowid)

                # Cambiar estado a 'unavailable'
                cursor.execute(
                    "UPDATE content SET status = 'unavailable' WHERE id = %s",
                    (item["content_id"],)
                )

            # Limpiar carrito
            ShoppingCart.clear_cart(user_id)

            conn.commit()
            return purchase_ids

        except Exception as e:
            conn.rollback()
            raise Exception(f"Error creating purchase: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def get_user_purchases(cls, user_id):
        """Obtiene todas las compras de un usuario con detalles del contenido"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
                SELECT p.*, c.title, c.classification, c.release_date, c.url_image, c.type,
                       pm.name as payment_method_name, pm.type as payment_method_type
                FROM purchase p
                JOIN content c ON p.content_id = c.id
                JOIN user_payment_method upm ON p.user_payment_method_id = upm.id
                JOIN payment_method pm ON upm.payment_method_id = pm.id
                WHERE p.user_id = %s
                ORDER BY p.purchase_date DESC
            """

            cursor.execute(query, (user_id,))
            purchases = cursor.fetchall()

            # Formatear fechas y otros datos para la respuesta
            result = []
            for purchase in purchases:
                result.append({
                    "id": purchase["id"],
                    "user_id": purchase["user_id"],
                    "payment_method": {
                        "id": purchase["user_payment_method_id"],
                        "name": purchase["payment_method_name"],
                        "type": purchase["payment_method_type"]
                    },
                    "content": {
                        "id": purchase["content_id"],
                        "title": purchase["title"],
                        "classification": purchase["classification"],
                        "release_date": purchase["release_date"].strftime('%d-%m-%Y'),
                        "url_image": purchase["url_image"],
                        "type": purchase["type"]
                    },
                    "unit_price": purchase["unit_price"],
                    "amount": purchase["amount"],
                    "total_price": purchase["unit_price"] * purchase["amount"],
                    "purchase_date": purchase["purchase_date"].strftime('%d-%m-%Y %H:%M:%S')
                })

            return result

        except Exception as e:
            raise Exception(f"Error getting user purchases: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def get_purchase_by_id(cls, purchase_id, user_id=None):
        """
        Obtiene una compra específica por su ID
        Si se proporciona user_id, valida que la compra pertenezca a ese usuario
        """
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
                SELECT p.*, c.title, c.classification, c.release_date, c.summary, 
                       c.url_image, c.status, c.type,
                       pm.name as payment_method_name, pm.type as payment_method_type
                FROM purchase p
                JOIN content c ON p.content_id = c.id
                JOIN user_payment_method upm ON p.user_payment_method_id = upm.id
                JOIN payment_method pm ON upm.payment_method_id = pm.id
                WHERE p.id = %s
            """
            params = [purchase_id]

            if user_id:
                query += " AND p.user_id = %s"
                params.append(user_id)

            cursor.execute(query, tuple(params))
            purchase = cursor.fetchone()

            if not purchase:
                return None

            # Formatear para la respuesta
            result = {
                "id": purchase["id"],
                "user_id": purchase["user_id"],
                "payment_method": {
                    "id": purchase["user_payment_method_id"],
                    "name": purchase["payment_method_name"],
                    "type": purchase["payment_method_type"]
                },
                "content": {
                    "id": purchase["content_id"],
                    "title": purchase["title"],
                    "classification": purchase["classification"],
                    "release_date": purchase["release_date"].strftime('%d-%m-%Y'),
                    "summary": purchase["summary"],
                    "url_image": purchase["url_image"],
                    "status": purchase["status"],
                    "type": purchase["type"]
                },
                "unit_price": purchase["unit_price"],
                "amount": purchase["amount"],
                "total_price": purchase["unit_price"] * purchase["amount"],
                "purchase_date": purchase["purchase_date"].strftime('%d-%m-%Y %H:%M:%S')
            }

            return result

        except Exception as e:
            raise Exception(f"Error getting purchase: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def get_purchase_by_date(cls, purchase_date, user_id=None):
        """
        Obtiene una compra específica por su fecha de compra (+-10 segundos de margen)
        Si se proporciona user_id, valida que la compra pertenezca a ese usuario.
        Soporta fechas con un día, mes o año específicos.
        """
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            # Detectar si la fecha es día, mes, o año
            try:
                purchase_date_obj = datetime.strptime(
                    purchase_date, '%d-%m-%Y %H:%M:%S')
                # Especificación exacta de fecha (día, mes, año)
                start_time = purchase_date_obj - timedelta(seconds=10)
                end_time = purchase_date_obj + timedelta(seconds=10)
            except ValueError:
                try:
                    purchase_date_obj = datetime.strptime(
                        purchase_date, '%d-%m-%Y')  # Solo día, mes, año
                    start_time = purchase_date_obj - timedelta(seconds=10)
                    end_time = purchase_date_obj + timedelta(seconds=10)
                except ValueError:
                    try:
                        purchase_date_obj = datetime.strptime(
                            purchase_date, '%m-%Y')  # Solo mes y año
                        start_time = datetime(
                            purchase_date_obj.year, purchase_date_obj.month, 1)
                        end_time = datetime(purchase_date_obj.year, purchase_date_obj.month,
                                            calendar.monthrange(purchase_date_obj.year, purchase_date_obj.month)[1])
                    except ValueError:
                        # Solo año
                        purchase_date_obj = datetime.strptime(
                            purchase_date, '%Y')
                        start_time = datetime(purchase_date_obj.year, 1, 1)
                        end_time = datetime(
                            purchase_date_obj.year, 12, 31, 23, 59, 59)

            query = """
                SELECT p.*, c.title, c.classification, c.release_date, c.summary, 
                       c.url_image, c.status, c.type,
                       pm.name as payment_method_name, pm.type as payment_method_type
                FROM purchase p
                JOIN content c ON p.content_id = c.id
                JOIN user_payment_method upm ON p.user_payment_method_id = upm.id
                JOIN payment_method pm ON upm.payment_method_id = pm.id
                WHERE p.purchase_date BETWEEN %s AND %s
            """
            params = [start_time, end_time]

            if user_id:
                query += " AND p.user_id = %s"
                params.append(user_id)

            cursor.execute(query, tuple(params))
            purchase = cursor.fetchone()

            if not purchase:
                return None

            # Formatear para la respuesta
            result = {
                "id": purchase["id"],
                "user_id": purchase["user_id"],
                "payment_method": {
                    "id": purchase["user_payment_method_id"],
                    "name": purchase["payment_method_name"],
                    "type": purchase["payment_method_type"]
                },
                "content": {
                    "id": purchase["content_id"],
                    "title": purchase["title"],
                    "classification": purchase["classification"],
                    "release_date": purchase["release_date"].strftime('%d-%m-%Y'),
                    "summary": purchase["summary"],
                    "url_image": purchase["url_image"],
                    "status": purchase["status"],
                    "type": purchase["type"]
                },
                "unit_price": purchase["unit_price"],
                "amount": purchase["amount"],
                "total_price": purchase["unit_price"] * purchase["amount"],
                "purchase_date": purchase["purchase_date"].strftime('%d-%m-%Y %H:%M:%S')
            }

            return result

        except Exception as e:
            raise Exception(f"Error getting purchase: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def get_all_purchases(cls):
        """Obtiene todas las compras en el sistema (solo para administradores)"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
                SELECT p.*, u.name, c.title, pm.name AS payment_method_name, pm.type AS payment_method_type
                FROM purchase p
                JOIN users u ON p.user_id = u.id
                JOIN content c ON p.content_id = c.id
                JOIN user_payment_method upm ON p.user_payment_method_id = upm.id
                JOIN payment_method pm ON upm.payment_method_id = pm.id
                ORDER BY p.purchase_date DESC
            """
            cursor.execute(query)
            purchases = cursor.fetchall()

            result = []
            for purchase in purchases:
                result.append({
                    "id": purchase["id"],
                    "user": {
                        "id": purchase["user_id"],
                        "name": purchase["name"]
                    },
                    "payment_method": {
                        "id": purchase["user_payment_method_id"],
                        "name": purchase["payment_method_name"],
                        "type": purchase["payment_method_type"]
                    },
                    "content": {
                        "id": purchase["content_id"],
                        "title": purchase["title"]
                    },
                    "unit_price": purchase["unit_price"],
                    "amount": purchase["amount"],
                    "total_price": purchase["unit_price"] * purchase["amount"],
                    "purchase_date": purchase["purchase_date"].strftime('%d-%m-%Y %H:%M:%S')
                })

            return result

        except Exception as e:
            raise Exception(f"Error getting all purchases: {str(e)}")
        finally:
            cursor.close()
            conn.close()
