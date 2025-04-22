from flask_mail import Message
import os
from dotenv import load_dotenv

load_dotenv()

def send_reset_email(to_email, token):
    from app import app, mail
    link = f"{os.getenv('FRONTEND_URL')}/reset-password?token={token}"
    msg = Message("Password Reset", recipients=[to_email])
    msg.body = f"Click the link to reset your password: {link}"
    with app.app_context():
        mail.send(msg)

def send_success_email(to_email):
    from app import app, mail
    msg = Message("Password Reset Successful", recipients=[to_email])
    msg.body = "Your password has been successfully reset."
    with app.app_context():
        mail.send(msg)