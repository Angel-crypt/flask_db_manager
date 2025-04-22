from flask import Blueprint, request, jsonify
from models import ShoppingCart
from services import token_required

shopping_cart_bp = Blueprint('shopping_cart', __name__)


@shopping_cart_bp.route("/cart", methods=["GET"])
@token_required
def get_cart(current_user):
    """Obtiene el carrito del usuario con todos sus items"""
    try:
        cart = ShoppingCart.get_cart_with_items(current_user["id"])
        return jsonify(cart), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@shopping_cart_bp.route("/cart/item", methods=["POST"])
@token_required
def add_item_to_cart(current_user):
    """Añade un item al carrito del usuario (solo 1 unidad permitida)"""
    data = request.get_json()

    if not data.get("content_id"):
        return jsonify({"error": "Content ID is required"}), 400

    content_id = data.get("content_id")

    try:
        item_id = ShoppingCart.add_item_to_cart(
            current_user["id"], content_id
        )

        return jsonify({
            "message": "Item added to cart successfully",
            "item_id": item_id
        }), 201
    except Exception as e:
        # Si el error es por duplicado, devolver un mensaje más específico
        error_message = str(e)
        if "already exists in cart" in error_message:
            return jsonify({"error": "This item is already in your cart"}), 400
        elif "unavailable" in error_message:
            return jsonify({"error": "This item is currently unavailable and cannot be added to cart"}), 400
        else:
            return jsonify({"error": error_message}), 500


@shopping_cart_bp.route("/cart/content/<int:content_id>", methods=["DELETE"])
@token_required
def remove_item_from_cart(current_user, content_id):
    """Elimina un item del carrito basado en el content_id"""
    try:
        rows_deleted = ShoppingCart.remove_item_from_cart(
            current_user["id"], content_id
        )

        if rows_deleted == 0:
            return jsonify({"error": "Item not found in cart"}), 404

        return jsonify({"message": "Item removed from cart successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@shopping_cart_bp.route("/cart", methods=["DELETE"])
@token_required
def clear_cart(current_user):
    """Elimina todos los items del carrito del usuario"""
    try:
        items_deleted = ShoppingCart.clear_cart(current_user["id"])

        return jsonify({
            "message": "Cart cleared successfully",
            "items_removed": items_deleted
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
