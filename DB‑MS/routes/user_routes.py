from flask import Blueprint, request, jsonify
from models import User
from services import admin_required, token_required

users_bp = Blueprint('users', __name__)

@users_bp.route("/admin/users", methods=["GET"])
@admin_required
def get_users(current_user):
    """Obtener todos los usuarios (solo admin)"""
    try:
        users = User.get_all()

        # Transformar fechas y eliminar contraseñas
        users_list = []
        for user in users:
            user_data = {
                "id": user["id"],
                "name": user["name"],
                "surname": user["surname"],
                "genre": user["genre"],
                "date_born": user["date_born"].strftime('%d-%m-%Y'),
                "date_enrollment": user["date_enrollment"].strftime('%d-%m-%Y %H:%M:%S'),
                "phone": user["phone"],
                "email": user["email"],
                "role": user["role"]
            }
            users_list.append(user_data)

        return jsonify(users_list), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@users_bp.route("/admin/users/<int:user_id>", methods=["GET"])
@admin_required
def get_user(current_user, user_id):
    """Obtener un usuario por ID (solo admin)"""
    try:
        user = User.get_by_id(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Eliminar contraseña de la respuesta
        user_data = {
            "id": user["id"],
            "name": user["name"],
            "surname": user["surname"],
            "genre": user["genre"],
            "date_born": user["date_born"].strftime('%d-%m-%Y'),
            "date_enrollment": user["date_enrollment"].strftime('%d-%m-%Y %H:%M:%S'),
            "phone": user["phone"],
            "email": user["email"],
            "role": user["role"]
        }

        return jsonify(user_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@users_bp.route("/users/profile", methods=["GET"])
@token_required
def get_profile(current_user):
    """Obtener perfil del usuario autenticado"""
    try:
        # Eliminar contraseña de la respuesta
        user_data = {
            "id": current_user["id"],
            "name": current_user["name"],
            "surname": current_user["surname"],
            "genre": current_user["genre"],
            "date_born": current_user["date_born"].strftime('%d-%m-%Y'),
            "date_enrollment": current_user["date_enrollment"].strftime('%d-%m-%Y %H:%M:%S'),
            "phone": current_user["phone"],
            "email": current_user["email"],
            "role": current_user["role"]
        }

        return jsonify(user_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@users_bp.route("/users/profile", methods=["PUT"])
@token_required
def update_profile(current_user):
    """Actualizar perfil del usuario autenticado"""
    data = request.get_json()

    # Campos que el usuario puede actualizar de su perfil
    allowed_fields = ["name", "surname", "genre", "date_born", "phone"]
    update_data = {k: v for k, v in data.items() if k in allowed_fields}

    # Si se quiere cambiar contraseña
    if "password" in data:
        # Hashear nueva contraseña
        try:
            # La contraseña será hasheada en el método User.create_user
            update_data["password"] = data["password"]
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    try:
        rows_updated = User.update(current_user["id"], update_data)

        if rows_updated == 0:
            return jsonify({"error": "No changes made"}), 400

        return jsonify({"message": "Profile updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@users_bp.route("/admin/users/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(current_user, user_id):
    """Eliminar un usuario (solo admin)"""
    try:
        rows_deleted = User.delete(user_id)

        if rows_deleted == 0:
            return jsonify({"error": "User not found"}), 404

        return jsonify({"message": "User deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
