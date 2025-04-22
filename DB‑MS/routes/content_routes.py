from flask import Blueprint, request, jsonify
from models import Content
from services import token_required, admin_required
from datetime import datetime

content_bp = Blueprint('content', __name__)


@content_bp.route("/content", methods=["GET"])
@token_required
def get_contents(current_user):
    """Obtener todos los contenidos con filtros opcionales"""
    try:
        # Extraer parámetros de consulta para filtrado
        genre_id = request.args.get('genre_id', type=int)
        tag_id = request.args.get('tag_id', type=int)
        director_id = request.args.get('director_id', type=int)
        title = request.args.get('title')
        genre_name = request.args.get('genre')
        director_name = request.args.get('director')
        tag_name = request.args.get('tag')
        content_id = request.args.get('id', type=int)
        status = request.args.get('status')
        
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        min_duration = request.args.get('min_duration', type=int)
        max_duration = request.args.get('max_duration', type=int)

        # Construir filtros
        filters = {}

        if genre_name:
            genre_id = Content.get_genre_id_by_name(genre_name)
            if not genre_id:
                return jsonify({"error": "Genre not found"}), 404
        if genre_id:
            if genre_id == 0:
                return jsonify({"error": "Invalid genre_id"}), 400
            filters['genre_id'] = genre_id

        if tag_name:
            tag_id = Content.get_tag_id_by_name(tag_name)
            if not tag_id:
                return jsonify({"error": "Tag not found"}), 404
        if tag_id:
            if tag_id == 0:
                return jsonify({"error": "Invalid tag_id"}), 400
            filters['tag_id'] = tag_id

        # Resolver el ID del director si se pasa por nombre
        if director_name:
            resolved_director_id = Content.get_director_id_by_name(
                director_name)
            if resolved_director_id:
                filters['director_id'] = resolved_director_id
            else:
                return jsonify({"error": "Director not found"}), 404
        elif director_id:
            if director_id == 0:
                return jsonify({"error": "Invalid director_id"}), 400
            filters['director_id'] = director_id

        if title:
            filters['title'] = title
        if content_id:
            filters['id'] = content_id
        if status:
            filters['status'] = status
        
        if min_price is not None:
            filters['min_price'] = min_price
        if max_price is not None:
            filters['max_price'] = max_price
        if min_duration is not None:
            filters['min_duration'] = min_duration
        if max_duration is not None:
            filters['max_duration'] = max_duration

        # Buscar contenidos con los filtros proporcionados
        contents = Content.search(filters)

        # Formatear resultados
        contents_list = []
        for content in contents:
            content_data = {
                "id": content["id"],
                "title": content["title"],
                "classification": content.get("classification"),
                "release_date": str(content.get("release_date")),
                "duration": str(content.get("duration")),
                "summary": content.get("summary"),
                "url_image": content.get("url_image"),
                "status": content.get("status"),
                "price": float(content.get("price", 0)),
                "type": content.get("type"),
                "record_date": str(content.get("record_date"))
            }
            contents_list.append(content_data)

        return jsonify(contents_list), 200
    except Exception as e:
        return jsonify({"errorR": str(e)}), 500


