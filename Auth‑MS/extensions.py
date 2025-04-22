from flask import Flask
from flask_mail import Mail
import os
from dotenv import load_dotenv

load_dotenv()

mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.update(
        MAIL_SERVER='live.smtp.mailtrap.io',
        MAIL_PORT=587,
        MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
        MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
        MAIL_DEFAULT_SENDER=os.getenv("MAIL_DEFAULT_SENDER"),
        MAIL_USE_TLS=True,
        MAIL_USE_SSL=False
    )
    mail.init_app(app)

    return app

