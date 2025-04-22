from flask import Blueprint, request, jsonify
from models import WishList
from services import token_required, admin_required

wish_list_bp = Blueprint('wish_list', __name__)


@wish_list_bp.route("/wish-lists", methods=["GET"])
@token_required
def get_user_wish_lists(current_user):
    try:
        wish_lists = WishList.get_user_wish_lists(current_user["id"])
        if not wish_lists:
            return jsonify({"message": "No wish lists found for the user"}), 404

        return jsonify([
            {
                "name": wl["name"],
                "latest_addition": wl["latest_addition"],
                "first_addition": wl["first_addition"],
                "content_count": wl["content_count"]
            } for wl in wish_lists
        ]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@wish_list_bp.route("/wish-list", methods=["GET"])
@token_required
def get_wish_list(current_user):
    try:
        wish_list_name = request.args.get("name")
        wish_list = WishList.get_wish_list_with_content(
            wish_list_name=wish_list_name,
            user_id=current_user["id"]
        )
        if not wish_list:
            return jsonify({"error": "Wish list not found"}), 404
        return jsonify(wish_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@wish_list_bp.route("/wish-list", methods=["POST"])
@token_required
def create_wish_list(current_user):
    data = request.get_json()
    if not data.get("name"):
        return jsonify({"error": "Name is required"}), 400

    wish_list_data = {
        "user_id": current_user["id"],
        "name": data["name"]
    }
    if data.get("content_id"):
        wish_list_data["content_id"] = data["content_id"]

    try:
        wish_list_id = WishList.create(wish_list_data)
        return jsonify({"id": wish_list_id, "message": "Wish list created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@wish_list_bp.route("/wish-list/<string:wish_list_name>", methods=["PUT"])
@token_required
def update_wish_list(current_user, wish_list_name):
    data = request.get_json()
    if not data.get("name"):
        return jsonify({"error": "Name is required"}), 400

    try:
        wish_list = WishList.get_wish_list_with_content(
            wish_list_name=wish_list_name, user_id=current_user["id"])
        if not wish_list:
            return jsonify({"error": "Wish list not found"}), 404

        rows_updated = WishList.update(
            wish_list_name, data["name"], current_user["id"])
        if rows_updated == 0:
            return jsonify({"error": "No changes made"}), 400

        return jsonify({"message": "Wish list updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@wish_list_bp.route("/wish-list/<string:wish_list_name>", methods=["DELETE"])
@token_required
def delete_wish_list(current_user, wish_list_name):
    try:
        rows_deleted = WishList.delete(
            name=wish_list_name,
            user_id=current_user["id"]
        )

        if rows_deleted == 0:
            return jsonify({"error": "No wish lists found with this name"}), 404

        return jsonify({"message": f"{rows_deleted} wish list entries deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@wish_list_bp.route("/wish-list/<string:wish_list_name>/content/<int:content_id>", methods=["POST"])
@token_required
def add_content_to_wish_list(current_user, wish_list_name, content_id):
    try:
        wish_list = WishList.get_wish_list_with_content(
            wish_list_name=wish_list_name, user_id=current_user["id"])
        if not wish_list:
            return jsonify({"error": "Wish list not found"}), 404

        new_id = WishList.add_content_to_wish_list(
            wish_list_name, content_id, current_user["id"])
        return jsonify({"message": "Content added to wish list", "new_id": new_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@wish_list_bp.route("/wish-list/<string:wish_list_name>/content/<int:content_id>", methods=["DELETE"])
@token_required
def remove_content_from_wish_list(current_user, wish_list_name, content_id):
    try:
        rows_deleted = WishList.remove_content_from_wish_list(
            wish_list_name, content_id, current_user["id"])

        if rows_deleted == 0:
            return jsonify({"error": "Content not found in wish list"}), 404

        return jsonify({"message": "Content removed from wish list successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    try:
        wish_lists = WishList.get_all()
        return jsonify([
            {
                "id": wl["id"],
                "user_id": wl["user_id"],
                "name": wl["name"],
                "date_creation": wl["date_creation"].strftime('%d-%m-%Y %H:%M:%S'),
                "content_id": wl["content_id"]
            } for wl in wish_lists
        ]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500