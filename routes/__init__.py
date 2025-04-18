from .auth_routes import auth_bp
from .user_routes import users_bp
from .payment_routes import payment_bp
from .content_routes import content_bp
from .purchase_routes import purchase_bp
from .wish_list_routes import wish_list_bp

__all__ = [
    "auth_bp",
    "users_bp",
    "payment_bp",
    "content_bp",
    "purchase_bp",
    "wish_list_bp"
]