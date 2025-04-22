from flask import Blueprint, request, jsonify
from models import PaymentMethod, UserPaymentMethod
from services import token_required

payment_method_bp = Blueprint('payment_method', __name__)


@payment_method_bp.route("/payment-methods", methods=["GET"])
@token_required
def get_user_payment_methods(current_user):
    """Obtiene todos los métodos de pago de un usuario"""
    try:
        payment_methods = UserPaymentMethod.get_user_payment_methods(
            current_user["id"])
        if not payment_methods:
            return jsonify({"message": "No payment methods found for this user"}), 404

        return jsonify([
            {
                "id": pm["payment_method_id"],
                "name": pm["name"],
                "type": pm["type"],
                "is_primary": bool(pm["is_primary"])
            } for pm in payment_methods
        ]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@payment_method_bp.route("/payment-methods/<int:payment_method_id>", methods=["GET"])
@token_required
def get_user_payment_method(current_user, payment_method_id):
    """Obtiene un método de pago específico de un usuario"""
    try:
        payment_method = UserPaymentMethod.get_user_payment_method(
            current_user["id"], payment_method_id
        )

        if not payment_method:
            return jsonify({"error": "Payment method not found or does not belong to user"}), 404

        return jsonify({
            "id": payment_method["payment_method_id"],
            "name": payment_method["name"],
            "type": payment_method["type"],
            "is_primary": bool(payment_method["is_primary"])
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@payment_method_bp.route("/payment-methods", methods=["POST"])
@token_required
def add_payment_method(current_user):
    """Crea un nuevo método de pago para un usuario"""
    data = request.get_json()

    # Validamos los datos requeridos
    if not data.get("name"):
        return jsonify({"error": "Name is required"}), 400

    if not data.get("type"):
        return jsonify({"error": "Type is required"}), 400

    payment_method_data = {
        "name": data["name"],
        "type": data["type"],
        "is_primary": data.get("is_primary", 0)
    }

    try:
        # Creamos el método de pago
        payment_method_id = UserPaymentMethod.add_payment_method(
            current_user["id"], payment_method_data
        )

        return jsonify({
            "message": "Payment method added successfully",
            "payment_method_id": payment_method_id
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@payment_method_bp.route("/payment-methods/<int:payment_method_id>", methods=["PUT"])
@token_required
def update_payment_method(current_user, payment_method_id):
    """Actualiza un método de pago de un usuario"""
    data = request.get_json()

    # Requerimos al menos un campo para actualizar
    if not data:
        return jsonify({"error": "No update data provided"}), 400

    payment_method_data = {}
    if "name" in data:
        payment_method_data["name"] = data["name"]

    if "type" in data:
        payment_method_data["type"] = data["type"]

    if "is_primary" in data:
        payment_method_data["is_primary"] = data["is_primary"]

    try:
        # Actualizamos el método de pago
        UserPaymentMethod.update_payment_method(
            current_user["id"], payment_method_id, payment_method_data
        )

        return jsonify({
            "message": "Payment method updated successfully"
        }), 200
    except Exception as e:
        if "not found" in str(e):
            return jsonify({"error": str(e)}), 404
        return jsonify({"error": str(e)}), 500


@payment_method_bp.route("/payment-methods/<int:payment_method_id>", methods=["DELETE"])
@token_required
def delete_payment_method(current_user, payment_method_id):
    """Elimina un método de pago de un usuario"""
    try:
        UserPaymentMethod.delete_payment_method(
            current_user["id"], payment_method_id)
        return jsonify({
            "message": "Payment method deleted successfully"
        }), 200
    except Exception as e:
        if "not found" in str(e):
            return jsonify({"error": str(e)}), 404
        elif "Cannot delete" in str(e):
            return jsonify({"error": str(e)}), 400
        return jsonify({"error": str(e)}), 500


@payment_method_bp.route("/payment-methods/<int:payment_method_id>/primary", methods=["PUT"])
@token_required
def set_primary_payment_method(current_user, payment_method_id):
    """Establece un método de pago como principal para un usuario"""
    try:
        UserPaymentMethod.set_primary_payment_method(
            current_user["id"], payment_method_id
        )

        return jsonify({
            "message": "Payment method set as primary successfully"
        }), 200
    except Exception as e:
        if "not found" in str(e):
            return jsonify({"error": str(e)}), 404
        return jsonify({"error": str(e)}), 500