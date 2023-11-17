from flask import Blueprint , render_template
from flask import redirect , url_for
from flask_login import  login_required ,  current_user
from flask import request
from website import db 
from flask import current_app, session
from flask_login import current_user
from .models import User, Note , Cart
from sqlalchemy.exc import SQLAlchemyError
import requests
from flask import flash
import random





views = Blueprint('views',__name__ )


#defininf the root so whenever its hit homepage is called
@views.route('/')
def home():
    return render_template('home.html')


def update_totalamt(user):
    # Calculate the total amount based on cart items
    user.totalamt = sum(item.productPrice * item.quantity for item in user.items)
    db.session.commit()
    print("After update - Total Amount:", user.totalamt)
    
#when the button for the cart is clicked then the db should be upadted from the product and the price of it it
@views.route('/', methods=['POST', 'GET'])
@login_required
def addproduct():
    if request.method == 'POST':
    # Get the product name and product price from the form data
        product_name = request.form.get('product_name')
        product_price = request.form.get('product_price')

    # Check if the product is already in the user's cart
        existing_item = Cart.query.filter_by(productName=product_name, user_id=current_user.id).first()

        if existing_item:
            # If the product is already in the cart, increment the quantity
            existing_item.quantity += 1
        else:
            # Get the current user's ID using the Flask-Login current_user attribute
            user_id = current_user.id
            # Create a new Note and add it to the database
            new_product = Cart(productName=product_name, user_id=user_id, productPrice=product_price, quantity=1)
            db.session.add(new_product)

        
        
        db.session.commit()
        update_totalamt(current_user)
        return redirect(url_for('views.home'))
    


@login_required
@views.route('/remove_from_cart/<int:item_id>', methods=['POST'])
def remove_from_cart(item_id):
    if request.method == 'POST':
        item_to_remove = Cart.query.get(item_id)
    
        if item_to_remove and item_to_remove.user_id == current_user.id:
            # Remove the item from the database
            db.session.delete(item_to_remove)
            db.session.commit()
            update_totalamt(current_user)

    return redirect(url_for('views.home'))
