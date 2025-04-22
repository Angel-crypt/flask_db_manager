from itsdangerous import URLSafeTimedSerializer
import os

SECRET_KEY = os.getenv("SECRET_KEY", "dev_key")
serializer = URLSafeTimedSerializer(SECRET_KEY)


def generate_reset_token(email):
    return serializer.dumps(email, salt="password-reset")


def verify_reset_token(token, max_age=900):  # 15min
    try:
        return serializer.loads(token, salt="password-reset", max_age=max_age)
    except Exception:
        return None