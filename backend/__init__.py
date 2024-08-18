from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
import config
import os
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_apscheduler import APScheduler


naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))
migrate = Migrate()
mail = Mail() ### 메일
scheduler = APScheduler()

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    
    jwt = JWTManager(app)
    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    from . import models
    
    from .views import auth_views, main_views, fishing_views
    app.register_blueprint(main_views.bp)
    app.register_blueprint(auth_views.bp)
    app.register_blueprint(fishing_views.bp)
    mail.init_app(app) 
    scheduler.init_app(app)
    
    return app