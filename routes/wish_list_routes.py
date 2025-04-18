from flask import Blueprint, request, jsonify
from models.user import User
from services import generate_token

wish_list_bp = Blueprint('wish_list', __name__)
