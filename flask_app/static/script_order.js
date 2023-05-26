// ************** Get all menu items *******************************************************
addEventListener('load', () => {
    let col_1 = document.querySelector('.col-1')
    let col_2 = document.querySelector('.col-2')

    col_1.innerHTML = '<img class="loading-gif" src="https://upload.wikimedia.org/wikipedia/commons/b/b1/Loading_icon.gif?20151024034921" alt="loading-gif">'
    col_2.innerHTML = '<img class="loading-gif" src="https://upload.wikimedia.org/wikipedia/commons/b/b1/Loading_icon.gif?20151024034921" alt="loading-gif">'

    fetch('/get_all_items')
    .then(response => response.json())
    .then(data => {

        let col_1_html = ''
        let col_2_html = ''

        for (var i = 0; i < data.length; i++){
            if (i % 2 == 0){

                col_1_html += `
                <div class="item">
                <details>
                    <summary>
                        <div class="title_desc">
                            <h3>${data[i].name}</h3>
                            <p>${data[i].description}</p>
                        </div>
                        <p>$<span id="price">${data[i].price}</span></p>
                    </summary>
                    <form class="add_to_cart_form">
                        <div class="quantity-container">
                            <label for="quantity" id="quantity" name="quantity">Quantity: </label>
                            <input type="number" name="quantity" value="1" class="quantity">
                        </div>
    
                        <input type="hidden" name="prod_id" value="${data[i].id}">
                        <input type="submit" value="Add to cart!">
                    </form>
                </details>
                </div>
                `
            }
            if (i % 2 == 1){

                col_2_html += `
                <div class="item">
                <details>
                    <summary>
                        <div class="title_desc">
                            <h3>${data[i].name}</h3>
                            <p>${data[i].description}</p>
                        </div>
                        <p>$<span id="price">${data[i].price}</span></p>
                    </summary>
                    <form class="add_to_cart_form" method='post'>
                        <div class="quantity-container">
                            <label for="quantity" id="quantity" name="quantity">Quantity: </label>
                            <input type="number" name="quantity" value="1" class="quantity">
                        </div>
    
                        <input type="hidden" name="prod_id" value="${data[i].id}">
                        <input type="submit" value="Add to cart!">
                    </form>
                </details>
                </div>
                `
            }
        }
        col_1.innerHTML = col_1_html
        col_2.innerHTML = col_2_html
    })

    // ********************** After all items have been loaded**********************************************
    // Add an event listener to each form
    .then(() => {
        let forms = document.querySelectorAll('.add_to_cart_form')

        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                e.preventDefault()

                let form_data = new FormData(form)

                fetch('/add_to_cart', {method : 'POST', body : form_data})
                .then(response => response.json())
                .then(data => {
                    document.querySelector('.error-message').innerHTML = ''

                    let cart = document.querySelector('.cart-items')
                    let running_total = parseFloat(document.getElementById('running-total').innerHTML)

                    //If the item is already stored in session, we calculate new quantity
                    //Else, we add a new div to display what the customer added
                    if (data.in_session){
                        document.getElementById(`${data.default_price}`).innerHTML = data.in_cart
                    } else {
                        cart.innerHTML += `
                            <div class="cart-item ${data.id}">
                                <h4>${data.name}</h4>
                                <div class='cart-quantity'>
                                    <p>Quantity:</p>
                                    <p id=${data.default_price}> ${data.quantity} </p>
                                </div>
                                <button class='remove_from_cart' id=${data.id} value=${data.id}> <i class="fa-solid fa-trash"></i> </button>
                            </div>
                        `
                        // Add remove button right after the cart item is created
                        let remove_buttons = document.querySelectorAll('.remove_from_cart')
                        if (remove_buttons.length != 0){
                            remove_buttons.forEach(button => {
                                button.addEventListener('click', () => {
                                    let prod_id = button.value
                                    fetch(`/remove_from_cart/${prod_id}`)
                                    .then(response => response.json())
                                    .then(data2 => {
                                        document.querySelector(`.${prod_id}`).remove()
                                        running_total = parseFloat(document.getElementById('running-total').innerHTML)
                                        running_total -= data2.price * data2.quantity
                                        document.getElementById('running-total').innerHTML = running_total.toFixed(2)
                                    })
                                })
                            })
                        }
                    }


                    
                    //Update running total
                    running_total += data.price * data.quantity
                    document.getElementById('running-total').innerHTML = running_total.toFixed(2)

                    //Reset input values to one
                    let all_quantities = document.querySelectorAll('.quantity')
                    all_quantities.forEach(button => {
                        button.value = 1
                    })
                })
            })
        })
    })
});

//******************* Get cart items function *****************************
//Upon loading the page, gather all cart items from session if there are any

addEventListener('load', () => {
    fetch('/get_cart')
    .then(response => response.json())
    .then(data => {
        let cart = document.querySelector('.cart-items')
        let running_total = parseFloat(document.getElementById('running-total').innerHTML)
        document.querySelector('.error-message').innerHTML = ''
        if (data.in_cart == false){
            cart.innerHTML = ''
        } else {
            for (let item of data){
    
                //Should a user come back, gather all the cart items from session on the back-end
                cart.innerHTML += `
                    <div class="cart-item" id=${item.id}>
                        <h4>${item.name}</h4>
                        <div class='cart-quantity'>
                            <p>Quantity:</p>
                            <p id=${item.default_price}> ${item.quantity} </p>
                        </div>
                        <button class='remove_from_cart' value=${item.id}> <i class="fa-solid fa-trash"></i> </button>
                    </div>
                `
    
                //Calculate running total based on previous cart items
                running_total += item.price * item.quantity
                document.getElementById('running-total').innerHTML = running_total.toFixed(2)

                let remove_button = document.querySelector('.remove_from_cart')
                console.log(remove_button)
                remove_button.addEventListener('click', (e) => {
                    e.preventDefault()
    
                    let prod_id = (remove_button.value).toString()
    
                    fetch(`/remove_from_cart/${prod_id}`)
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById(prod_id).remove()
                        running_total -= data.price * data.quantity
                        console.log(data.price, data.quantity, running_total)
                        document.getElementById('running-total').innerHTML = running_total.toFixed(2)
                    })
                })
            }
        }
    })
})

