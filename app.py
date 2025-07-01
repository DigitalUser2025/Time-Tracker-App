import os
import logging
from datetime import timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash

# Set up logging
logging.basicConfig(level=logging.INFO)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Use ProxyFix for correct URL scheme behind proxies like Render
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database connection string from environment
# Append sslmode=require for Neon DB connection
database_url = os.environ.get("DATABASE_URL", "sqlite:///timetracker.db")
if database_url.startswith("postgres://"):
    # Replace deprecated prefix for SQLAlchemy compatibility if needed
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# Ensure SSL mode for Neon PostgreSQL
if "sslmode" not in database_url:
    sep = "&" if "?" in database_url else "?"
    database_url += f"{sep}sslmode=require"

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Session configuration
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize SQLAlchemy with Flask app
db.init_app(app)

with app.app_context():
    # Import your models here to register them with SQLAlchemy
    import models

    # Create tables if they don't exist
    db.create_all()

    # Create default users if they don't exist
    from models import User

    def create_user_if_not_exists(phone, password, question, answer, role, full_name):
        user = User.query.filter_by(phone_number=phone).first()
        if not user:
            new_user = User(
                phone_number=phone,
                password_hash=generate_password_hash(password),
                security_question=question,
                security_answer=answer,
                role=role,
                is_approved=True,
                full_name=full_name
            )
            db.session.add(new_user)
            logging.info(f"User created: {role} - {full_name}")

    create_user_if_not_exists("0000000000", "admin123", "What is your favorite color?", "blue", "admin", "System Administrator")
    create_user_if_not_exists("1111111111", "manager123", "What city were you born in?", "chicago", "manager", "Demo Manager")
    create_user_if_not_exists("2222222222", "employee123", "What was your first pet's name?", "buddy", "employee", "Demo Employee")

    db.session.commit()

# Import your routes last to avoid circular imports
import routes

if __name__ == "__main__":
    # Optional: Run Flask dev server (not recommended on Render, which uses gunicorn)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
