import bcrypt
from models.base_model import BaseModel
from services import get_db_connection
from mysql.connector.errors import IntegrityError

class User(BaseModel):
    """Modelo para la tabla Users"""

    table_name = "users"