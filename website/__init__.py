from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_mail import Mail 
import os
from authlib.integrations.flask_client import OAuth
from flask_admin import Admin , BaseView , expose
from flask_admin.contrib.sqla import ModelView

from flask_login import login_user, login_required, logout_user, current_user
from flask_login import current_user
from flask import request
from flask_admin import AdminIndexView
from functools import wraps
from flask import current_app
from flask import Flask, redirect, url_for
from flask_socketio import SocketIO










#making the admin panel interface here 

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated or not current_user.is_admin == 1:
            return redirect(url_for('auth.login', next=request.url))
        return self.render('admin/index.html')

class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin == 1

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login', next=request.url))
    




    
    








#flask authentication system for the admin



db = SQLAlchemy()
DB_NAME = 'ecommerce.db'

mail = Mail()
oauth = OAuth()
admin = Admin()
socketio = SocketIO()





def create_app():
    app = Flask(__name__)
    
    
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    with app.app_context():
        db.init_app(app)
        oauth.init_app(app)
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = 'ahere094@gmail.com'
    app.config['MAIL_PASSWORD'] = 'hpao tmpx hlyk jkkv'
    app.config['STRIPE_PUBLIC_KEY'] = 'pk_test_51OEbyRI3XvqE4k0AqsimrKerDkmHHwAdrZvvds4j83IEEneodzzxcHg4HrBviXBfXTKcBH8VbWlkC6rN0X66U5sU00ctlkquxs'
    
    mail = Mail(app)
    
    
    
    mail.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")



    admin.init_app(app, index_view=MyAdminIndexView())
    
    

    


        
    

    

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    from .views import views
    from .auth import auth
    from .profile import profile
    

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(profile, url_prefix='/')

    

    from .models import User, Note , Cart , product , Profile
    
    admin.add_view(MyModelView(product , db.session))
    admin.add_view(MyModelView(Profile , db.session))
   
    
    create_database(app)
    

    

    

    
    return app

def create_database(app):
    with app.app_context():
        if not path.exists('website/' + DB_NAME):
            db.create_all()
            print('Created Database!')
            
            

            

            
            
