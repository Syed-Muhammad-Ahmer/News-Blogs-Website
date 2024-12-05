# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor

db = SQLAlchemy()

def create_app():

    app = Flask(__name__)
    app.config.from_object('config.Config')
    ckeditor = CKEditor(app)

    # Initialize plugins
    db.init_app(app)

    # Register the Blueprint
    from app.routes import bp
    app.register_blueprint(bp)

    
    return app
