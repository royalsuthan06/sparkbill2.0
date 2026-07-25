const API_BASE = '/api';

function askConfirmation(message) {
    return new Promise((resolve) => {
        const modal = document.getElementById('custom-confirm-modal');
        const titleEl = document.getElementById('custom-confirm-title');
        const msgEl = document.getElementById('custom-confirm-message');
        const okBtn = document.getElementById('custom-confirm-ok');
        const cancelBtn = document.getElementById('custom-confirm-cancel');

        if (!modal || !titleEl || !msgEl || !okBtn || !cancelBtn) {
            resolve(confirm(message));
            return;
        }

        titleEl.textContent = "ArunCrackers";
        msgEl.textContent = message;

        modal.classList.remove('hidden');
        modal.offsetHeight; // Force reflow
        modal.classList.remove('opacity-0');
        modal.querySelector('.transform').classList.remove('scale-95');
        modal.querySelector('.transform').classList.add('scale-100');

        function cleanUp(result) {
            modal.classList.add('opacity-0');
            modal.querySelector('.transform').classList.remove('scale-100');
            modal.querySelector('.transform').classList.add('scale-95');
            setTimeout(() => {
                modal.classList.add('hidden');
            }, 200);

            okBtn.removeEventListener('click', onOk);
            cancelBtn.removeEventListener('click', onCancel);

            resolve(result);
        }

        function onOk() { cleanUp(true); }
        function onCancel() { cleanUp(false); }

        okBtn.addEventListener('click', onOk);
        cancelBtn.addEventListener('click', onCancel);
    });
}


let products = [];
let cartItems = [];
let currentView = 'billing';
let editingProductId = null;
let allSales = [];
let activePeriod = 'today';

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
        populateCategoryFilter();
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
        document.getElementById('stat-categories').textContent = [...new Set(products.map(p => p.category))].length;
    } catch (err) {
        console.error('Failed to load stats:', err);
    }
}

async function loadSales() {
    try {
        const res = await fetch(`${API_BASE}/sales`);
        allSales = await res.json();
        filterReports();
    } catch (err) {
        console.error('Failed to load sales:', err);
    }
}

function populateCategoryFilter() {
    const filterCategory = document.getElementById('filter-category');
    if (!filterCategory) return;

    const currentValue = filterCategory.value || 'all';

    // Get unique categories and filter out empty values
    const categories = [...new Set(products.map(p => p.category).filter(Boolean))].sort();

    let html = '<option value="all">All Categories</option>';
    categories.forEach(cat => {
        html += `<option value="${cat}">${cat}</option>`;
    });

    filterCategory.innerHTML = html;

    // Restore previous selection if it exists in the new list, else fall back to 'all'
    if (categories.includes(currentValue) || currentValue === 'all') {
        filterCategory.value = currentValue;
    } else {
        filterCategory.value = 'all';
    }
}

