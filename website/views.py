from flask import Blueprint , render_template
from flask import redirect , url_for
from flask_login import  login_required ,  current_user
from flask import request
from website import db 
from flask import current_app, session
from flask_login import current_user
from .models import User, Note
from sqlalchemy.exc import SQLAlchemyError
import requests
from flask import flash
import random





views = Blueprint('views',__name__ )


#defininf the root so whenever its hit homepage is called
@views.route('/')

def home():
    return render_template('home.html')


@views.route('/', methods=['POST', 'GET'])
def addtask():
 # Use 'views.index' instead of 'index'
    if request.method == 'POST':
        task = request.form.get('addtask')
       
        if task:
            # Get the current user's ID using the Flask-Login current_user attribute
            user_id = current_user.id
            # Create a new Note and add it to the database
            new_note = Note(text=task, user_id=user_id)  # Use 'task' and 'user_id' variables
            db.session.add(new_note)
            db.session.commit()
            
        return redirect(url_for('views.home'))
    
    
@views.route('/alltasldelete' , methods=['POST'])
def deletealltask():
    
    if request.method=='POST':
        texts = Note.query.filter_by(user_id=current_user.id).all() 
        for text in texts:
            db.session.delete(text)
            db.session.commit()
        flash('All the tasks have been deleted' ,  category='success')
    return redirect(url_for('views.home'))     
    
@views.route('deletetask' , methods=['POST' , 'GET'])
def deletetask():
    task_message = request.form.get('deletetask')  # Get the task message from the form input
    tasks = Note.query.filter_by(user_id=current_user.id, text=task_message).all()

    if tasks:
        for task in tasks:
            db.session.delete(task)
            db.session.commit()
        flash('Task(s) have been deleted', category='success')
    else:
        flash('Task not found', category='error')

    return redirect(url_for('views.home'))