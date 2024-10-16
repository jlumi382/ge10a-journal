from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, template_folder="templates/")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./events.db'
    app.config['SESSION_PERMANENT'] = False
    app.secret_key = os.urandom(24)

    db.init_app(app)

    # register routes
    from routes import register_routes
    register_routes(app, db)

    migrate = Migrate(app, db)

    return app
