from models.base_model import BaseModel
from services import get_db_connection
from mysql.connector.errors import IntegrityError
from datetime import timedelta

class Content(BaseModel):
    """Modelo para la tabla Content"""

    table_name = "content"