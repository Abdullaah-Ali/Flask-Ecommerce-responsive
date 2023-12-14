#database models
#and todo
#importing db models deom init
#flask login help user login
from website import db
from flask_login import UserMixin
from sqlalchemy import func
from flask_admin.contrib.sqla import ModelView
from website import admin




class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255))#task being store here
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    notes = db.relationship('User', backref=db.backref('todos', lazy=True))
    
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    productName = db.Column(db.String(255))
    productPrice = db.Column(db.Integer)
    quantity = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('items', lazy=True))

    
    
        
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique= True)
    password = db.Column(db.String(150))
    first_name= db.Column(db.String(150))
    otp = db.Column(db.String(16))
    totalamt= db.Column(db.Integer,default=0)
    is_verified = db.Column(db.Boolean, default=0)  # Change the default value to 0
    is_admin = db.Column(db.Boolean, default=0)
    


class product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(120), nullable=False)
    
    
 
 
class profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name= db.Column(db.String(150))
    profile_image = db.Column(db.String(255))
    

    
    






    
    