function renderInventoryTable() {
    const tbody = document.getElementById('inventory-table-body');
    if (!tbody) return;

    const categoryFilter = document.getElementById('filter-category')?.value || 'all';
    const priceFilter = document.getElementById('filter-price')?.value || 'all';

    let filtered = products;

    if (categoryFilter !== 'all') {
        filtered = filtered.filter(p => p.category === categoryFilter);
    }

    if (priceFilter !== 'all') {
        if (priceFilter === 'under-100') {
            filtered = filtered.filter(p => p.price < 100);
        } else if (priceFilter === '100-500') {
            filtered = filtered.filter(p => p.price >= 100 && p.price <= 500);
        } else if (priceFilter === '500-1000') {
            filtered = filtered.filter(p => p.price > 500 && p.price <= 1000);
        } else if (priceFilter === 'over-1000') {
            filtered = filtered.filter(p => p.price > 1000);
        }
    }



    const countDisplay = document.getElementById('inventory-count-display');
    if (countDisplay) {
        if (filtered.length === products.length) {
            countDisplay.textContent = `(Showing all ${products.length} products)`;
        } else {
            countDisplay.textContent = `(Showing ${filtered.length} of ${products.length} products)`;
        }
    }

    tbody.innerHTML = filtered.map(p => {
        return `
            <tr class="zebra-row hover:bg-surface-container transition-colors cursor-default">
                <td class="px-4 py-2 font-mono text-primary font-semibold text-[13px]">${p.sku}</td>
                <td class="px-4 py-2 text-on-surface font-semibold outline-none">${p.name}</td>
                <td class="px-4 py-2 text-on-surface-variant outline-none">${p.category || '-'}</td>
                <td class="px-4 py-2 font-mono text-right text-on-surface outline-none">₹${p.price.toFixed(2)}</td>
                <td class="px-4 py-2 text-center flex justify-center gap-2">
                    <button class="text-on-surface-variant hover:text-primary transition-colors p-1 rounded-md" onclick="openEditProductModal(${p.id})">
                        <span class="material-symbols-outlined text-[18px]">edit</span>
                    </button>
                    <button class="text-on-surface-variant hover:text-error transition-colors p-1 rounded-md" onclick="deleteProduct(${p.id}, '${p.name.replace(/'/g, "\\'")}')">
                        <span class="material-symbols-outlined text-[18px]">delete</span>
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

    // Dropdown menus (safely check existence)
    const settingsBtn = document.getElementById('settings-btn');
    const settingsMenu = document.getElementById('settings-menu');
    const accountBtn = document.getElementById('account-btn');
    const accountMenu = document.getElementById('account-menu');

    if (settingsBtn && settingsMenu) {
        settingsBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            settingsMenu.classList.toggle('hidden');
            if (accountMenu) accountMenu.classList.add('hidden');
        });
    }
    if (accountBtn && accountMenu) {
        accountBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            accountMenu.classList.toggle('hidden');
            if (settingsMenu) settingsMenu.classList.add('hidden');
        });
    }
    window.addEventListener('click', () => {
        if (settingsMenu) settingsMenu.classList.add('hidden');
        if (accountMenu) accountMenu.classList.add('hidden');
    });

    // Billing
    document.getElementById('sku-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') addToCart();
    });
    document.getElementById('sku-input').addEventListener('input', (e) => {
        const sku = e.target.value.trim();
        const preview = document.getElementById('product-preview');
        if (!sku) {
            preview.textContent = '-';
            return;
        }
        const product = products.find(p => p.sku === sku);
        preview.textContent = product ? product.name : 'Not found';
    });
    document.getElementById('qty-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') addToCart();
    });
    document.getElementById('void-btn').addEventListener('click', voidCart);
    document.getElementById('checkout-btn').addEventListener('click', checkout);

    // Inventory
    document.getElementById('add-product-btn').addEventListener('click', openAddProductModal);
    document.getElementById('product-modal-close').addEventListener('click', closeProductModal);
    document.getElementById('product-modal-backdrop').addEventListener('click', closeProductModal);
    document.getElementById('product-modal-cancel').addEventListener('click', closeProductModal);
    document.getElementById('product-modal-save').addEventListener('click', saveProduct);

    // Filters
    document.getElementById('filter-category').addEventListener('change', renderInventoryTable);
    document.getElementById('filter-price').addEventListener('change', renderInventoryTable);
    document.getElementById('reset-filters-btn').addEventListener('click', resetFilters);

    // Reports Filters
    document.querySelectorAll('#period-btn-group [data-period]').forEach(btn => {
        btn.addEventListener('click', () => handlePeriodChange(btn.dataset.period));
    });
    document.getElementById('custom-start-date').addEventListener('change', filterReports);
    document.getElementById('custom-end-date').addEventListener('change', filterReports);

    // Sale Modal
    document.getElementById('sale-modal-close').addEventListener('click', closeSaleModal);
    document.getElementById('sale-modal-backdrop').addEventListener('click', closeSaleModal);
    document.getElementById('sale-modal-cancel').addEventListener('click', closeSaleModal);
    document.getElementById('sale-modal-print').addEventListener('click', () => printCurrentSale());

    // PDF Modal
    document.getElementById('pdf-modal-close').addEventListener('click', closePdfModal);
    document.getElementById('pdf-modal-backdrop').addEventListener('click', closePdfModal);
    document.getElementById('pdf-modal-cancel').addEventListener('click', closePdfModal);
    document.getElementById('pdf-modal-print-btn').addEventListener('click', () => {
        const iframe = document.getElementById('pdf-iframe');
        if (iframe && iframe.contentWindow) {
            iframe.contentWindow.focus();
            iframe.contentWindow.print();
        }
    });

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

    if (qty <= 0) {
        showToast('Quantity must be greater than 0!', 'error');
        return;
    }

    const product = products.find(p => p.sku === sku);
    if (!product) {
        showToast('Product not found!', 'error');
        return;
    }

    const existing = cartItems.find(ci => ci.product_id === product.id);

    if (existing) {
        existing.quantity += qty;
    } else {
        cartItems.push({
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
    skuInput.focus();
}

function renderCart() {
    const tbody = document.getElementById('bill-table-body');
    let sno = 1;
    tbody.innerHTML = cartItems.map(item => {
        const total = item.quantity * item.price;
        return `
            <tr class="zebra-row">
                <td class="p-padding-cell font-data-md">${sno++}</td>
                <td class="p-padding-cell font-body-md text-on-surface">${item.product_name}</td>
                <td class="p-padding-cell font-data-md text-right text-on-surface-variant">
                    ₹${item.price.toFixed(2)}
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
}

function updateCartItemQty(productId, qty) {
    const item = cartItems.find(i => i.product_id === productId);
    const newQty = parseInt(qty) || 1;
    if (item) {
        item.quantity = newQty;
        if (item.quantity <=0) removeFromCart(productId);
        else renderCart();
    }
}

function removeFromCart(productId) {
    cartItems = cartItems.filter(i => i.product_id !== productId);
    renderCart();
}

async function voidCart() {
    if (await askConfirmation('Are you sure you want to void this bill?')) {
        cartItems = [];
        renderCart();
        document.getElementById('product-preview').textContent = '-';
    }
}

async function checkout() {
    if (cartItems.length === 0) {
        showToast('Cart is empty!', 'error');
        return;
    }

    const customerName = document.getElementById('customer-name').value;
    const customerMobile = document.getElementById('customer-mobile').value;
    const totalAmount = cartItems.reduce((sum, i) => sum + (i.price * i.quantity), 0);

    const saleData = {
        customer_name: customerName,
        customer_mobile: customerMobile,
        total_amount: totalAmount,
        discount: 0,
        amount_paid: totalAmount,
        balance: 0,
        payment_method: 'Cash',
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
            const result = await res.json();
            showToast('Sale completed successfully!', 'success');
            
            // Auto-open print preview PDF in modal
            if (result && result.id) {
                showPdfModal(result.id);
            }
            
            cartItems = [];
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
        alert(`An error occurred: ${err.message}`);
    }
}

function openAddProductModal() {
    editingProductId = null;
    document.getElementById('product-modal-title').textContent = 'Add Product';
    document.getElementById('product-sku').value = '';
    document.getElementById('product-name').value = '';
    document.getElementById('product-category').value = 'One Sound Crackers';
    document.getElementById('product-price').value = 0;
    document.getElementById('product-modal').classList.remove('hidden');
}

function openEditProductModal(id) {
    const product = products.find(p => p.id === id);
    if (!product) return;
    editingProductId = id;
    document.getElementById('product-modal-title').textContent = 'Edit Product';
    document.getElementById('product-sku').value = product.sku;
    document.getElementById('product-name').value = product.name;
    document.getElementById('product-category').value = product.category || 'One Sound Crackers';
    document.getElementById('product-price').value = product.price;
    document.getElementById('product-modal').classList.remove('hidden');
}

function closeProductModal() {
    document.getElementById('product-modal').classList.add('hidden');
}

function resetFilters() {
    document.getElementById('filter-category').value = 'all';
    document.getElementById('filter-price').value = 'all';
    renderInventoryTable();
}

function filterReports() {
    if (!allSales || allSales.length === 0) {
        updateReportStats(0, 0, 0);
        renderReportsTable([]);
        return;
    }

    const today = new Date();
    
    // Helper to get start/end of a local date
    const getStartOfDay = (date) => new Date(date.getFullYear(), date.getMonth(), date.getDate(), 0, 0, 0, 0);
    const getEndOfDay = (date) => new Date(date.getFullYear(), date.getMonth(), date.getDate(), 23, 59, 59, 999);

    let startDate, endDate;

    if (activePeriod === 'today') {
        startDate = getStartOfDay(today);
        endDate = getEndOfDay(today);
    } else if (activePeriod === 'yesterday') {
        const yesterday = new Date(today);
        yesterday.setDate(today.getDate() - 1);
        startDate = getStartOfDay(yesterday);
        endDate = getEndOfDay(yesterday);
    } else if (activePeriod === '7d') {
        const sevenDaysAgo = new Date(today);
        sevenDaysAgo.setDate(today.getDate() - 6);
        startDate = getStartOfDay(sevenDaysAgo);
        endDate = getEndOfDay(today);
    } else if (activePeriod === 'custom') {
        const startVal = document.getElementById('custom-start-date').value;
        const endVal = document.getElementById('custom-end-date').value;

        if (startVal) {
            startDate = getStartOfDay(new Date(startVal));
        } else {
            startDate = new Date(0); // far past
        }

        if (endVal) {
            endDate = getEndOfDay(new Date(endVal));
        } else {
            endDate = getEndOfDay(today);
        }
    }

    const filtered = allSales.filter(sale => {
        const saleDate = new Date(sale.sale_date);
        return saleDate >= startDate && saleDate <= endDate;
    });

    const totalSales = filtered.reduce((sum, s) => sum + (s.total_amount || 0), 0);
    const totalCount = filtered.length;
    const avgBill = totalCount > 0 ? totalSales / totalCount : 0;

    updateReportStats(totalSales, totalCount, avgBill);
    renderReportsTable(filtered);
}

function updateReportStats(totalSales, totalCount, avgBill) {
    document.getElementById('report-today-sales').textContent = `₹${totalSales.toFixed(2)}`;
    document.getElementById('report-today-count').textContent = totalCount;
    document.getElementById('report-avg-bill').textContent = `₹${avgBill.toFixed(2)}`;
}

function handlePeriodChange(period) {
    activePeriod = period;
    
    // Toggle active styles on buttons
    document.querySelectorAll('#period-btn-group [data-period]').forEach(btn => {
        if (btn.dataset.period === period) {
            btn.className = "px-3 py-1 text-sm font-bold bg-primary text-white rounded shadow-sm";
        } else {
            btn.className = "px-3 py-1 text-sm font-bold text-on-surface-variant hover:bg-surface-container-low rounded";
        }
    });

    // Show/hide custom date range inputs
    const customContainer = document.getElementById('custom-date-container');
    if (period === 'custom') {
        customContainer.classList.remove('hidden');
        
        // Default start/end input fields if empty
        const startInput = document.getElementById('custom-start-date');
        const endInput = document.getElementById('custom-end-date');
        const todayStr = new Date().toISOString().split('T')[0];
        
        if (!startInput.value) startInput.value = todayStr;
        if (!endInput.value) endInput.value = todayStr;
    } else {
        customContainer.classList.add('hidden');
    }

    filterReports();
}

async function saveProduct() {
    const sku = document.getElementById('product-sku').value.trim();
    const name = document.getElementById('product-name').value.trim();
    const category = document.getElementById('product-category').value;
    const price = parseFloat(document.getElementById('product-price').value) || 0;

    if (!sku || !name) {
        showToast('Please fill SKU and product name!', 'error');
        return;
    }

    const data = { sku, name, category, stock_quantity: 0, price };

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
            showToast('Product saved successfully!', 'success');
            closeProductModal();
            await loadProducts();
            await loadStats();
        } else {
            const errorData = await res.json();
            showToast(`Failed to save product: ${errorData.error || 'Unknown error'}`, 'error');
        }
    } catch (err) {
        console.error(err);
        showToast(`An error occurred: ${err.message}`, 'error');
    }
}

