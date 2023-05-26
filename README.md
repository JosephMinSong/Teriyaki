# Teriyaki Bowl
![Picture of teriyaki chicken](https://static01.nyt.com/images/2016/05/28/dining/28COOKING-CHICKEN-TERIYAKI1/28COOKING-CHICKEN-TERIYAKI1-videoSixteenByNineJumbo1600.jpg)

## The motivation behind this project was to build a comfortable, yet sleek web application for my parent's restaurant. 

### The main goal of the project was to not only build a website where people could order delicious teriyaki, but to also ensure the safety and privacy of the user's information (i.e. credit card)
### Project built with Python, JavaScript, Flask, Jinja2, MySQL, HTML/CSS and incorporates AJAX, Bcrypt, Stripe API, Google Map API  

A huge part of this project is the incorporation of **Stripe API** as part of the user experience. 
From Stripes already existing database, I was able to reduce the amount of code and instead, utilize AJAX to dynamically build my order page. Should anything change with the menu, the only changes would only
be needed in Stripe!

```py
@app.route('/get_all_items')
def get_all():
    result = stripe.Product.list(limit=100, active=True)['data']

    all_items = []
    for item in result:
        item.price = (stripe.Price.retrieve(item['default_price'])['unit_amount'])/100
        all_items.append(item)

    all_items.reverse()
    return jsonify(all_items)
```

From here, I am given all of my products as a JSON for my front-end JavaScript to read and use.

To give my paying customers the feeling of safety and security, I utilize Stripes checkout session by sending the product id's from my customers cart to Stripe. 
Stripe can then process the product id's and produce a secure checkout session where we never see their sensitive credit card information **ever**. 

![Picture of stripe checkout session](https://res.cloudinary.com/practicaldev/image/fetch/s--CDbO1zkG--/c_imagga_scale,f_auto,fl_progressive,h_900,q_auto,w_1600/https://dev-to-uploads.s3.amazonaws.com/i/fk71m1mwmkukvbbewo5a.png)

Finally, by utilizing a webhook, we can listen for any completed, successful checkout sessions from Stripe to see what the customer ordered and make their dish. 

```py
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
```







