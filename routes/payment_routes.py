from flask import Blueprint, request, jsonify
from models.user import User
from services import generate_token

payment_bp = Blueprint('payment', __name__)