let currentViewingSaleId = null;

function closeSaleModal() {
    document.getElementById('sale-modal').classList.add('hidden');
    currentViewingSaleId = null;
}

function closePdfModal() {
    document.getElementById('pdf-modal').classList.add('hidden');
    document.getElementById('pdf-iframe').src = '';
}

function showPdfModal(saleId) {
    const iframe = document.getElementById('pdf-iframe');
    iframe.src = `/api/sales/${saleId}/pdf_inline`;
    document.getElementById('pdf-modal').classList.remove('hidden');
}

async function viewSale(id) {
    try {
        const res = await fetch(`${API_BASE}/sales/${id}`);
        if (!res.ok) throw new Error('Failed to fetch sale');
        const sale = await res.json();
        currentViewingSaleId = id;

        const date = new Date(sale.sale_date);
        const body = document.getElementById('sale-modal-body');
        body.innerHTML = `
            <div class="space-y-4">
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <span class="text-[11px] font-bold uppercase text-on-surface-variant">Invoice Number</span>
                        <p class="font-data-md text-data-md text-on-surface">${sale.invoice_number}</p>
                    </div>
                    <div>
                        <span class="text-[11px] font-bold uppercase text-on-surface-variant">Date & Time</span>
                        <p class="font-data-md text-data-md text-on-surface">${date.toLocaleDateString('en-IN')} ${date.toLocaleTimeString('en-IN', {hour:'2-digit', minute:'2-digit'})}</p>
                    </div>
                    <div>
                        <span class="text-[11px] font-bold uppercase text-on-surface-variant">Customer</span>
                        <p class="font-data-md text-data-md text-on-surface">${sale.customer_name || 'Walk-in'}</p>
                    </div>
                    <div>
                        <span class="text-[11px] font-bold uppercase text-on-surface-variant">Payment Method</span>
                        <p class="font-data-md text-data-md text-on-surface">${sale.payment_method}</p>
                    </div>
                </div>
                <div class="border-t border-outline-variant pt-4">
                    <table class="w-full text-left">
                        <thead>
                            <tr class="border-b border-outline-variant">
                                <th class="pb-2 text-[11px] font-bold uppercase text-on-surface-variant">Item</th>
                                <th class="pb-2 text-[11px] font-bold uppercase text-on-surface-variant text-center">Qty</th>
                                <th class="pb-2 text-[11px] font-bold uppercase text-on-surface-variant text-right">Price</th>
                                <th class="pb-2 text-[11px] font-bold uppercase text-on-surface-variant text-right">Total</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${sale.items.map(item => `
                                <tr class="border-b border-outline-variant/50">
                                    <td class="py-2 font-body-md text-on-surface">${item.product_name}</td>
                                    <td class="py-2 font-data-md text-data-md text-center text-on-surface">${item.quantity}</td>
                                    <td class="py-2 font-data-md text-data-md text-right text-on-surface">₹${parseFloat(item.price).toFixed(2)}</td>
                                    <td class="py-2 font-data-md text-data-md text-right font-semibold text-on-surface">₹${parseFloat(item.total).toFixed(2)}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
                <div class="border-t border-outline-variant pt-4 space-y-2">
                    <div class="flex justify-between text-body-sm text-on-surface-variant">
                        <span>Total Amount</span>
                        <span class="font-semibold">₹${parseFloat(sale.total_amount).toFixed(2)}</span>
                    </div>
                    <div class="flex justify-between text-body-sm text-on-surface-variant">
                        <span>Amount Paid</span>
                        <span class="font-semibold">₹${parseFloat(sale.amount_paid).toFixed(2)}</span>
                    </div>
                    <div class="flex justify-between text-body-sm text-on-surface-variant">
                        <span>Balance</span>
                        <span class="font-semibold">₹${parseFloat(sale.balance).toFixed(2)}</span>
                    </div>
                </div>
            </div>
        `;
        document.getElementById('sale-modal').classList.remove('hidden');
    } catch (err) {
        console.error(err);
        alert('Failed to load sale details');
    }
}

function printSale(id) {
    showPdfModal(id);
}

function printCurrentSale() {
    if (!currentViewingSaleId) return;
    showPdfModal(currentViewingSaleId);
}

function handleHotkeys(e) {
    if (e.key === 'F1') { e.preventDefault(); document.getElementById('sku-input').focus(); }
    if (e.key === 'F2') { e.preventDefault(); document.getElementById('qty-input').focus(); }
    if (e.key === 'F3') { e.preventDefault(); document.getElementById('customer-name').focus(); }
    if (e.key === 'F8') { e.preventDefault(); voidCart(); }
    if (e.key === 'F12') { e.preventDefault(); checkout(); }
}

function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `flex items-center gap-4 bg-white border border-outline-variant px-6 py-4 shadow-2xl rounded-xl pointer-events-auto transform translate-y-[-20px] opacity-0 transition-all duration-300 ease-out border-l-4 min-w-[320px] md:min-w-[400px] ${
        type === 'success' ? 'border-l-emerald-500' : 'border-l-red-500'
    }`;

    const icon = type === 'success' ? 'check_circle' : 'error';
    const iconColor = type === 'success' ? 'text-emerald-500' : 'text-red-500';

    toast.innerHTML = `
        <span class="material-symbols-outlined text-[28px] ${iconColor}">${icon}</span>
        <div class="flex-1">
            <p class="text-base font-bold text-on-surface">${message}</p>
        </div>
        <button class="material-symbols-outlined text-[20px] text-on-surface-variant hover:text-on-surface ml-3" onclick="this.parentElement.remove()">close</button>
    `;

    container.appendChild(toast);

    // Trigger animation
    setTimeout(() => {
        toast.className = toast.className.replace('translate-y-[-20px] opacity-0', 'translate-y-0 opacity-100');
    }, 10);

    // Auto dismiss
    setTimeout(() => {
        if (toast.parentNode) {
            toast.className = toast.className.replace('translate-y-0 opacity-100', 'translate-y-[-20px] opacity-0');
            setTimeout(() => {
                if (toast.parentNode) toast.remove();
            }, 300);
        }
    }, 3500);
}
async function deleteProduct(id, name) {
    if (await askConfirmation(`Are you sure you want to delete the product "${name}"?`)) {
        try {
            const res = await fetch(`${API_BASE}/products/${id}`, {
                method: 'DELETE'
            });
            if (res.ok) {
                showToast('Product deleted successfully!', 'success');
                await loadProducts();
                await loadStats();
            } else {
                const errorData = await res.json();
                showToast(`Failed to delete product: ${errorData.error || 'Unknown error'}`, 'error');
            }
        } catch (err) {
            console.error(err);
            showToast(`An error occurred: ${err.message}`, 'error');
        }
    }
}

init();
