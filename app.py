import os
import logging
from datetime import datetime, timedelta
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///timetracker.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Session configuration for persistent login
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)  # 30 days for employees

# Initialize the app with the extension
db.init_app(app)

with app.app_context():
    # Import models to ensure tables are created
    import models
    db.create_all()
    
    # Create default admin user
    from models import User
    from werkzeug.security import generate_password_hash
    
    # Create default admin user
    admin_exists = User.query.filter_by(phone_number="0000000000").first()
    if not admin_exists:
        admin_user = User(
            phone_number="0000000000",
            password_hash=generate_password_hash("admin123"),
            security_question="What is your favorite color?",
            security_answer="blue",
            role="admin",
            is_approved=True,
            full_name="System Administrator"
        )
        db.session.add(admin_user)
        logging.info("Default admin user created")
    
    # Create demo manager user
    manager_exists = User.query.filter_by(phone_number="1111111111").first()
    if not manager_exists:
        manager_user = User(
            phone_number="1111111111",
            password_hash=generate_password_hash("manager123"),
            security_question="What city were you born in?",
            security_answer="chicago",
            role="manager",
            is_approved=True,
            full_name="Demo Manager"
        )
        db.session.add(manager_user)
        logging.info("Demo manager user created")
    
    # Create demo employee user
    employee_exists = User.query.filter_by(phone_number="2222222222").first()
    if not employee_exists:
        employee_user = User(
            phone_number="2222222222",
            password_hash=generate_password_hash("employee123"),
            security_question="What was your first pet's name?",
            security_answer="buddy",
            role="employee",
            is_approved=True,
            full_name="Demo Employee"
        )
        db.session.add(employee_user)
        logging.info("Demo employee user created")
    
    db.session.commit()

# Import routes
import routes
