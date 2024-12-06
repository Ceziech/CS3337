document.addEventListener('DOMContentLoaded', () => {
    const checkoutTable = document.getElementById('checkout-table');
    const subtotalElement = document.getElementById('subtotal');
    const taxElement = document.getElementById('tax');
    const totalElement = document.getElementById('total');
    const placeOrderButton = document.getElementById('place-order-btn');

    const cart = JSON.parse(localStorage.getItem('cart')) || [];
    const taxRate = 0.10;

    if (cart.length === 0) {
        // Display a message if the cart is empty
        const emptyMessage = document.createElement('p');
        emptyMessage.textContent = 'Your cart is empty. Please add items to proceed.';
        emptyMessage.style.textAlign = 'center';
        checkoutTable.parentElement.insertBefore(emptyMessage, checkoutTable);
        checkoutTable.style.display = 'none'; // Hide the table
        placeOrderButton.style.display = 'none'; // Hide the place order button
        return;
    }

    let subtotal = 0;

    // Populate the table with cart items
    cart.forEach((item) => {
        subtotal += item.price;
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${item.name}</td>
            <td>$${item.price.toFixed(2)}</td>
        `;
        checkoutTable.appendChild(row);
    });

    // Calculate totals
    const tax = subtotal * taxRate;
    const total = subtotal + tax;

    subtotalElement.textContent = `Sub-Total: $${subtotal.toFixed(2)}`;
    taxElement.textContent = `City of Los Angeles 10% Parking Occupancy Tax: $${tax.toFixed(2)}`;
    totalElement.textContent = `Total: $${total.toFixed(2)}`;

    // Place order button event listener
    placeOrderButton.addEventListener('click', () => {
        alert('Order placed successfully!');
        localStorage.removeItem('cart'); // Clear the cart
        window.location.href = 'confirmation.html'; // Redirect to confirmation page
    });
});
