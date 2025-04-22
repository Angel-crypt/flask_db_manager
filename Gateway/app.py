from flask import Flask, request, jsonify, Response
import requests
import os
from dotenv import load_dotenv
from flask_cors import CORS
from routes.azure_QA import azure_QA

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
CORS(app)
app.register_blueprint(azure_QA, url_prefix='/api/azure')

# Dirección del microservicio
FILMHUB_API_URL = os.environ.get(
    "FILMHUB_API_URL", "https://angelcrypt12.pythonanywhere.com/api")
AUTH_API_URL = os.environ.get(
    "AUTH_API_URL", "https://angelcruzr.pythonanywhere.com/")

# Función para manejar las solicitudes hacia la API
def proxy_request(endpoint, method='GET', data=None, params=None):
    url = f"{FILMHUB_API_URL}{endpoint}"

    headers = {}
    # Propagar el token si existe
    if 'Authorization' in request.headers:
        headers['Authorization'] = request.headers['Authorization']

    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, params=params)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=data)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)

        return response.json(), response.status_code
    except requests.RequestException as e:
        return {"error": f"API service error: {str(e)}"}, 503

# Función para manejar las solicitudes hacia la API de Autenticación
def auth_proxy_request(endpoint, method='GET', data=None, params=None):
    url = f"{AUTH_API_URL}{endpoint}"

    headers = {}
    # Propagar el token si existe
    if 'Authorization' in request.headers:
        headers['Authorization'] = request.headers['Authorization']

    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, params=params)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=data)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)

        print(f"Auth API response: {response.status_code} - {response.text}")
        
        return response.json(), response.status_code
    except requests.RequestException as e:
        return {"error": f"Auth API service error: {str(e)}"}, 503

# Rutas de salud/estado
# Ruta interna para saber si el gateway mismo está corriendo
@app.route('/api/health', methods=['GET'])
def health_check():
    """Check the health of the gateway."""
    return jsonify({'status': 'ok', 'service': 'filmHUB-gateway'}), 200

# Ruta extendida para consultar la salud de los otros servicios
@app.route("/health", methods=["GET"])
def gateway_health():
    """Check the health of the gateway and other services."""
    services = {
        'gateway': 'ok',
        'auth': 'unknown',
        'filmhub': 'unknown'
    }
    try:
        res_auth = requests.get(f"{AUTH_API_URL}/api/health", timeout=2)
        services['auth'] = res_auth.json()
    except Exception as e:
        services['auth'] = {'status': 'down', 'error': str(e)}

    try:
        res_filmhub = requests.get(
            f"{FILMHUB_API_URL}/health", timeout=2)
        services['filmhub'] = res_filmhub.json()
    except Exception as e:
        services['filmhub'] = {'status': 'down', 'error': str(e)}

    return jsonify(services), 200 if all(
        isinstance(v, dict) and v.get('status') == 'ok' for v in services.values() if isinstance(v, dict)) else 503

# Rutas de autenticación (redirigidas al microservicio de autenticación)
@app.route("/auth/register", methods=["POST"])
def auth_register():
    return auth_proxy_request("/auth/register", method="POST", data=request.get_json())

@app.route("/auth/login", methods=["POST"])
def auth_login():
    return auth_proxy_request("/auth/login", method="POST", data=request.get_json())

@app.route("/auth/logout", methods=["POST"])
def auth_logout():
    return auth_proxy_request("/auth/logout", method="POST")

@app.route("/auth/verify", methods=["GET"])
def auth_verify():
    return auth_proxy_request("/auth/verify")

@app.route("/auth/request-reset", methods=["POST"])
def auth_request_reset():
    return auth_proxy_request("/auth/request-reset", method="POST", data=request.get_json())

@app.route("/auth/reset-password", methods=["POST"])
def auth_reset_password():
    return auth_proxy_request("/auth/reset-password", method="POST", data=request.get_json())

# Esta ruta se usaría para validar permisos de administrador
@app.route("/auth/check-admin", methods=["GET"])
def check_admin():
    return auth_proxy_request("/auth/check-admin")

# Rutas de usuarios
@app.route("/users/profile", methods=["GET"])
def get_user_profile():
    return proxy_request("/users/profile")

@app.route("/users/profile", methods=["PUT"])
def update_user_profile():
    return proxy_request("/users/profile", method="PUT", data=request.get_json())

# Rutas admin de usuarios (protegidas)
@app.route("/admin/users", methods=["GET"])
def admin_get_users():
    return proxy_request("/admin/users")

@app.route("/admin/users/<int:user_id>", methods=["GET"])
def admin_get_user(user_id):
    return proxy_request(f"/admin/users/{user_id}")

@app.route("/admin/users/<int:user_id>", methods=["DELETE"])
def admin_delete_user(user_id):
    return proxy_request(f"/admin/users/{user_id}", method="DELETE")

# Rutas de métodos de pago
@app.route("/payment-methods", methods=["GET"])
def get_payment_methods():
    return proxy_request("/payment-methods")

@app.route("/payment-methods", methods=["POST"])
def add_payment_method():
    return proxy_request("/payment-methods", method="POST", data=request.get_json())

@app.route("/payment-methods/<int:payment_method_id>", methods=["GET"])
def get_payment_method(payment_method_id):
    return proxy_request(f"/payment-methods/{payment_method_id}")

@app.route("/payment-methods/<int:payment_method_id>", methods=["PUT"])
def update_payment_method(payment_method_id):
    return proxy_request(f"/payment-methods/{payment_method_id}", method="PUT", data=request.get_json())

@app.route("/payment-methods/<int:payment_method_id>", methods=["DELETE"])
def delete_payment_method(payment_method_id):
    return proxy_request(f"/payment-methods/{payment_method_id}", method="DELETE")

