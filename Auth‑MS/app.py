import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mail import Mail
from functools import wraps
from dotenv import load_dotenv
from extensions import create_app, mail
from routes.password_routes import password_bp
from services.auth_services import register_user, authenticate, decode_token

load_dotenv()
app = create_app()
CORS(app)
mail = Mail(app)

app.register_blueprint(password_bp, url_prefix="/auth")

token_blacklist = set()

def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        hdr = request.headers.get("Authorization", "")
        if not hdr.startswith("Bearer "):
            return jsonify({"error": "Authentication required"}), 401

        token = hdr.split()[1]

        if token in token_blacklist:
            return jsonify({"error": "Token has been revoked"}), 401

        payload = decode_token(token)
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401
        return f(payload, *args, **kwargs)
    return wrapper


@app.route("/auth/register", methods=["POST"])
def route_register():
    data = request.get_json()
    try:
        user_id = register_user(data)
        return jsonify({"message": "User registered", "user_id": user_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/auth/login", methods=["POST"])
def route_login():
    data = request.get_json()
    result = authenticate(data.get("email", ""), data.get("password", ""))
    if not result:
        return jsonify({"error": "Invalid credentials"}), 401
    return jsonify(result)

@app.route("/auth/logout", methods=["POST"])
@token_required
def route_logout(payload):
    hdr = request.headers.get("Authorization", "")
    token = hdr.split()[1]
    token_blacklist.add(token)
    return jsonify({"message": "Logged out successfully"}), 200

@app.route("/auth/verify", methods=["GET"])
@token_required
def route_verify(payload):
    return jsonify({"user_id": payload["user_id"], "role": payload["role"]})

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'service': 'filmHUB-auth'}), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8002))
    app.run(host="0.0.0.0", port=port, debug=True)
