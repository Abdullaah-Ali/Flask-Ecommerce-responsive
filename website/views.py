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
import stripe
from flask import jsonify
import pprint




views = Blueprint('views',__name__ )


#defininf the root so whenever its hit homepage is called
@views.route('/')
def home():
    return render_template('home.html')


def update_totalamt(user):
    # Calculate the total amount based on cart items
    user.totalamt = sum(item.productPrice * item.quantity if item.productPrice is not None else 0 for item in user.items)
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

stripe.api_key = 'sk_test_51OEbyRI3XvqE4k0A54gimD8HmieuLuGXRcwSgmPwwoGtAh2eoLQAYZW1IU5TqNOshgbbZlPyVPzhwPqRRqu8Uig100kbtGtV9t'
def get_cart_data(user_id):
    cart_items = Cart.query.filter_by(user_id=user_id).all()

    cart_data = []
    for item in cart_items:
        if item.productPrice is not None:
            cart_data.append({
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': item.productName,
                    },
                    'unit_amount': int(item.productPrice * 100),  # Amount in cents
                },
                'quantity': item.quantity,
            })

    return cart_data


@login_required
@views.route('/checkout', methods=['GET' , 'POST'])
def checkout():
    try:
        # Get the user's cart data dynamically from the database
        cart_data = get_cart_data(current_user.id)

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=cart_data,
            mode='payment',
            success_url='https://your-website.com/success',
            cancel_url='https://your-website.com/cart',
            billing_address_collection='required',
            shipping_address_collection={
                'allowed_countries': ['US'],  # Specify the allowed countries for shipping
            }
        )

        # Retrieve the Checkout Session ID from the response
        checkout_session_id = checkout_session.id

        # Construct the redirect URL using the Checkout Session ID
        checkout_url = f"https://checkout.stripe.com/checkout/session/{checkout_session_id}"

        # Redirect the user to the Stripe Checkout page
        return redirect(checkout_session.url)

    except stripe.error.StripeError as e:
        print("Stripe Error:", str(e))
        return str(e)
    except Exception as e:
        print("Exception:", str(e))
        return str(e)
    
    
#making an function call to parse the data from the stripe and then send it and update ita ccordingly
endpoint_secret = 'whsec_fab2a19aef2652987a16dbe97fd606b9eaa79eab123cdb9080a9cf388d6025b2'


@views.route('/webhook', methods=['POST'])
def webhook():
    event = None
    payload = request.data
    sig_header = request.headers['STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        raise e
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise e

    # Handle the event
    event_type = event['type']
    if event_type == 'checkout.session.completed':
        session = event['data']['object']
        customer_email = session['customer_details']['email']
        invoice_number = session['payment_intent']
        shipping_details = session.get('shipping_details', {})
        address = shipping_details.get('address', {})

        # Access specific fields within the address
        city = address.get('city', 'N/A')
        country = address.get('country', 'N/A')
        line1 = address.get('line1', 'N/A')
        line2 = address.get('line2', 'N/A')
        postal_code = address.get('postal_code', 'N/A')
        state = address.get('state', 'N/A')

        print(f"Customer Email: {customer_email}, Invoice Number: {invoice_number}, Address: {city}, {country}, {line1}, {line2}, {postal_code}, {state}")

    elif event_type == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        
    elif event_type == 'charge.succeeded':
        charge = event['data']['object']

    else:
        print('Unhandled event type {}'.format(event_type))

    return jsonify(success=True)