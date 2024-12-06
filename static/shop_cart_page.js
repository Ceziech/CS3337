document.addEventListener('DOMContentLoaded', () => {
    let cart = [];
    const taxRate = 0.10;

    const cartTable = document.getElementById('cart-table');
    const subtotalElement = document.getElementById('subtotal');
    const taxElement = document.getElementById('tax');
    const totalElement = document.getElementById('total');
    const removeAllButton = document.getElementById('remove-item-btn');
    const addPermitForm = document.getElementById('add-permit-form');
    const continueButton = document.getElementById('continue-btn');

    const permitPrices = {
        '1-day': { name: '1-Day Parking Permit', price: 10.00 },
        '7-day': { name: '7-Day Parking Permit', price: 50.00 },
        '30-day': { name: '30-Day Parking Permit', price: 100.00 },
    };

    addPermitForm.addEventListener('submit', (event) => {
        event.preventDefault();

        const permitType = document.getElementById('permit-type').value;
        if (permitType && permitPrices[permitType]) {
            addItemToCart(permitPrices[permitType]);
            updateCartDisplay();
        }
    });

    continueButton.addEventListener('click', () => {
        // Check if the cart has items
        if (cart.length === 0) {
            alert('Your cart is empty. Please add items before continuing.');
            return;
        }

        // Save the cart to localStorage
        localStorage.setItem('cart', JSON.stringify(cart));

        // Redirect to the checkout page
        window.location.href = 'checkout.html';
    });

    function addItemToCart(item) {
        cart.push(item);
    }

    function removeItem(index) {
        cart.splice(index, 1);
        updateCartDisplay();
    }

    function updateCartDisplay() {
        cartTable.innerHTML = `
            <tr>
                <th>Item</th>
                <th>Price</th>
                <th>Remove</th>
            </tr>
        `;

        let subtotal = 0;

        cart.forEach((item, index) => {
            subtotal += item.price;
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${item.name}</td>
                <td>$${item.price.toFixed(2)}</td>
                <td><button class="remove-btn" data-index="${index}">Remove</button></td>
            `;
            cartTable.appendChild(row);
        });

        const tax = subtotal * taxRate;
        const total = subtotal + tax;

        subtotalElement.textContent = `Sub-Total: $${subtotal.toFixed(2)}`;
        taxElement.textContent = `City of Los Angeles 10% Parking Occupancy Tax: $${tax.toFixed(2)}`;
        totalElement.textContent = `Total: $${total.toFixed(2)}`;

        // Attach remove event listeners
        document.querySelectorAll('.remove-btn').forEach((btn) => {
            btn.addEventListener('click', () => {
                const index = btn.dataset.index;
                removeItem(index);
            });
        });
    }

    removeAllButton.addEventListener('click', () => {
        cart = [];
        updateCartDisplay();
    });
});
