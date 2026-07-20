const API_BASE = '/api';

let products = [];
let cartItems = [];
let currentView = 'billing';
let editingProductId = null;

async function init() {
    updateDate();
    await loadProducts();
    await loadStats();
    await loadSales();
    setupEventListeners();
    switchView('billing');
}

function updateDate() {
    const now = new Date();
    document.getElementById('bill-date').textContent = now.toLocaleDateString('en-IN');
}

async function loadProducts() {
    try {
        const res = await fetch(`${API_BASE}/products`);
        products = await res.json();
        renderInventoryTable();
    } catch (err) {
        console.error('Failed to load products:', err);
    }
}

async function loadStats() {
    try {
        const res = await fetch(`${API_BASE}/stats`);
        const stats = await res.json();
        document.getElementById('stat-total-skus').textContent = stats.total_skus;
        document.getElementById('stat-low-stock').textContent = stats.low_stock_items;
        document.getElementById('stat-inventory-value').textContent = `₹${stats.inventory_value.toFixed(2)}`;
        document.getElementById('stat-categories').textContent = [...new Set(products.map(p => p.category))].length;

        document.getElementById('report-today-sales').textContent = `₹${stats.today_sales.toFixed(2)}`;
        document.getElementById('report-today-count').textContent = stats.today_count;
        const avgBill = stats.today_count > 0 ? (stats.today_sales / stats.today_count).toFixed(2) : '0.00';
        document.getElementById('report-avg-bill').textContent = `₹${avgBill}`;
    } catch (err) {
        console.error('Failed to load stats:', err);
    }
}

async function loadSales() {
    try {
        const res = await fetch(`${API_BASE}/sales`);
        const sales = await res.json();
        renderReportsTable(sales);
    } catch (err) {
        console.error('Failed to load sales:', err);
    }
}

function renderInventoryTable() {
    const tbody = document.getElementById('inventory-table-body');
    tbody.innerHTML = products.map(p => {
        let badgeClass = 'bg-emerald-100 text-emerald-700 border-emerald-200';
        let dotClass = 'bg-emerald-500';
        let status = 'Healthy';
        if (p.stock_quantity < 30) {
            badgeClass = 'bg-red-100 text-red-700 border-red-200';
            dotClass = 'bg-red-500';
            status = 'Low Stock';
        } else if (p.stock_quantity < 60) {
            badgeClass = 'bg-amber-100 text-amber-700 border-amber-200';
            dotClass = 'bg-amber-500';
            status = 'Warning';
        }
        return `
            <tr class="zebra-row hover:bg-surface-container transition-colors cursor-default">
                <td class="px-4 py-2 font-mono text-primary font-semibold text-[13px]">${p.sku}</td>
                <td class="px-4 py-2 text-on-surface font-semibold outline-none">${p.name}</td>
                <td class="px-4 py-2 text-on-surface-variant outline-none">${p.category || '-'}</td>
                <td class="px-4 py-2 text-center">
                    <span class="inline-flex items-center px-2 py-0.5 rounded-full ${badgeClass} text-[11px] font-semibold border">
                        <span class="w-1.5 h-1.5 rounded-full ${dotClass} mr-1.5"></span>
                        ${p.stock_quantity} ${status}
                    </span>
                </td>
                <td class="px-4 py-2 font-mono text-right text-on-surface outline-none">₹${p.cost_price.toFixed(2)}</td>
                <td class="px-4 py-2 font-mono text-right text-on-surface outline-none">₹${p.mrp.toFixed(2)}</td>
                <td class="px-4 py-2 text-center">
                    <button class="text-on-surface-variant hover:text-primary transition-colors p-1 rounded-md" onclick="openEditProductModal(${p.id})">
                        <span class="material-symbols-outlined text-[18px]">edit</span>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

function renderReportsTable(sales) {
    const tbody = document.getElementById('reports-table-body');
    tbody.innerHTML = sales.map(s => {
        const date = new Date(s.sale_date);
        return `
            <tr class="data-grid-row border-b border-outline-variant hover:bg-surface-container-low transition-colors">
                <td class="px-4 py-2 font-data-sm">${s.invoice_number}</td>
                <td class="px-4 py-2">${date.toLocaleDateString('en-IN')} ${date.toLocaleTimeString('en-IN', {hour:'2-digit', minute:'2-digit'})}</td>
                <td class="px-4 py-2">${s.customer_name || 'Walk-in'}</td>
                <td class="px-4 py-2 text-right font-data-sm">${s.items || 0}</td>
                <td class="px-4 py-2 text-right font-semibold">₹${s.total_amount.toFixed(2)}</td>
                <td class="px-4 py-2">
                    <div class="flex justify-center gap-2">
                        <button class="p-1 hover:text-primary transition-colors" title="View Details" onclick="viewSale(${s.id})">
                            <span class="material-symbols-outlined text-[20px]">visibility</span>
                        </button>
                        <button class="p-1 hover:text-primary transition-colors" title="Reprint Bill" onclick="printSale(${s.id})">
                            <span class="material-symbols-outlined text-[20px]">print</span>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

function setupEventListeners() {
    // Navigation
    document.querySelectorAll('[data-view]').forEach(el => {
        el.addEventListener('click', () => switchView(el.dataset.view));
    });

    // Dropdown menus
    document.getElementById('settings-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        document.getElementById('settings-menu').classList.toggle('hidden');
        document.getElementById('account-menu').classList.add('hidden');
    });
    document.getElementById('account-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        document.getElementById('account-menu').classList.toggle('hidden');
        document.getElementById('settings-menu').classList.add('hidden');
    });
    window.addEventListener('click', () => {
        document.getElementById('settings-menu').classList.add('hidden');
        document.getElementById('account-menu').classList.add('hidden');
    });

    // Billing
    document.getElementById('sku-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') addToCart();
    });
    document.getElementById('void-btn').addEventListener('click', voidCart);
    document.getElementById('checkout-btn').addEventListener('click', checkout);
    document.getElementById('received-input').addEventListener('input', updateBalance);

    // Inventory
    document.getElementById('add-product-btn').addEventListener('click', openAddProductModal);
    document.getElementById('product-modal-close').addEventListener('click', closeProductModal);
    document.getElementById('product-modal-backdrop').addEventListener('click', closeProductModal);
    document.getElementById('product-modal-cancel').addEventListener('click', closeProductModal);
    document.getElementById('product-modal-save').addEventListener('click', saveProduct);

    // Hotkeys
    document.addEventListener('keydown', handleHotkeys);
}