@app.route("/payment-methods/<int:payment_method_id>/primary", methods=["PUT"])
def set_primary_payment_method(payment_method_id):
    return proxy_request(f"/payment-methods/{payment_method_id}/primary", method="PUT")

# Rutas de contenido
@app.route("/content", methods=["GET"])
def get_contents():
    return proxy_request("/content", params=request.args)

@app.route("/content/<int:content_id>", methods=["GET"])
def get_content(content_id):
    return proxy_request(f"/content/{content_id}")

# Rutas admin de contenido
@app.route("/admin/content", methods=["POST"])
def admin_create_content():
    return proxy_request("/admin/content", method="POST", data=request.get_json())

@app.route("/admin/content/<int:content_id>", methods=["PUT"])
def admin_update_content(content_id):
    return proxy_request(f"/admin/content/{content_id}", method="PUT", data=request.get_json())

@app.route("/admin/content/<int:content_id>", methods=["DELETE"])
def admin_delete_content(content_id):
    return proxy_request(f"/admin/content/{content_id}", method="DELETE")

@app.route("/admin/content/<int:content_id>/genres", methods=["POST"])
def admin_add_content_genre(content_id):
    return proxy_request(f"/admin/content/{content_id}/genres", method="POST", data=request.get_json())

@app.route("/admin/content/<int:content_id>/genres/<int:genre_id>", methods=["DELETE"])
def admin_remove_content_genre(content_id, genre_id):
    return proxy_request(f"/admin/content/{content_id}/genres/{genre_id}", method="DELETE")

@app.route("/admin/content/<int:content_id>/tags", methods=["POST"])
def admin_add_content_tag(content_id):
    return proxy_request(f"/admin/content/{content_id}/tags", method="POST", data=request.get_json())

@app.route("/admin/content/<int:content_id>/tags/<int:tag_id>", methods=["DELETE"])
def admin_remove_content_tag(content_id, tag_id):
    return proxy_request(f"/admin/content/{content_id}/tags/{tag_id}", method="DELETE")

@app.route("/admin/content/<int:content_id>/directors", methods=["POST"])
def admin_add_content_director(content_id):
    return proxy_request(f"/admin/content/{content_id}/directors", method="POST", data=request.get_json())

@app.route("/admin/content/<int:content_id>/directors/<int:director_id>", methods=["DELETE"])
def admin_remove_content_director(content_id, director_id):
    return proxy_request(f"/admin/content/{content_id}/directors/{director_id}", method="DELETE")

# Rutas de compras
@app.route("/purchases", methods=["POST"])
def create_purchase():
    return proxy_request("/purchases", method="POST", data=request.get_json())

@app.route("/purchases", methods=["GET"])
def get_user_purchases():
    return proxy_request("/purchases")

@app.route("/purchases/<int:purchase_id>", methods=["GET"])
def get_purchase(purchase_id):
    return proxy_request(f"/purchases/{purchase_id}")

@app.route("/purchases/date/<string:purchase_date>", methods=["GET"])
def get_purchase_by_date(purchase_date):
    return proxy_request(f"/purchases/date/{purchase_date}")

# Rutas admin de compras
@app.route("/admin/purchases", methods=["GET"])
def admin_get_all_purchases():
    return proxy_request("/admin/purchases")

@app.route("/admin/purchases/<int:purchase_id>", methods=["GET"])
def admin_get_purchase(purchase_id):
    return proxy_request(f"/admin/purchases/{purchase_id}")

# Rutas de carrito de compras
@app.route("/cart", methods=["GET"])
def get_cart():
    return proxy_request("/cart")

@app.route("/cart/item", methods=["POST"])
def add_item_to_cart():
    return proxy_request("/cart/item", method="POST", data=request.get_json())

@app.route("/cart/content/<int:content_id>", methods=["DELETE"])
def remove_item_from_cart(content_id):
    return proxy_request(f"/cart/content/{content_id}", method="DELETE")

@app.route("/cart", methods=["DELETE"])
def clear_cart():
    return proxy_request("/cart", method="DELETE")

# Rutas de listas de deseos
@app.route("/wish-lists", methods=["GET"])
def get_user_wish_lists():
    return proxy_request("/wish-lists")

@app.route("/wish-list", methods=["GET"])
def get_wish_list():
    return proxy_request("/wish-list", params=request.args)

@app.route("/wish-list", methods=["POST"])
def create_wish_list():
    return proxy_request("/wish-list", method="POST", data=request.get_json())

@app.route("/wish-list/<string:wish_list_name>", methods=["PUT"])
def update_wish_list(wish_list_name):
    return proxy_request(f"/wish-list/{wish_list_name}", method="PUT", data=request.get_json())

@app.route("/wish-list/<string:wish_list_name>", methods=["DELETE"])
def delete_wish_list(wish_list_name):
    return proxy_request(f"/wish-list/{wish_list_name}", method="DELETE")

@app.route("/wish-list/<string:wish_list_name>/content/<int:content_id>", methods=["POST"])
def add_content_to_wish_list(wish_list_name, content_id):
    return proxy_request(f"/wish-list/{wish_list_name}/content/{content_id}", method="POST")

@app.route("/wish-list/<string:wish_list_name>/content/<int:content_id>", methods=["DELETE"])
def remove_content_from_wish_list(wish_list_name, content_id):
    return proxy_request(f"/wish-list/{wish_list_name}/content/{content_id}", method="DELETE")

# Manejadores de errores
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Gateway - Resource not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Gateway - Internal server error'}), 500


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('FLASK_DEBUG', 'TRUE').lower() == 'true'
    app.run(host="0.0.0.0", port=port, debug=debug)