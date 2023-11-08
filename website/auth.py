from .models import User
from website import db, mail  # Import the 'mail' instance from the main app
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, render_template, Flask, request, flash, redirect, url_for, session
from flask_login import login_user, login_required, logout_user, current_user
from flask_mail import Message
import pyotp
from website import views
from flask import OAuth
from website import OAuth
from website import app

auth = Blueprint('auth', __name__)
oauth = OAuth(app)
google = oauth.remote_app(
    'google',
    consumer_key='464462423467-hrrha457ptid2g0j132pet8316d64klk.apps.googleusercontent.com',  # Replace with your Google OAuth client ID
    consumer_secret='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',  # Replace with your Google OAuth client secret
    request_token_params={
        'scope': 'email',  # Request access to user's email
    },
    base_url='https://accounts.google.com/o/oauth2/auth',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

@app.route('/google-authorized')
def google_authorized():
    response = google.authorized_response()
    if response is None or response.get('access_token') is None:
        flash('Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        ), 'error')
        return redirect(url_for('auth.login'))

    # Get user data from the Google response
    google_user_id = response.get('user_id')
    google_email = response.get('email')
    google_first_name = response.get('given_name')
    google_password = response.get('password')  # Assuming Google provides the hashed password

    # Check if the user already exists based on their Google email
    user = User.query.filter_by(email=google_email).first()

    if user:
        # Update the user's data, set the first name, increment is_verified to 1, and store the Google-provided password
        user.first_name = google_first_name
        user.is_verified = 1
        user.password = google_password  # Store the Google-provided password
    else:
        # Create a new user if the Google email doesn't exist in your database
        new_user = User(email=google_email, first_name=google_first_name, password=google_password, is_verified=1)
        db.session.add(new_user)

    db.session.commit()

    # Log in the user
    login_user(user)

    return redirect(url_for('views.home'))


@auth.route('/login' , methods=['GET', 'POST'])
def login():

    user = None  # Initialize user to None

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

    if user:
        if user.is_verified == 1 and check_password_hash(user.password, password):
            flash('Login successful', category='success')
            login_user(user, remember=True)
            return redirect(url_for('views.home'))  
        else:
            flash('Your account is not verified. Please verify your account first.', category='error')
    else:
        flash('Invalid email or password', category='error')

    return render_template("login.html")

#rather we will render html login page from the filesystem using jinja method
#handiling post method for the user credentials

@auth.route('/logout')
@login_required
def logout():  
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/signup', methods=['GET', 'POST'])
def sign_up():
    

    if request.method == 'POST':
        email = request.form.get('email')
        first_name= request.form.get('firstName')
        lastName = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
    
        user = User.query.filter_by(email=email).first()
        if user:
            flash('email already exists', category='error')
            return render_template("signup.html")    
        elif len(email) < 4 or "@gmail" not in email:
            flash('Your email address is too short or does not contain "@gmail". Please enter a valid email address', category='error')
            
        elif len(first_name) < 2:
            flash('please enter a valid first name',category='error')
        elif len(lastName) < 2:
            flash('please enter a valid last name',category='error')
        elif password1 != password2:
            flash('passwords do not match',category='error')
        elif len(password1) < 4:
            flash('password must be at least 4 characters long' ,category='error')
            return render_template("signup.html") 
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method='sha256'), is_verified=False)
            db.session.add(new_user)
            db.session.commit()

            session['new_user_id'] = new_user.id

            otp = generate_otp()
            new_user.otp = otp
            db.session.commit()
            send_otp_email(email, otp)

            flash('Account created successfully. Please check your email for OTP.', category='success')
            return redirect(url_for('auth.otpverify'))

           

   
    return render_template("signup.html") 


def generate_otp():
    totp = pyotp.TOTP(pyotp.random_base32())
    return totp.now()
    
def send_otp():
    email = request.form.get('email')
    otp = generate_otp()
    # Store email and OTP in the database
    send_otp_email(email, otp)
    return 'OTP sent to your email'

def send_otp_email(email, otp):
    msg = Message('Email Verification OTP', sender='ahere094@gmail.com', recipients=[email])
    msg.body = f'Your OTP is for verification: {otp}'
    mail.send(msg)

@auth.route('/otpverify', methods=['GET', 'POST'])
def otpverify():
    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        new_user_id = session.get('new_user_id')

        if new_user_id:
            new_user = User.query.get(new_user_id)

            if new_user:
                if new_user.otp == entered_otp:
                    new_user.is_verified = 1
                    db.session.commit()
                    login_user(new_user)
                    
                    return redirect(url_for('views.home'))
                else:
                    flash('Invalid OTP. Please try again.', category='error')

    return render_template("otpverify.html")