function switchView(viewName) {
    currentView = viewName;
    document.querySelectorAll('[data-view]').forEach(el => {
        el.classList.toggle('nav-active', el.dataset.view === viewName);
    });
    document.querySelectorAll('main').forEach(el => {
        el.classList.toggle('hidden', el.id !== `view-${viewName}`);
    });
    if (viewName === 'inventory') renderInventoryTable();
    if (viewName === 'reports') loadSales();
}

function addToCart() {
    const skuInput = document.getElementById('sku-input');
    const qtyInput = document.getElementById('qty-input');
    const sku = skuInput.value.trim();
    const qty = parseInt(qtyInput.value) || 1;

    const product = products.find(p => p.sku === sku);
    if (!product) {
        alert('Product not found!');
        return;
    }

    const existing = cartItems.find(ci => ci.product_id === product.id);
    const currentCartQty = existing ? existing.quantity : 0;
    const totalQtyAfterAdd = currentCartQty + qty;

    if (totalQtyAfterAdd > product.stock_quantity) {
        alert(`Not enough stock for ${product.name}! Only ${product.stock_quantity} left in stock!`);
        return;
    }

    if (existing) {
        existing.quantity += qty;
    } else {
        cartItems.push({
            product_id: product.id,
            product_name: product.name,
            price: product.price,
            mrp: product.mrp,
            quantity: qty
        });
    }

    renderCart();
    skuInput.value = '';
    qtyInput.value = 1;
    skuInput.focus();
}

