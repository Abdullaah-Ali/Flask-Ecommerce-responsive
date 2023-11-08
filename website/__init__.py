from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_mail import Mail 
import os








db = SQLAlchemy()
DB_NAME = 'qwerty.db'

mail = Mail()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = 'yours@gmail.com'
    app.config['MAIL_PASSWORD'] = 'yourpas'
    mail = Mail(app)
    mail.init_app(app)
    

    

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    @login_manager.user_loader
    
    def load_user(id):
        return User.query.get(int(id))
    
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Note
    
    create_database(app)

    
    
    return app

def create_database(app):
    with app.app_context():
        if not path.exists('website/' + DB_NAME):
            db.create_all()
            print('Created Database!')
            
            
