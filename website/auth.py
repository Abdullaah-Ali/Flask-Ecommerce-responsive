from .models import User
from website import db, mail   # Import the 'mail' instance from the main app
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, render_template, Flask, request, flash, redirect, url_for, session
from flask_login import login_user, login_required, logout_user, current_user
from flask_mail import Message
import pyotp
from website import views
from website import oauth


from flask_oauthlib.client import OAuth




auth = Blueprint('auth', __name__)




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




oauth.register(
    name='google',
    client_id='464462423467-hrrha457ptid2g0j132pet8316d64klk.apps.googleusercontent.com',
    client_secret='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',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    redirect_uri='http://127.0.0.1:5000/authorize',  # Add your redirect URI if needed
    client_kwargs={"scope": "openid profile email"},
    jwks_uri='https://www.googleapis.com/oauth2/v3/certs'
)


@auth.route('/google_register', methods=['GET', 'POST'])
def google_register():
    if request.method == 'POST':
        print("The function is being called and hence it's good to go")
        google = oauth.create_client('google')
        redirect_uri = url_for('auth.authorize', _external=True)
        return google.authorize_redirect(redirect_uri)

@auth.route('/authorize')
def authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('https://www.googleapis.com/oauth2/v1/userinfo')
    resp.raise_for_status()
    profile = resp.json()
    first_name = profile.get('given_name')
    email = profile.get('email')
    user = User.query.filter_by(email=email).first()
    if user:
        # If the user exists, authenticate them
        login_user(user)
        flash(f'Welcome back, {first_name}!', category='success')
    else:
        # If the user doesn't exist, add them to the database
        new_user = User(email=email, first_name=first_name, is_verified= 1)
        db.session.add(new_user)
        db.session.commit()

        # Automatically authenticate the new user
        login_user(new_user)
        flash(f'Welcome, {first_name}! You have been automatically verified.', category='success')

    # Redirect to the home page or any other desired page
    return redirect(url_for('views.home'))

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