function renderCart() {
    const tbody = document.getElementById('bill-table-body');
    let sno = 1;
    tbody.innerHTML = cartItems.map(item => {
        const product = products.find(p => p.id === item.product_id);
        const stock = product ? product.stock_quantity : 0;
        const total = item.quantity * item.price;
        let stockClass = '';
        if (stock <30) stockClass='text-error';
        else if (stock <60) stockClass='text-yellow-600';
        return `
            <tr class="zebra-row">
                <td class="p-padding-cell font-data-md">${sno++}</td>
                <td class="p-padding-cell font-body-md text-on-surface">${item.product_name}</td>
                <td class="p-padding-cell text-center font-data-md ${stockClass}">${stock}</td>
                <td class="p-padding-cell font-data-md text-right text-on-surface-variant">
                    ₹${item.price.toFixed(2)} <span class="line-through">/₹${item.mrp.toFixed(2)}</span>
                </td>
                <td class="p-padding-cell text-right">
                    <input type="number" class="w-20 bg-transparent border border-outline-variant rounded p-1 text-center text-primary font-bold" value="${item.quantity}" min="1" onchange="updateCartItemQty(${item.product_id}, this.value)" />
                </td>
                <td class="p-padding-cell text-right font-semibold text-data-lg">₹${total.toFixed(2)}</td>
                <td class="p-padding-cell text-center">
                    <button class="text-error hover:text-error/80" onclick="removeFromCart(${item.product_id})">
                        <span class="material-symbols-outlined text-[20px]">delete</span>
                    </button>
                </td>
            </tr>
        `;
    }).join('');

    const totalItems = cartItems.reduce((sum, i) => sum + i.quantity, 0);
    const subtotal = cartItems.reduce((sum, i) => sum + (i.price * i.quantity), 0);
    document.getElementById('subtotal-display').textContent = subtotal.toFixed(2);
    document.getElementById('grand-total-val').textContent = subtotal.toFixed(2);
    document.getElementById('units-display').textContent = `Items: ${totalItems} Units`;
    updateBalance();
}

function updateCartItemQty(productId, qty) {
    const item = cartItems.find(i => i.product_id === productId);
    const product = products.find(p => p.id === productId);
    const newQty = parseInt(qty) || 1;
    if (item && product) {
        if (newQty > product.stock_quantity) {
            alert(`Not enough stock for ${product.name}! Only ${product.stock_quantity} left in stock!`);
            renderCart(); // reset to previous value
            return;
        }
        item.quantity = newQty;
        if (item.quantity <=0) removeFromCart(productId);
        else renderCart();
    }
}

function removeFromCart(productId) {
    cartItems = cartItems.filter(i => i.product_id !== productId);
    renderCart();
}

function voidCart() {
    if (confirm('Are you sure you want to void this bill?')) {
        cartItems = [];
        renderCart();
        document.getElementById('received-input').value = '';
    }
}

function updateBalance() {
    const received = parseFloat(document.getElementById('received-input').value) || 0;
    const subtotal = cartItems.reduce((sum, i) => sum + (i.price * i.quantity), 0);
    const balance = received - subtotal;
    document.getElementById('balance-val').textContent = balance.toFixed(2);
}

async function checkout() {
    if (cartItems.length === 0) {
        alert('Cart is empty!');
        return;
    }

    const customerName = document.getElementById('customer-name').value;
    const customerMobile = document.getElementById('customer-mobile').value;
    const received = parseFloat(document.getElementById('received-input').value) || 0;
    const totalAmount = cartItems.reduce((sum, i) => sum + (i.price * i.quantity), 0);

    const saleData = {
        customer_name: customerName,
        customer_mobile: customerMobile,
        total_amount: totalAmount,
        discount: 0,
        amount_paid: received,
        balance: Math.max(0, received - totalAmount),
        payment_method: received >= totalAmount ? 'Cash' : 'Partial',
        items: cartItems.map(i => ({
            ...i,
            total: i.price * i.quantity
        }))
    };

    try {
        const res = await fetch(`${API_BASE}/sales`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(saleData)
        });

        if (res.ok) {
            alert('Sale completed successfully!');
            cartItems = [];
            renderCart();
            document.getElementById('customer-name').value = '';
            document.getElementById('customer-mobile').value = '';
            document.getElementById('received-input').value = '';
            await loadProducts();
            await loadStats();
        } else {
            const errorData = await res.json();
            alert(`Failed to complete sale: ${errorData.error || 'Unknown error'}`);
        }
    } catch (err) {
        console.error(err);
        alert(`An error occurred: ${err.message}`);
    }
}

