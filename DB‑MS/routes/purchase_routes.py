from flask import Blueprint, request, jsonify
from models import Purchase, User
from services import token_required, admin_required

purchase_bp = Blueprint('purchase', __name__)


@purchase_bp.route("/purchases", methods=["POST"])
@token_required
def create_purchase(current_user):
    """Crea compras a partir de los items en el carrito del usuario"""
    try:
        data = request.get_json()
        user_payment_method_id = data.get(
            "user_payment_method_id") if data else None
        purchase_ids = Purchase.create_purchase(
            current_user["id"], user_payment_method_id)

        return jsonify({
            "message": "Purchase completed successfully",
            "purchase_ids": purchase_ids,
            "total_items_purchased": len(purchase_ids)
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@purchase_bp.route("/purchases", methods=["GET"])
@token_required
def get_user_purchases(current_user):
    """Obtiene todas las compras del usuario autenticado"""
    try:
        purchases = Purchase.get_user_purchases(current_user["id"])
        return jsonify(purchases), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@purchase_bp.route("/purchases/<int:purchase_id>", methods=["GET"])
@token_required
def get_purchase(current_user, purchase_id):
    """Obtiene detalles de una compra específica del usuario por el id de la compra"""
    try:
        purchase = Purchase.get_purchase_by_id(purchase_id, current_user["id"])

        if not purchase:
            return jsonify({"error": "Purchase not found or does not belong to user"}), 404

        return jsonify(purchase), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@purchase_bp.route("/purchases/date/<string:purchase_date>", methods=["GET"])
@token_required
def get_purchase_by_date(current_user, purchase_date):
    """Obtiene detalles de una compra específica del usuario por la fecha de compra"""
    try:
        purchase = Purchase.get_purchase_by_date(
            purchase_date, current_user["id"])

        if not purchase:
            return jsonify({"error": "Purchase not found or does not belong to user"}), 404

        return jsonify(purchase), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@purchase_bp.route("/admin/purchases", methods=["GET"])
@admin_required
def get_all_purchases(current_user):
    """Obtiene todas las compras (solo para administradores)"""
    try:
        purchases = Purchase.get_all_purchases()
        return jsonify(purchases), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
