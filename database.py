import os
from flask import Flask
from models import db

def init_db(app: Flask):
    database_url = os.getenv("DATABASE_URL", "sqlite:///portfolio.db")
    
    # Handle Heroku-style postgres:// URLs
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
        
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