function openAddProductModal() {
    editingProductId = null;
    document.getElementById('product-modal-title').textContent = 'Add Product';
    document.getElementById('product-sku').value = '';
    document.getElementById('product-name').value = '';
    document.getElementById('product-category').value = 'Sparklers';
    document.getElementById('product-stock').value = 0;
    document.getElementById('product-cost-price').value = 0;
    document.getElementById('product-price').value = 0;
    document.getElementById('product-mrp').value = 0;
    document.getElementById('product-modal').classList.remove('hidden');
}

function openEditProductModal(id) {
    const product = products.find(p => p.id === id);
    if (!product) return;
    editingProductId = id;
    document.getElementById('product-modal-title').textContent = 'Edit Product';
    document.getElementById('product-sku').value = product.sku;
    document.getElementById('product-name').value = product.name;
    document.getElementById('product-category').value = product.category || 'Sparklers';
    document.getElementById('product-stock').value = product.stock_quantity;
    document.getElementById('product-cost-price').value = product.cost_price;
    document.getElementById('product-price').value = product.price;
    document.getElementById('product-mrp').value = product.mrp;
    document.getElementById('product-modal').classList.remove('hidden');
}

function closeProductModal() {
    document.getElementById('product-modal').classList.add('hidden');
}

async function saveProduct() {
    const sku = document.getElementById('product-sku').value.trim();
    const name = document.getElementById('product-name').value.trim();
    const category = document.getElementById('product-category').value;
    const stock = parseInt(document.getElementById('product-stock').value) || 0;
    const costPrice = parseFloat(document.getElementById('product-cost-price').value) || 0;
    const price = parseFloat(document.getElementById('product-price').value) || 0;
    const mrp = parseFloat(document.getElementById('product-mrp').value) || 0;

    if (!sku || !name) {
        alert('Please fill SKU and product name!');
        return;
    }

    const data = { sku, name, category, stock_quantity: stock, cost_price: costPrice, price, mrp };

    try {
        let res;
        if (editingProductId) {
            res = await fetch(`${API_BASE}/products/${editingProductId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
        } else {
            res = await fetch(`${API_BASE}/products`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
        }

        if (res.ok) {
            alert('Product saved successfully!');
            closeProductModal();
            await loadProducts();
            await loadStats();
        } else {
            const errorData = await res.json();
            alert(`Failed to save product: ${errorData.error || 'Unknown error'}`);
        }
    } catch (err) {
        console.error(err);
        alert(`An error occurred: ${err.message}`);
    }
}

async function checkout() {
    if (cartItems.length === 0) {
        alert('Cart is empty!');
        return;
    }

    const customerName = document.getElementById('customer-name').value;
    const customerMobile = document.getElementById('customer-mobile').value;
    const received = parseFloat(document.getElementById('received-input').value) || 0;
    const totalAmount = cartItems.reduce((sum, i) => sum + (i.price * i.quantity), 0);

    const saleData = {
        customer_name: customerName,
        customer_mobile: customerMobile,
        total_amount: totalAmount,
        discount: 0,
        amount_paid: received,
        balance: Math.max(0, received - totalAmount),
        payment_method: received >= totalAmount ? 'Cash' : 'Partial',
        items: cartItems.map(i => ({
            ...i,
            total: i.price * i.quantity
        }))
    };

    try {
        const res = await fetch(`${API_BASE}/sales`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(saleData)
        });

        if (res.ok) {
            alert('Sale completed successfully!');
            cartItems = [];
            renderCart();
            document.getElementById('customer-name').value = '';
            document.getElementById('customer-mobile').value = '';
            document.getElementById('received-input').value = '';
            await loadProducts();
            await loadStats();
        } else {
            const errorData = await res.json();
            alert(`Failed to complete sale: ${errorData.error || 'Unknown error'}`);
        }
    } catch (err) {
        console.error(err);
        alert(`An error occurred: ${err.message}`);
    }
}

function viewSale(id) {
    alert(`Viewing sale #${id}`);
}

function printSale(id) {
    alert(`Printing sale #${id}`);
}

function handleHotkeys(e) {
    if (e.key === 'F1') { e.preventDefault(); document.getElementById('sku-input').focus(); }
    if (e.key === 'F2') { e.preventDefault(); document.getElementById('qty-input').focus(); }
    if (e.key === 'F3') { e.preventDefault(); document.getElementById('customer-name').focus(); }
    if (e.key === 'F8') { e.preventDefault(); voidCart(); }
    if (e.key === 'F12') { e.preventDefault(); checkout(); }
}

init();
