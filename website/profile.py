import os
from flask import Blueprint, app , render_template
from flask import redirect , url_for
from flask_login import  login_required ,  current_user
from flask import request
from website import db , mail , admin
from flask import current_app, session
from datetime import datetime, timedelta

from flask_login import current_user
from .models import User, Note , Cart , product
from sqlalchemy.exc import SQLAlchemyError
import requests
from flask import flash
import random
import stripe
from flask import jsonify
import pprint
from flask_mail import Message







#here we weould create  a profile system for our website 

profile = Blueprint('profile',__name__ )

@profile.route('/userprofile')
def showuserprofilr ():
     return render_template('profile.html')
 