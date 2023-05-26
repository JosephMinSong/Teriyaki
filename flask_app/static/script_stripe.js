const button = document.getElementById('checkout');

button.addEventListener('click', e => {
    fetch('/stripe_pay')
    .then((result) => { return result.json() })
    .then((data) => {
        if (data.is_valid == false){
            document.querySelector('.error-message').innerHTML = `
                <p>${data.message}</p>
            `
        } else {
            var stripe = Stripe(data.checkout_public_key);
            stripe.redirectToCheckout({
                // Make the id field from the Checkout Session creation API response
                // available to this file, so you can provide it as parameter here
                // instead of the {{CHECKOUT_SESSION_ID}} placeholder.
                sessionId: data.checkout_session_id
            }).then(function (result) {
                // If `redirectToCheckout` fails due to a browser or network
                // error, display the localized error message to your customer
                // using `result.error.message`.
            })
        }
    })
});