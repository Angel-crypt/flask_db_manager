# app.py
import os
from flask import Flask, jsonify
from dotenv import load_dotenv
from routes.auth_routes import auth_bp
from routes.users_routes import users_bp
from routes.payment_routes import payment_bp
from routes.content_routes import content_bp
from routes.purchase_routes import purchase_bp
from routes.wish_list_routes import wish_list_bp

# Cargar variables de entorno
load_dotenv()


def create_app():
    """Crea y configura la aplicación Flask"""
    app = Flask(__name__)

    # Configuración secreta
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

    # Manejo global de errores
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({'error': 'Internal server error'}), 500

    # Registrar blueprints
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(users_bp, url_prefix='/api')
    app.register_blueprint(payment_bp, url_prefix='/api')
    app.register_blueprint(content_bp, url_prefix='/api')
    app.register_blueprint(purchase_bp, url_prefix='/api')
    app.register_blueprint(wish_list_bp, url_prefix='/api')

    # Ruta de estado/salud
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'ok', 'service': 'blockbuster-api'})

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get('PORT', 8000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get(
        'FLASK_DEBUG', 'False').lower() == 'true')
