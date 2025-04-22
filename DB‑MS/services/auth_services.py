import os
import jwt
from datetime import datetime, timedelta
from flask import request, jsonify
from functools import wraps

# Configuraciones para JWT
SECRET_KEY = os.environ.get("SECRET_KEY")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION = 24  # horas


def generate_token(user_id):
    """
    Genera un token JWT para el usuario
    """
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_token(token):
    """
    Decodifica y valida un token JWT
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_current_user():
    """
    Obtiene el usuario actual desde el token de autorización
    """
    from models import User
    
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ")[1]

    payload = decode_token(token)
    if not payload:
        return None

    user_id = payload.get("user_id")
    if not user_id:
        return None

    return User.get_by_id(user_id)


def token_required(f):
    """
    Decorador para requerir un token válido en las rutas
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        current_user = get_current_user()

        if current_user is None:
            return jsonify({"error": "Authentication required"}), 401

        return f(current_user, *args, **kwargs)

    return decorated


def admin_required(f):
    """
    Decorador para requerir un token válido y rol de administrador
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        current_user = get_current_user()

        if current_user is None:
            return jsonify({"error": "Authentication required"}), 401

        if current_user.get("role", "").lower() != "admin":
            return jsonify({"error": "Admin privileges required"}), 403

        return f(current_user, *args, **kwargs)

    return decorated
