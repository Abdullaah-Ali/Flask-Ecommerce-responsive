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

            # Return a JSON response indicating success
            return jsonify({'success': True, 'new_total': current_user.totalamt})

    # Return a JSON response indicating failure
    return jsonify({'success': False, 'error': 'Item not found or user does not have permission'})



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
        cart_data = get_cart_data(current_user.id)
        client_reference_id = f"user_{current_user.id}"

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=cart_data,
            mode='payment',
            success_url='http://127.0.0.1:5000/',
            cancel_url='http://127.0.0.1:5000/',
            billing_address_collection='required',
            #its just the shipping addresss code provided by the stripe docs for all the coutry for now can be changed according to the need of client !
    shipping_address_collection={
        'allowed_countries': [
            'AC', 'AD', 'AE', 'AF', 'AG', 'AI', 'AL', 'AM', 'AO', 'AQ', 'AR', 'AT', 'AU', 'AW', 'AX', 'AZ',
            'BA', 'BB', 'BD', 'BE', 'BF', 'BG', 'BH', 'BI', 'BJ', 'BL', 'BM', 'BN', 'BO', 'BQ', 'BR', 'BS', 'BT',
            'BV', 'BW', 'BY', 'BZ', 'CA', 'CD', 'CF', 'CG', 'CH', 'CI', 'CK', 'CL', 'CM', 'CN', 'CO', 'CR', 'CV',
            'CW', 'CY', 'CZ', 'DE', 'DJ', 'DK', 'DM', 'DO', 'DZ', 'EC', 'EE', 'EG', 'EH', 'ER', 'ES', 'ET', 'FI',
            'FJ', 'FK', 'FO', 'FR', 'GA', 'GB', 'GD', 'GE', 'GF', 'GG', 'GH', 'GI', 'GL', 'GM', 'GN', 'GP', 'GQ',
            'GR', 'GS', 'GT', 'GU', 'GW', 'GY', 'HK', 'HN', 'HR', 'HT', 'HU', 'ID', 'IE', 'IL', 'IM', 'IN', 'IO',
            'IQ', 'IS', 'IT', 'JE', 'JM', 'JO', 'JP', 'KE', 'KG', 'KH', 'KI', 'KM', 'KN', 'KR', 'KW', 'KY', 'KZ',
            'LA', 'LB', 'LC', 'LI', 'LK', 'LR', 'LS', 'LT', 'LU', 'LV', 'LY', 'MA', 'MC', 'MD', 'ME', 'MF', 'MG',
            'MK', 'ML', 'MM', 'MN', 'MO', 'MQ', 'MR', 'MS', 'MT', 'MU', 'MV', 'MW', 'MX', 'MY', 'MZ', 'NA', 'NC',
            'NE', 'NG', 'NI', 'NL', 'NO', 'NP', 'NR', 'NU', 'NZ', 'OM', 'PA', 'PE', 'PF', 'PG', 'PH', 'PK', 'PL',
            'PM', 'PN', 'PR', 'PS', 'PT', 'PY', 'QA', 'RE', 'RO', 'RS', 'RU', 'RW', 'SA', 'SB', 'SC', 'SE', 'SG',
            'SH', 'SI', 'SJ', 'SK', 'SL', 'SM', 'SN', 'SO', 'SR', 'SS', 'ST', 'SV', 'SX', 'SZ', 'TA', 'TC', 'TD',
            'TF', 'TG', 'TH', 'TJ', 'TK', 'TL', 'TM', 'TN', 'TO', 'TR', 'TT', 'TV', 'TW', 'TZ', 'UA', 'UG', 'US',
            'UY', 'UZ', 'VA', 'VC', 'VE', 'VG', 'VN', 'VU', 'WF', 'WS', 'XK', 'YE', 'YT', 'ZA', 'ZM', 'ZW'
        ],
    },
            client_reference_id=client_reference_id,
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
    formatted_due_datetime = None  # Initialize outside the if block

    if event_type == 'checkout.session.completed':
        session = event['data']['object']
        created_timestamp = session['created']
        customer_email = session['customer_details']['email']
        username = session['customer_details']['name']
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
        client_reference_id = session['client_reference_id']
        user_id = int(client_reference_id.split('_')[1])

        update_user_cart_and_total(user_id, session)
   
        line_items = stripe.checkout.Session.list_line_items(session['id'])
        product_info = "\n".join([f"Product: {item['description']}, Quantity: {item['quantity']}" for item in line_items.get('data', [])])
        print("Product Info:\n", product_info)

        created_datetime = datetime.utcfromtimestamp(created_timestamp)
        formatted_created_datetime = created_datetime.strftime('%Y-%m-%d')

        # Calculate due date as 14 days after creation
        due_datetime = created_datetime + timedelta(days=14)
        formatted_due_datetime = due_datetime.strftime('%Y-%m-%d')  # Use '%Y-%m-%d' for only date
        print(f"The date that the recipient is created at is {formatted_created_datetime} and the due date is {formatted_due_datetime}")
        
        find_mail(user_id, line_items, city, country, line1, line2, state, invoice_number, username, customer_email, formatted_due_datetime, formatted_created_datetime)
          
    elif event_type == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        
    elif event_type == 'charge.succeeded':
        charge = event['data']['object']

    else:
        print('Unhandled event type {}'.format(event_type))

    return jsonify(success=True)

def update_user_cart_and_total(user_id, session):
    # Assuming you have a method to retrieve the user based on user_id
    user = User.query.get(user_id)

    # Clear the user's cart (delete all cart entries)
    Cart.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    
    
def find_email_by_user_id(user_id):
    # Assuming you have a method to retrieve the user based on user_id
    user = User.query.get(user_id)

    if user:
        return user.email
        
    else:
        return None 
    
def find_mail(user_id, line_items, city, country, line1, line2, state, invoice_number , username , customer_email , formatted_created_datetime , formatted_due_datetime):
    customer_email = find_email_by_user_id(user_id)

    if customer_email:
        print(f"Customer Email found: {customer_email}")
        product_details = [{'description': item['description'], 'quantity': item['quantity'], 'price': item['price']['unit_amount_decimal']} for item in line_items.get('data', [])]
        address_mail = f"{country}, {city}, {line1}, {line2}, {state}"
        invoice_mail_no = invoice_number

        send_invoice_email(customer_email, product_details, address_mail, invoice_mail_no, username, customer_email , formatted_created_datetime , formatted_due_datetime)
    else:
        print("Customer Email not found")
        
def calculate_grand_total(product_details):
    prices = [float(item['price']) for item in product_details]
    print("Prices:", prices)
    return sum(prices)




def send_invoice_email(recipient, product_details, address, invoice_number , username , customer_email , formatted_created_datetime , formatted_due_datetime):
    # Render the HTML template with actual data
    
    html_content = render_template('invoice.html', product_details=product_details, address=address, invoice_number=invoice_number ,  username=username , recipient=customer_email ,created_at=formatted_created_datetime , due_at=formatted_due_datetime )

    # Send the email
    logo_path = os.path.join(current_app.root_path, "static/images/logo.png")

    msg = Message('Invoice from Red Ecommerce Store', sender='ahere094@gmail.com', recipients=[recipient])
    with open(logo_path, "rb") as logo:
        msg.attach('logo.png', 'image/png', logo.read(), 'inline', headers=[['Content-ID', '<logo-image>']])
    
    msg.html = html_content
    
 

    mail.send(msg)
    print("Email sent successfully")



