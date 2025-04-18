from flask import Blueprint, request, jsonify
from models import Content
from services import token_required, admin_required

content_bp = Blueprint('content', __name__)

@content_bp.route("/content", methods=["GET"])
@token_required
def get_contents():
    """Obtener todos los contenidos"""
    try:
        contents = Content.get_all()

        contents_list = []
        for content in contents:
            content_data = {
                "id": content["id"],
                "title": content["title"],
                "rating": content.get("rating"),
                "release_date": str(content.get("release_date")),
                "duration": str(content.get("duration")),
                "summary": content.get("summary"),
                "image_url": content.get("image_url"),
                "status": content.get("status"),
                "price": float(content.get("price", 0)),
                "type": content.get("type"),
            }
            contents_list.append(content_data)

        return jsonify(contents_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500