@content_bp.route("/content/<int:content_id>", methods=["GET"])
@token_required
def get_content(current_user, content_id):
    """Obtener un contenido específico con todos sus detalles"""
    try:
        content = Content.get_with_details(content_id)

        if not content:
            return jsonify({"error": "Content not found"}), 404

        # Formatear datos para la respuesta
        content_data = {
            "id": content["id"],
            "title": content["title"],
            "classification": content.get("classification"),
            "release_date": str(content.get("release_date")),
            "duration": str(content.get("duration")),
            "summary": content.get("summary"),
            "url_image": content.get("url_image"),
            "status": content.get("status"),
            "price": float(content.get("price", 0)),
            "type": content.get("type"),
            "record_date": str(content.get("record_date")),
            "genres": content.get("genres", []),
            "tags": content.get("tags", []),
            "directors": content.get("directors", [])
        }

        return jsonify(content_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@content_bp.route("/admin/content", methods=["POST"])
@admin_required
def create_content(current_user):
    """Crear un nuevo contenido (solo administradores)"""
    data = request.get_json()

    # Validar campos requeridos
    required_fields = ["title", "classification", "release_date",
                       "duration", "summary", "url_image", "status", "price", "type", "genres", "tags", "directors"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    try:
        # Convertir duration string a formato correcto si es necesario
        if isinstance(data["duration"], str):
            try:
                # Formato esperado: "HH:MM:SS"
                time_parts = data["duration"].split(":")
                if len(time_parts) == 3:
                    # Formato correcto
                    pass
                elif len(time_parts) == 2:
                    # Agregar segundos si faltan
                    data["duration"] = f"{data['duration']}:00"
                else:
                    return jsonify({"error": "Invalid duration format. Use HH:MM:SS or HH:MM"}), 400
            except Exception:
                return jsonify({"error": "Invalid duration format"}), 400

        # Crear el contenido principal
        content_id = Content.create(data)

        # Procesar relaciones si existen
        if 'genres' in data and isinstance(data['genres'], list):
            for genre_id in data['genres']:
                Content.add_genre(content_id, genre_id)

        if 'tags' in data and isinstance(data['tags'], list):
            for tag_id in data['tags']:
                Content.add_tag(content_id, tag_id)

        if 'directors' in data and isinstance(data['directors'], list):
            for director_id in data['directors']:
                Content.add_director(content_id, director_id)

        return jsonify({
            "message": "Content created successfully",
            "content_id": content_id
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@content_bp.route("/admin/content/<int:content_id>", methods=["PUT"])
@admin_required
def update_content(current_user, content_id):
    """Actualizar un contenido existente (solo administradores)"""
    data = request.get_json()

    try:
        # Verificar que el contenido existe
        existing_content = Content.get_by_id(content_id)
        if not existing_content:
            return jsonify({"error": "Content not found"}), 404

        # Convertir duration string a formato correcto si es necesario
        if "duration" in data and isinstance(data["duration"], str):
            try:
                # Formato esperado: "HH:MM:SS"
                time_parts = data["duration"].split(":")
                if len(time_parts) == 3:
                    # Formato correcto
                    pass
                elif len(time_parts) == 2:
                    # Agregar segundos si faltan
                    data["duration"] = f"{data['duration']}:00"
                else:
                    return jsonify({"error": "Invalid duration format. Use HH:MM:SS or HH:MM"}), 400
            except Exception:
                return jsonify({"error": "Invalid duration format"}), 400

        # Actualizar el contenido principal
        rows_updated = Content.update(content_id, data)

        # Actualizar relaciones si se proporcionan
        if 'genres' in data and isinstance(data['genres'], list):
            # Obtener géneros actuales
            current_content = Content.get_with_details(content_id)
            current_genres = [g['id']
                              for g in current_content.get('genres', [])]

            # Agregar nuevos géneros
            for genre_id in data['genres']:
                if genre_id not in current_genres:
                    Content.add_genre(content_id, genre_id)

            # Eliminar géneros que no están en la lista nueva
            for genre_id in current_genres:
                if genre_id not in data['genres']:
                    Content.remove_genre(content_id, genre_id)

        if 'tags' in data and isinstance(data['tags'], list):
            # Obtener etiquetas actuales
            current_content = Content.get_with_details(content_id)
            current_tags = [t['id'] for t in current_content.get('tags', [])]

            # Agregar nuevas etiquetas
            for tag_id in data['tags']:
                if tag_id not in current_tags:
                    Content.add_tag(content_id, tag_id)

            # Eliminar etiquetas que no están en la lista nueva
            for tag_id in current_tags:
                if tag_id not in data['tags']:
                    Content.remove_tag(content_id, tag_id)

        if 'directors' in data and isinstance(data['directors'], list):
            # Obtener directores actuales
            current_content = Content.get_with_details(content_id)
            current_directors = [d['id']
                                 for d in current_content.get('directors', [])]

            # Agregar nuevos directores
            for director_id in data['directors']:
                if director_id not in current_directors:
                    Content.add_director(content_id, director_id)

            # Eliminar directores que no están en la lista nueva
            for director_id in current_directors:
                if director_id not in data['directors']:
                    Content.remove_director(content_id, director_id)

        return jsonify({
            "message": "Content updated successfully",
            "rows_updated": rows_updated
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@content_bp.route("/admin/content/<int:content_id>", methods=["DELETE"])
@admin_required
def delete_content(current_user, content_id):
    """Eliminar un contenido (solo administradores)"""
    try:
        # Verificar que el contenido existe
        existing_content = Content.get_by_id(content_id)
        if not existing_content:
            return jsonify({"error": "Content not found"}), 404

        # Eliminar relaciones (géneros, etiquetas, directores)
        Content.remove_all_relations(content_id)

        # Eliminar el contenido
        rows_deleted = Content.delete(content_id)

        if rows_deleted == 0:
            return jsonify({"error": "Failed to delete content"}), 500

        return jsonify({
            "message": "Content deleted successfully"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@content_bp.route("/admin/content/<int:content_id>/genres", methods=["POST"])
@admin_required
def add_content_genre(current_user, content_id):
    """Añadir un género a un contenido (solo administradores)"""
    data = request.get_json()

    if 'genre_id' not in data:
        return jsonify({"error": "Missing genre_id field"}), 400

    try:
        # Verificar que el contenido existe
        existing_content = Content.get_by_id(content_id)
        if not existing_content:
            return jsonify({"error": "Content not found"}), 404

        # Añadir el género
        result = Content.add_genre(content_id, data['genre_id'])

        if result:
            return jsonify({"message": "Genre added successfully"}), 200
        else:
            return jsonify({"error": "Genre already exists or invalid genre_id"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@content_bp.route("/admin/content/<int:content_id>/genres/<int:genre_id>", methods=["DELETE"])
@admin_required
def remove_content_genre(current_user, content_id, genre_id):
    """Eliminar un género de un contenido (solo administradores)"""
    try:
        # Verificar que el contenido existe
        existing_content = Content.get_by_id(content_id)
        if not existing_content:
            return jsonify({"error": "Content not found"}), 404

        # Eliminar el género
        result = Content.remove_genre(content_id, genre_id)

        if result:
            return jsonify({"message": "Genre removed successfully"}), 200
        else:
            return jsonify({"error": "Genre not found for this content"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@content_bp.route("/admin/content/<int:content_id>/tags", methods=["POST"])
@admin_required
def add_content_tag(current_user, content_id):
    """Añadir una etiqueta a un contenido (solo administradores)"""
    data = request.get_json()

    if 'tag_id' not in data:
        return jsonify({"error": "Missing tag_id field"}), 400

    try:
        # Verificar que el contenido existe
        existing_content = Content.get_by_id(content_id)
        if not existing_content:
            return jsonify({"error": "Content not found"}), 404

        # Añadir la etiqueta
        result = Content.add_tag(content_id, data['tag_id'])

        if result:
            return jsonify({"message": "Tag added successfully"}), 200
        else:
            return jsonify({"error": "Tag already exists or invalid tag_id"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@content_bp.route("/admin/content/<int:content_id>/tags/<int:tag_id>", methods=["DELETE"])
@admin_required
def remove_content_tag(current_user, content_id, tag_id):
    """Eliminar una etiqueta de un contenido (solo administradores)"""
    try:
        # Verificar que el contenido existe
        existing_content = Content.get_by_id(content_id)
        if not existing_content:
            return jsonify({"error": "Content not found"}), 404

        # Eliminar la etiqueta
        result = Content.remove_tag(content_id, tag_id)

        if result:
            return jsonify({"message": "Tag removed successfully"}), 200
        else:
            return jsonify({"error": "Tag not found for this content"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@content_bp.route("/admin/content/<int:content_id>/directors", methods=["POST"])
@admin_required
def add_content_director(current_user, content_id):
    """Añadir un director a un contenido (solo administradores)"""
    data = request.get_json()

    if 'director_id' not in data:
        return jsonify({"error": "Missing director_id field"}), 400

    try:
        # Verificar que el contenido existe
        existing_content = Content.get_by_id(content_id)
        if not existing_content:
            return jsonify({"error": "Content not found"}), 404

        # Añadir el director
        result = Content.add_director(content_id, data['director_id'])

        if result:
            return jsonify({"message": "Director added successfully"}), 200
        else:
            return jsonify({"error": "Invalid director_id"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@content_bp.route("/admin/content/<int:content_id>/directors/<int:director_id>", methods=["DELETE"])
@admin_required
def remove_content_director(current_user, content_id, director_id):
    """Eliminar un director de un contenido (solo administradores)"""
    try:
        # Verificar que el contenido existe
        existing_content = Content.get_by_id(content_id)
        if not existing_content:
            return jsonify({"error": "Content not found"}), 404

        # Eliminar el director
        result = Content.remove_director(content_id, director_id)

        if result:
            return jsonify({"message": "Director removed successfully"}), 200
        else:
            return jsonify({"error": "Director not found for this content"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
