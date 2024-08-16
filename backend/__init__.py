from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import config
import os
from flask_mail import Mail
from flask_apscheduler import APScheduler

db = SQLAlchemy()
migrate = Migrate()
mail = Mail() ### 메일
scheduler = APScheduler()

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    
    db.init_app(app)
    migrate.init_app(app, db)
    from . import models
    
    from .views import auth_views
    # app.register_blueprint(main_views.bp)
    app.register_blueprint(auth_views.bp)
    mail.init_app(app) 
    scheduler.init_app(app)
    
    return app