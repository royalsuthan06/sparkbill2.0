function addToCart() {
    const skuInput = document.getElementById('sku-input');
    const qtyInput = document.getElementById('qty-input');
    const sku = skuInput.value.trim();
    const qty = parseInt(qtyInput.value) || 1;

    if (qty <= 0) {
        showToast('Quantity must be greater than 0!', 'error');
        return;
    }

    const product = findProductBySku(sku);
    if (!product) {
        showToast('Product not found!', 'error');
        return;
    }

    const existing = SparkBill.cartItems.find(ci => ci.product_id === product.id);

    if (existing) {
        existing.quantity += qty;
    } else {
        SparkBill.cartItems.push({
            product_id: product.id,
            product_name: product.name,
            price: product.price,
            quantity: qty
        });
    }

    renderCart();
    skuInput.value = '';
    qtyInput.value = 1;
    document.getElementById('product-preview').textContent = '-';
    const dd = document.getElementById('sku-dropdown');
    if (dd) { dd.classList.add('hidden'); dd.innerHTML = ''; }
    skuInput.focus();
}

function renderCart() {
    const tbody = document.getElementById('bill-table-body');
    let sno = 1;
    tbody.innerHTML = SparkBill.cartItems.map((item, idx) => {
        const total = item.quantity * item.price;
        const isNav = idx === SparkBill.cartNavIndex;
        return `
            <tr class="zebra-row transition-all ${isNav ? 'bg-error/15 border-l-4 border-l-error' : ''}">
                <td class="p-padding-cell font-data-md ${isNav ? 'text-error font-bold' : ''}">${sno++}</td>
                <td class="p-padding-cell font-body-md ${isNav ? 'text-error font-semibold' : 'text-on-surface'}">${escapeHtml(item.product_name)}</td>
                <td class="p-padding-cell font-data-md text-right ${isNav ? 'text-error' : 'text-on-surface-variant'}">
                    ₹${item.price.toFixed(2)}
                </td>
                <td class="p-padding-cell text-right">
                    <input type="number" class="w-20 bg-transparent border border-outline-variant rounded p-1 text-center text-primary font-bold cart-qty-input" data-product-id="${item.product_id}" value="${item.quantity}" min="1" />
                </td>
                <td class="p-padding-cell text-right font-semibold text-data-lg ${isNav ? 'text-error' : ''}">₹${total.toFixed(2)}</td>
                <td class="p-padding-cell text-center">
                    <button class="text-error hover:text-error/80 remove-cart-btn" data-product-id="${item.product_id}">
                        <span class="material-symbols-outlined text-[20px]">delete</span>
                    </button>
                </td>
            </tr>
        `;
    }).join('');

    const totalItems = SparkBill.cartItems.reduce((sum, i) => sum + i.quantity, 0);
    const subtotal = SparkBill.cartItems.reduce((sum, i) => sum + (i.price * i.quantity), 0);
    document.getElementById('subtotal-display').textContent = subtotal.toFixed(2);
    document.getElementById('grand-total-val').textContent = subtotal.toFixed(2);
    document.getElementById('units-display').textContent = `Items: ${totalItems} Units`;
}

function updateCartItemQty(productId, qty) {
    const item = SparkBill.cartItems.find(i => i.product_id === productId);
    const newQty = parseInt(qty) || 1;
    if (item) {
        item.quantity = newQty;
        if (item.quantity <=0) removeFromCart(productId);
        else renderCart();
    }
}

function removeFromCart(productId) {
    SparkBill.cartItems = SparkBill.cartItems.filter(i => i.product_id !== productId);
    SparkBill.cartNavIndex = -1;
    renderCart();
}

function removeFromCartByIndex(index) {
    if (index >= 0 && index < SparkBill.cartItems.length) {
        const removed = SparkBill.cartItems.splice(index, 1)[0];
        SparkBill.cartNavIndex = -1;
        renderCart();
        showToast(`Removed "${removed.product_name}"`, 'success');
    } else {
        showToast('Invalid S.No!', 'error');
    }
}

async function voidCart() {
    if (await askConfirmation('Are you sure you want to void this bill?')) {
        SparkBill.cartItems = [];
        SparkBill.cartNavIndex = -1;
        renderCart();
        document.getElementById('product-preview').textContent = '-';
    }
}

async function checkout() {
    if (SparkBill.cartItems.length === 0) {
        showToast('Cart is empty!', 'error');
        return;
    }

    const checkoutBtn = document.getElementById('checkout-btn');
    if (checkoutBtn.disabled) return;
    checkoutBtn.disabled = true;
    checkoutBtn.innerHTML = '<span class="text-xs uppercase tracking-[0.2em] mb-1 font-bold">Processing...</span>';

    const customerName = document.getElementById('customer-name').value;
    const customerMobile = document.getElementById('customer-mobile').value;

    const saleData = {
        customer_name: customerName,
        customer_mobile: customerMobile,
        payment_method: 'Cash',
        items: SparkBill.cartItems.map(i => ({
            product_id: i.product_id,
            quantity: i.quantity
        }))
    };

    try {
        const res = await fetch(`${API_BASE}/sales`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(saleData)
        });

        if (res.ok) {
            const result = await res.json();
            showToast('Sale completed successfully!', 'success');
            
            if (result && result.id) {
                showPdfModal(result.id);
            }
            
            SparkBill.cartItems = [];
            SparkBill.cartNavIndex = -1;
            renderCart();
            document.getElementById('customer-name').value = '';
            document.getElementById('customer-mobile').value = '';
            document.getElementById('sku-input').value = '';
            document.getElementById('product-preview').textContent = '-';
            await loadProducts();
            await loadStats();
            await loadSales();
        } else {
            const errorData = await res.json();
            showToast(`Failed to complete sale: ${errorData.error || 'Unknown error'}`, 'error');
        }
    } catch (err) {
        console.error(err);
        showToast('An error occurred while processing the sale.', 'error');
    } finally {
        checkoutBtn.disabled = false;
        checkoutBtn.innerHTML = '<span class="text-xs uppercase tracking-[0.2em] mb-1 font-bold">Confirm & Print</span>F12 - GENERATE INVOICE';
    }
}

document.addEventListener('click', (e) => {
    const removeBtn = e.target.closest('.remove-cart-btn');
    if (removeBtn) { removeFromCart(parseInt(removeBtn.dataset.productId)); return; }
});

document.addEventListener('change', (e) => {
    if (e.target.classList.contains('cart-qty-input')) {
        updateCartItemQty(parseInt(e.target.dataset.productId), e.target.value);
    }
});
