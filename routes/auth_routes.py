from flask import Blueprint, request, jsonify
from models.user import User
from services import generate_token

auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/auth/login", methods=["POST"])
def login():
    """
    Iniciar sesión y obtener token JWT
    """
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    try:
        user = User.validate_credentials(email, password)

        if not user:
            return jsonify({"error": "Invalid credentials"}), 401

        token = generate_token(user["id"])

        return jsonify({
            "token": token,
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"]
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/auth/logout", methods=["POST"])
def logout():
    """
    Cerrar sesión. El token debe eliminarse del lado cliente.
    """
    return jsonify({"message": "Logout successful. Please delete the token on client side."}), 200


@auth_bp.route("/auth/register", methods=["POST"])
def register():
    """
    Registrar un nuevo usuario
    """
    data = request.get_json()
    required_fields = ["name", "surname", "genre",
                       "date_born", "phone", "email", "password"]

    # Verificar campos requeridos
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    # Por defecto todos los usuarios nuevos son "user"
    data["role"] = "user"

    try:
        user_id = User.create_user(data)

        return jsonify({
            "message": "User registered successfully",
            "user_id": user_id
        }), 201

    except Exception as e:
        # 400 para errores de validación como email duplicado
        return jsonify({"error": str(e)}), 400
