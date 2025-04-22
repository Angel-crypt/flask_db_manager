from flask import Blueprint, request, jsonify
from services.email_service import send_reset_email, send_success_email
from services.token_service import generate_reset_token, verify_reset_token
from dotenv import load_dotenv
import requests
import os

load_dotenv()

password_bp = Blueprint('password', __name__)
DB_URL = os.getenv("DB_MS_URL")


@password_bp.route("/request-reset", methods=["POST"])
def request_password_reset():
    email = request.json.get("email")
    if not email:
        return jsonify({"error": "Email is required"}), 400

    # Verificar si el email existe (con db-ms)
    res = requests.get(
        f"{DB_URL}/users/by-email",
        params={"email": email},
        headers={"X-API-KEY": os.getenv("DB_MS_API_KEY")}
    )
    if res.status_code != 200:
        return jsonify({"error": "User not found"}), 404

    token = generate_reset_token(email)
    send_reset_email(email, token)
    return jsonify({"message": "Reset email sent"}), 200

@password_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    token = data.get("token")
    new_password = data.get("password")

    email = verify_reset_token(token)
    if not email:
        return jsonify({"error": "Invalid or expired token"}), 400

    # Actualizar contraseña en DB
    res = requests.put(
        f"{DB_URL}/users/update-password",
        json={"email": email, "password": new_password},
        headers={"X-API-KEY": os.getenv("DB_MS_API_KEY")}
    )
    send_success_email(email)

    if res.status_code != 200:
        return jsonify({"error": "Could not reset password"}), 500

    return jsonify({"message": "Password updated"}), 200
