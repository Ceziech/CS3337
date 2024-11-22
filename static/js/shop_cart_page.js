document.addEventListener('DOMContentLoaded', () => {
    let cart = [];
    const taxRate = 0.10; // 10% tax rate

    const cartTable = document.getElementById('cart-table');
    const subtotalElement = document.getElementById('subtotal');
    const taxElement = document.getElementById('tax');
    const totalElement = document.getElementById('total');
    const removeItemButton = document.getElementById('remove-item-btn');

    // Example item to add for demonstration
    const item = {
        name: 'Permit - 1-Day Event and Visitor Parking Permit',
        price: 10.00
    };

    // Add a sample item for visual demo
    addItemToCart(item);
    updateCartDisplay();

    function addItemToCart(item) {
        cart.push(item);
    }

    function removeItemFromCart() {
        if (cart.length > 0) {
            cart.pop(); // Removes the last item
            updateCartDisplay();
        }
    }

    function updateCartDisplay() {
        // Clear current table rows (except header)
        cartTable.innerHTML = `
            <tr>
                <th>Item</th>
                <th>Price</th>
                <th>View</th>
            </tr>
        `;

        let subtotal = 0;

        // Display each item in the cart
        cart.forEach((item, index) => {
            subtotal += item.price;
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${item.name}</td>
                <td>$${item.price.toFixed(2)}</td>
                <td><button onclick="removeItem(${index})">Remove</button></td>
            `;
            cartTable.appendChild(row);
        });

        // Update cart totals
        const tax = subtotal * taxRate;
        const total = subtotal + tax;

        subtotalElement.textContent = `Sub-Total: $${subtotal.toFixed(2)}`;
        taxElement.textContent = `City of Los Angeles 10% Parking Occupancy Tax: $${tax.toFixed(2)}`;
        totalElement.textContent = `Total: $${total.toFixed(2)}`;
    }

    // Button event listener
    removeItemButton.addEventListener('click', removeItemFromCart);
});
