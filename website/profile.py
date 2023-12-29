import os
from flask import Blueprint, app , render_template
from flask import redirect , url_for
from flask_login import  login_required ,  current_user
from flask import request
from website import db , mail , admin , socketio
from flask import current_app, session
from datetime import datetime, timedelta

from flask_login import current_user
from .models import User, Note , Cart , product , Profile
from sqlalchemy.exc import SQLAlchemyError
import requests
from flask import flash
import random
import stripe
from flask import jsonify
import pprint
from flask import *

from flask_mail import Message
from flask_socketio import SocketIO, emit, disconnect






#here we weould create  a profile system for our website 

profile = Blueprint('user_profile', __name__)




@profile.route('/profile', methods=['GET' , 'POST'])
@login_required
def user_profile():
    user_id = current_user.id
    profile = Profile.query.filter_by(user_id=user_id).first()

    if not profile:
        profile = Profile(user_id=user_id)

    if request.method == 'POST':
        # Handle form submission for updating the profile
        profile.first_name = request.form.get('fname')
        profile.last_name = request.form.get('lname')
        profile.gender = request.form.get('gender')
        profile.number = request.form.get('number')
        
        

        db.session.add(profile)
        db.session.commit()

    return render_template('profile.html', profile=profile)

          
          



@login_required
@profile.route('/userprofile' , methods=['POST' , 'GET'])
def showuserprofile ():
     user_id = current_user.id   
     profile = Profile.query.filter_by(user_id=current_user.id).first()
     
     if profile:
          profile_data = {
            'id': profile.id,
            'first_name': profile.first_name,
            'last_name': profile.last_name,
            'image': profile.image,
            'number': profile.number,
            'gender': profile.gender
 
          }
          print(profile_data)
          return jsonify(profile_data)
     else :
          return jsonify({'message': 'Profile does not exist for the current user'}), 404

          
   
   
 
 
 
 
  



# we would creat the functions on the same webapp that would basically url hits honge aur jis user ko register karna he karlenga using the ajax page reload off karenge 
#simmilarly har btn pe func call for the betterment 
#image probllem oslution aswell
#already registred / created profile added option aswell
 

#chat bot custom data tained
    

from flask_socketio import SocketIO
from website.chatbot import get_chatbot_response






chat_history = [] 

@socketio.on('connect')
def handle_connect():
    user_id = request.sid
    print(f'Client connected: {user_id}')

@socketio.on('disconnect')
def handle_disconnect():
    user_id = request.sid
    print(f'Client disconnected: {user_id}')

@socketio.on('message')
def handle_message(data):
    print('Received message:', data['msg'])
    user_message = data['msg']  # Define user_message
    chatbot_response = get_chatbot_response(user_message, chat_history)  # Pass chat_history to get_chatbot_response
    emit('message', {'user_id': 'server', 'msg': f'Server received: {user_message}. Chatbot response: {chatbot_response}'})
    print (chatbot_response)
    
    
    

@profile.route('/chatai', methods=['GET', 'POST'])
def chatwithai():
    return render_template('chatroom.html')


# --> server recived the msg take it to the file of chat bot and then response generate re send the msg to the sevrer 
# -->  ,msg to be store in logs 7 days expire
#--> 1 on 1 convo