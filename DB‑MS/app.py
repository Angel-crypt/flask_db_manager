import os
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from flask_cors import CORS
from models import User
from services import get_db_connection
import bcrypt

from routes import (
    users_bp,
    payment_method_bp,
    content_bp,
    purchase_bp,
    wish_list_bp,
    shopping_cart_bp
)

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    API_KEY = os.getenv("API_KEY")
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({'error': 'Internal server error'}), 500

    # Middleware: proteger todas las rutas /internal/*
    @app.before_request
    def check_api_key():
        if request.path.startswith("/internal/"):
            key = request.headers.get("X-API-KEY")
            if key != API_KEY:
                return jsonify({"error": "Unauthorized"}), 401

    # Crear usuario (interna)
    @app.route("/internal/users", methods=["POST"])
    def create_user_internal():
        data = request.get_json() or {}
        # Mapeo de password_hash → password
        if "password_hash" in data:
            data["password"] = data.pop("password_hash")
        user_id = User.create(data)
        return jsonify({"user_id": user_id}), 201

    # Obtener usuario por email (interna)
    @app.route("/internal/users/by-email", methods=["GET"])
    def get_user_by_email():
        email = request.args.get("email")
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if not user:
            return jsonify({"error": "Not found"}), 404
        # Renombrar password → password_hash
        if "password" in user:
            user["password_hash"] = user.pop("password")
        return jsonify(user)
    
    @app.route("/internal/users/update-password", methods=["PUT"])
    def internal_update_password():
        """Actualizar contraseña por email (uso interno)"""
        data = request.get_json()
        email = data.get("email")
        new_password = data.get("password")

        if not email or not new_password:
            return jsonify({"error": "Email and password required"}), 400

        hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("UPDATE users SET password = %s WHERE email = %s", (hashed, email))
            conn.commit()
            affected_rows = cur.rowcount
            cur.close()
            conn.close()

            if affected_rows == 0:
                return jsonify({"error": "No user updated"}), 404
            return jsonify({"message": "Password updated"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # Obtener usuario por ID (interna)
    @app.route("/internal/users/<int:user_id>", methods=["GET"])
    def get_user_by_id_internal(user_id):
        user = User.get_by_id(user_id)
        if not user:
            return jsonify({"error": "Not found"}), 404
        if "password" in user:
            user["password_hash"] = user.pop("password")
        return jsonify(user)

    #app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(users_bp, url_prefix='/api')
    app.register_blueprint(payment_method_bp, url_prefix='/api')
    app.register_blueprint(content_bp, url_prefix='/api')
    app.register_blueprint(purchase_bp, url_prefix='/api')
    app.register_blueprint(wish_list_bp, url_prefix='/api')
    app.register_blueprint(shopping_cart_bp, url_prefix='/api')

    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'ok', 'service': 'filmHUB-db'}), 200

    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get('PORT', 8001))
    app.run(host="0.0.0.0", port=port, debug=True)