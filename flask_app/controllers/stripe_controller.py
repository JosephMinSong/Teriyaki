from flask_app import app
from flask import render_template, redirect, session, request, flash, url_for, abort, jsonify
from flask_app.models.user_model import User
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)
import os
from dotenv import load_dotenv
load_dotenv()

import stripe

app.config['STRIPE_PUBLIC_KEY'] = os.getenv('STRIPE_PUBLIC_KEY')
app.config['STRIPE_SECRET_KEY'] = os.getenv('STRIPE_SECRET_KEY')

app.config['STRIPE_ENDPOINT_SECRET'] = os.getenv('STRIPE_SECRET_ENDPOINT')

stripe.api_key = app.config['STRIPE_SECRET_KEY']


# ********************** Get all items ***********************************************
@app.route('/get_all_items')
def get_all():
    result = stripe.Product.list(limit=100, active=True)['data']

    all_items = []
    for item in result:
        item.price = (stripe.Price.retrieve(item['default_price'])['unit_amount'])/100
        all_items.append(item)

    all_items.reverse()
    return jsonify(all_items)


# ************************ Get cart items *******************************************
@app.route('/get_cart')
def get_cart():

    all_items = []
    for key in session:
        if key != 'user_id':
            one_item = stripe.Product.retrieve(key)
            one_item['quantity'] = session[one_item['id']]
            one_item['price'] = (stripe.Price.retrieve(one_item['default_price'])['unit_amount'])/100
            all_items.append(one_item)

    if len(all_items) == 0:
        return {'in_cart' : False}
    
    return jsonify(all_items)


# **************************** Add to cart ************************************
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():

    product_id = request.form['prod_id']
    quantity = request.form['quantity']

    result = stripe.Product.retrieve(product_id)

    # If the product is already in our cart (via session)
    # We also return a "True" value to our JS to add logic there
    if product_id in session:

        # We add the additional quantity to our existing quantity in session
        result.in_session = True

        session[product_id] += int(quantity)
        result.in_cart = session[product_id]
        result.quantity = int(quantity)
        result.price = (stripe.Price.retrieve(result['default_price'])['unit_amount'])/100
        return jsonify(result)

    # Else, we get the price and send it over as well
    result.price = (stripe.Price.retrieve(result['default_price'])['unit_amount'])/100

    # We store the item's id as a key and the quantity of the item as it's value
    session[product_id] = int(quantity)
    result.quantity = int(quantity)
    result.in_cart = session[product_id]
    return jsonify(result)


# ********************* Remove from cart ******************************************
@app.route('/remove_from_cart/<string:prod_id>')
def remove(prod_id):
    quantity = session[prod_id]
    result = stripe.Product.retrieve(prod_id)
    result.price = (stripe.Price.retrieve(result['default_price'])['unit_amount'])/100
    del session[prod_id]
    
    return {'quantity' : quantity, 'price' : result.price}


# ************************** Stripe Pay ***************************************************
@app.route('/stripe_pay')
def stripe_pay():

    # Create a list of item dictionaries for stripe
    all_items = []
    if len(session) == 0:
        return {'is_valid': False, 'message' : "Please add items to cart before checkout"}
    else: 
        for key in session:
            if key != 'user_id':
                one_item_data = stripe.Product.retrieve(key)
                one_item = {}
                one_item['price'] = one_item_data['default_price']
                one_item['quantity'] = session[key]
                all_items.append(one_item)

    # Now create the stripe session through stripe api
    stripe_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=all_items,
        mode='payment',
        automatic_tax={ 'enabled' : True },
        success_url=url_for('thankyou', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('order', _external=True)
    )

    # Per stripe's api, we need to send the session id and public key to our JS
    return {
        'checkout_session_id': stripe_session['id'], 
        'checkout_public_key': app.config['STRIPE_PUBLIC_KEY']
    }

# ********************** Checkout Session Complete ******************************************
@app.route('/checkout_session_complete')
def checkout_session_complete():
    all_items = {}
    for key in session:
        if 'user_id' in session:
            if key != 'user_id':
                item_data = {
                    'user_id' : session['user_id'],
                    'product_id' : key
                }
                ordered_item = stripe.Product.retrieve(key)['name']
                all_items[ordered_item] = session[key]
                User.add_favorite(item_data)
        else:
            ordered_item = stripe.Product.retrieve(key)['name']
            all_items[ordered_item] = session[key]
    
    for key in list(session.keys()):
        if key != 'user_id':
            session.pop(key)
    return all_items

# ****************** Stripe Webhook Listener **************************
@app.route('/stripe_webhook', methods=['POST'])
def stripe_webhook():

    # If the content is bigger than a megabyte, we abort since no payment should be this big
    if request.content_length > 1024 * 1024:
        print("REQUEST TOO BIG")
        abort(400)

    # Gather data for Stripe's endpoint
    payload = request.get_data()
    sig_header = request.environ.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = app.config['STRIPE_ENDPOINT_SECRET']
    event = None

    try:
        event = stripe.Webhook.construct_event(
        payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        print('INVALID PAYLOAD')
        return {}, 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print('INVALID SIGNATURE')
        return {}, 400

    # Handle the checkout session completed event and print order
    if event['type'] == 'checkout.session.completed':
        stripe_session_webhook = event['data']['object']
        all_line_items = stripe.checkout.Session.list_line_items(stripe_session_webhook['id'])

        all_items = []
        for item in all_line_items:
            all_items.append(item['description'])

        print(all_items)

    return {}
