addEventListener('load', () => {
    fetch('/checkout_session_complete')
    .then(response => response.json())
    .then(data => {
        let cust_order = document.getElementById('cust-order')
        let cust_order_html = ''

        for (let key in data){  
            cust_order_html += ` ${data[key]} - ${key} ; `
        }

        cust_order.innerHTML = cust_order_html
    })
})