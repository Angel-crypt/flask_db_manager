from flask import Blueprint, request, jsonify
from models.user import User
from services import generate_token

purchase_bp = Blueprint('purchase', __name__)
