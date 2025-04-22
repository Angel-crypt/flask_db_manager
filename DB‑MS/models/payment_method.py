from models import BaseModel
from services import get_db_connection
from mysql.connector.errors import IntegrityError


class PaymentMethod(BaseModel):
    """Modelo para la tabla payment_method"""

    table_name = "payment_method"

    @classmethod
    def get_by_id(cls, payment_method_id):
        """Obtiene un método de pago por su ID"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT * FROM payment_method WHERE id = %s",
                (payment_method_id,)
            )
            return cursor.fetchone()
        except Exception as e:
            raise Exception(f"Error getting payment method: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def get_all(cls):
        """Obtiene todos los métodos de pago disponibles"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM payment_method")
            return cursor.fetchall()
        except Exception as e:
            raise Exception(f"Error getting payment methods: {str(e)}")
        finally:
            cursor.close()
            conn.close()


class UserPaymentMethod(BaseModel):
    """Modelo para la tabla user_payment_method"""

    table_name = "user_payment_method"

    @classmethod
    def get_user_payment_methods(cls, user_id):
        """Obtiene todos los métodos de pago de un usuario"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
                SELECT upm.id, upm.user_id, upm.payment_method_id, upm.is_primary,
                       pm.name, pm.type
                FROM user_payment_method upm
                JOIN payment_method pm ON upm.payment_method_id = pm.id
                WHERE upm.user_id = %s
            """
            cursor.execute(query, (user_id,))
            return cursor.fetchall()
        except Exception as e:
            raise Exception(f"Error getting user payment methods: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def get_user_payment_method(cls, user_id, payment_method_id):
        """Obtiene un método de pago específico de un usuario"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
                SELECT upm.id, upm.user_id, upm.payment_method_id, upm.is_primary,
                       pm.name, pm.type
                FROM user_payment_method upm
                JOIN payment_method pm ON upm.payment_method_id = pm.id
                WHERE upm.user_id = %s AND upm.payment_method_id = %s
            """
            cursor.execute(query, (user_id, payment_method_id))
            return cursor.fetchone()
        except Exception as e:
            raise Exception(f"Error getting user payment method: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def add_payment_method(cls, user_id, payment_method_data):
        """Crea un nuevo método de pago y lo asocia al usuario"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Primero creamos el método de pago
            cursor.execute(
                "INSERT INTO payment_method (name, type) VALUES (%s, %s)",
                (payment_method_data["name"], payment_method_data["type"])
            )
            payment_method_id = cursor.lastrowid

            # Verificamos si es el método de pago principal
            is_primary = payment_method_data.get("is_primary", 0)

            # Si es el principal, actualizamos cualquier otro método principal a no principal
            if is_primary == 1:
                cursor.execute(
                    "UPDATE user_payment_method SET is_primary = 0 WHERE user_id = %s AND is_primary = 1",
                    (user_id,)
                )

            # Luego lo asociamos al usuario
            cursor.execute(
                "INSERT INTO user_payment_method (user_id, payment_method_id, is_primary) VALUES (%s, %s, %s)",
                (user_id, payment_method_id, is_primary)
            )

            conn.commit()
            return payment_method_id
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error adding payment method: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def update_payment_method(cls, user_id, payment_method_id, payment_method_data):
        """Actualiza un método de pago de un usuario"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Verificamos que el método de pago exista y pertenezca al usuario
            query = """
                SELECT upm.id
                FROM user_payment_method upm
                WHERE upm.user_id = %s AND upm.payment_method_id = %s
            """
            cursor.execute(query, (user_id, payment_method_id))
            if not cursor.fetchone():
                raise Exception(
                    "Payment method not found or does not belong to user")

            # Actualizamos el método de pago
            update_fields = []
            update_values = []

            if "name" in payment_method_data:
                update_fields.append("name = %s")
                update_values.append(payment_method_data["name"])

            if "type" in payment_method_data:
                update_fields.append("type = %s")
                update_values.append(payment_method_data["type"])

            if update_fields:
                update_query = f"UPDATE payment_method SET {', '.join(update_fields)} WHERE id = %s"
                update_values.append(payment_method_id)
                cursor.execute(update_query, tuple(update_values))

            # Si se especifica is_primary, actualizamos la relación
            if "is_primary" in payment_method_data and payment_method_data["is_primary"] == 1:
                # Primero quitamos el estado primary de otros métodos
                cursor.execute(
                    "UPDATE user_payment_method SET is_primary = 0 WHERE user_id = %s AND is_primary = 1",
                    (user_id,)
                )
                # Luego establecemos este método como primary
                cursor.execute(
                    "UPDATE user_payment_method SET is_primary = 1 WHERE user_id = %s AND payment_method_id = %s",
                    (user_id, payment_method_id)
                )

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error updating payment method: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def delete_payment_method(cls, user_id, payment_method_id):
        """Elimina un método de pago de un usuario"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Verificamos que el método de pago exista y pertenezca al usuario
            query = """
                SELECT upm.id, upm.is_primary
                FROM user_payment_method upm
                WHERE upm.user_id = %s AND upm.payment_method_id = %s
            """
            cursor.execute(query, (user_id, payment_method_id))
            result = cursor.fetchone()
            if not result:
                raise Exception(
                    "Payment method not found or does not belong to user")

            # Verificamos si el método de pago está siendo utilizado en alguna compra
            cursor.execute(
                "SELECT COUNT(*) FROM purchase WHERE payment_method_id = %s",
                (payment_method_id,)
            )
            if cursor.fetchone()[0] > 0:
                raise Exception(
                    "Cannot delete payment method that is used in purchases")

            # Eliminamos la relación entre el usuario y el método de pago
            cursor.execute(
                "DELETE FROM user_payment_method WHERE user_id = %s AND payment_method_id = %s",
                (user_id, payment_method_id)
            )

            # Eliminamos el método de pago
            cursor.execute(
                "DELETE FROM payment_method WHERE id = %s",
                (payment_method_id,)
            )

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error deleting payment method: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def set_primary_payment_method(cls, user_id, payment_method_id):
        """Establece un método de pago como principal para un usuario"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Verificamos que el método de pago exista y pertenezca al usuario
            query = """
                SELECT upm.id
                FROM user_payment_method upm
                WHERE upm.user_id = %s AND upm.payment_method_id = %s
            """
            cursor.execute(query, (user_id, payment_method_id))
            if not cursor.fetchone():
                raise Exception(
                    "Payment method not found or does not belong to user")

            # Quitamos el estado primary de todos los métodos de pago del usuario
            cursor.execute(
                "UPDATE user_payment_method SET is_primary  = 0 WHERE user_id = %s",
                (user_id,)
            )

            # Establecemos este método como primary
            cursor.execute(
                "UPDATE user_payment_method SET is_primary  = 1 WHERE user_id = %s AND payment_method_id = %s",
                (user_id, payment_method_id)
            )

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error setting primary payment method: {str(e)}")
        finally:
            cursor.close()
            conn.close()
