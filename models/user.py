import bcrypt
from models.base_model import BaseModel
from services.db_service import get_db_connection
from mysql.connector.errors import IntegrityError


class User(BaseModel):
    """Modelo para la tabla Users"""

    table_name = "Users"

    @classmethod
    def create_user(cls, user_data):
        """
        Crea un nuevo usuario con la contraseña hasheada
        """
        # Hashear contraseña
        password = user_data.get("password")
        if password:
            hashed_password = bcrypt.hashpw(password.encode(
                'utf-8'), bcrypt.gensalt()).decode('utf-8')
            user_data["password"] = hashed_password

        try:
            return cls.create(user_data)
        except Exception as e:
            if isinstance(e.__cause__, IntegrityError):
                error_message = str(e.__cause__)
                if "Users.phone" in error_message:
                    raise Exception("Phone number already exists")
                elif "Users.mail" in error_message:
                    raise Exception("Email already exists")
            raise e

    @classmethod
    def validate_credentials(cls, email, password):
        """
        Valida las credenciales de un usuario
        """
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("SELECT * FROM Users WHERE mail = %s", (email,))
            user = cursor.fetchone()

            if not user:
                return None

            stored_password = user.get("password", "")

            # Verificar contraseña
            if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                return user

            return None
        except Exception as e:
            raise Exception(f"Error validating credentials: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def is_admin(cls, user_id):
        """
        Verifica si un usuario es administrador
        """
        user = cls.get_by_id(user_id)
        return user and user.get("rol", "").lower() == "admin"
