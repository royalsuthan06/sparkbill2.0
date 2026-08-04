const SparkBill = {
    products: [],
    allSales: [],
    currentView: 'billing',
    cartItems: [],
    cartNavIndex: -1,
    editingProductId: null,
    activePeriod: 'today',
    currentViewingSaleId: null
};

async function init() {
    updateDate();
    await loadProducts();
    await loadStats();
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
        if (!res.ok) throw new Error('Failed to fetch products');
        SparkBill.products = await res.json();
        populateCategoryFilter();
        renderInventoryTable();
    } catch (err) {
        console.error('Failed to load products:', err);
    }
}

async function loadStats() {
    try {
        const res = await fetch(`${API_BASE}/stats`);
        if (!res.ok) throw new Error('Failed to fetch stats');
        const stats = await res.json();
        document.getElementById('stat-total-skus').textContent = stats.total_skus;
        document.getElementById('stat-categories').textContent = [...new Set(SparkBill.products.map(p => p.category))].length;
    } catch (err) {
        console.error('Failed to load stats:', err);
    }
}

async function loadSales() {
    try {
        const all = [];
        let page = 1;
        let totalPages = 1;
        do {
            const res = await fetch(`${API_BASE}/sales?page=${page}&per_page=500`);
            if (!res.ok) throw new Error('Failed to fetch sales');
            const data = await res.json();
            all.push(...(data.sales || data));
            totalPages = data.pages || 1;
            page++;
        } while (page <= totalPages);
        SparkBill.allSales = all;
        filterReports();
    } catch (err) {
        console.error('Failed to load sales:', err);
    }
}

function switchView(viewName) {
    SparkBill.currentView = viewName;
    document.querySelectorAll('[data-view]').forEach(el => {
        el.classList.toggle('nav-active', el.dataset.view === viewName);
    });
    document.querySelectorAll('main').forEach(el => {
        el.classList.toggle('hidden', el.id !== `view-${viewName}`);
    });
    if (viewName === 'inventory') renderInventoryTable();
    if (viewName === 'reports') loadSales();
}

function setupEventListeners() {
    document.querySelectorAll('[data-view]').forEach(el => {
        el.addEventListener('click', () => switchView(el.dataset.view));
    });

    const skuInput = document.getElementById('sku-input');
    const skuDropdown = document.getElementById('sku-dropdown');
    let highlightedIndex = -1;
    let skuDropdownMouseDown = false;

    skuInput.addEventListener('input', (e) => {
        const query = e.target.value.trim().toLowerCase();
        const preview = document.getElementById('product-preview');

        if (!query) {
            preview.textContent = '-';
            hideSkuDropdown();
            return;
        }

        const matched = SparkBill.products.filter(p =>
            p.sku.toLowerCase().includes(query) || p.name.toLowerCase().includes(query)
        );

        if (matched.length > 0) {
            showSkuDropdown(matched);
        } else {
            hideSkuDropdown();
        }

        const product = findProductBySku(e.target.value.trim()) || (matched.length === 1 ? matched[0] : null);
        preview.textContent = product ? product.name : (matched.length > 0 ? `${matched.length} product(s) found` : 'Not found');
    });

    skuInput.addEventListener('keydown', (e) => {
        const items = skuDropdown.querySelectorAll('.sku-dropdown-item');
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            highlightedIndex = Math.min(highlightedIndex + 1, items.length - 1);
            updateHighlight(items);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            highlightedIndex = Math.max(highlightedIndex - 1, -1);
            updateHighlight(items);
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (highlightedIndex >= 0 && items[highlightedIndex]) {
                skuInput.value = items[highlightedIndex].dataset.sku;
                hideSkuDropdown();
                addToCart();
            } else if (items.length > 0) {
                skuInput.value = items[0].dataset.sku;
                hideSkuDropdown();
                addToCart();
            } else {
                hideSkuDropdown();
                addToCart();
            }
        } else if (e.key === 'Escape') {
            hideSkuDropdown();
        }
    });

    skuInput.addEventListener('mousedown', () => {
        skuDropdownMouseDown = false;
    });

    skuInput.addEventListener('blur', () => {
        if (!skuDropdownMouseDown) {
            hideSkuDropdown();
        }
        skuDropdownMouseDown = false;
    });

    function showSkuDropdown(matches) {
        highlightedIndex = -1;
        skuDropdown.innerHTML = matches.slice(0, 10).map(p =>
            `<div class="sku-dropdown-item px-3 py-2 cursor-pointer hover:bg-primary/10 flex justify-between items-center" data-sku="${escapeHtml(p.sku)}">
                <span class="font-data-md text-primary font-semibold text-[13px]">${escapeHtml(p.sku)}</span>
                <span class="text-on-surface font-semibold text-[13px] mx-3 flex-1 truncate">${escapeHtml(p.name)}</span>
                <span class="font-data-md text-on-surface-variant text-[12px]">₹${p.price.toFixed(2)}</span>
            </div>`
        ).join('');

        skuDropdown.querySelectorAll('.sku-dropdown-item').forEach(item => {
            item.addEventListener('mousedown', () => {
                skuDropdownMouseDown = true;
                skuInput.value = item.dataset.sku;
                hideSkuDropdown();
                const product = findProductBySku(item.dataset.sku);
                document.getElementById('product-preview').textContent = product ? product.name : '-';
                document.getElementById('qty-input').focus();
            });
        });

        skuDropdown.classList.remove('hidden');
    }

    function hideSkuDropdown() {
        skuDropdown.classList.add('hidden');
        skuDropdown.innerHTML = '';
        highlightedIndex = -1;
    }

    function updateHighlight(items) {
        items.forEach((item, i) => {
            item.classList.toggle('bg-primary/10', i === highlightedIndex);
            item.classList.toggle('bg-transparent', i !== highlightedIndex);
        });
    }

    document.getElementById('qty-input').addEventListener('keydown', (e) => {
        if (e.key === 'Enter') addToCart();
    });
    document.getElementById('void-btn').addEventListener('click', voidCart);
    document.getElementById('checkout-btn').addEventListener('click', checkout);

    document.getElementById('add-product-btn').addEventListener('click', openAddProductModal);
    document.getElementById('product-modal-close').addEventListener('click', closeProductModal);
    document.getElementById('product-modal-backdrop').addEventListener('click', closeProductModal);
    document.getElementById('product-modal-cancel').addEventListener('click', closeProductModal);
    document.getElementById('product-modal-save').addEventListener('click', saveProduct);

    document.getElementById('filter-category').addEventListener('change', renderInventoryTable);
    document.getElementById('filter-price').addEventListener('change', renderInventoryTable);
    document.getElementById('reset-filters-btn').addEventListener('click', resetFilters);

    document.querySelectorAll('#period-btn-group [data-period]').forEach(btn => {
        btn.addEventListener('click', () => handlePeriodChange(btn.dataset.period));
    });
    document.getElementById('custom-start-date').addEventListener('change', filterReports);
    document.getElementById('custom-end-date').addEventListener('change', filterReports);

    document.getElementById('sale-modal-close').addEventListener('click', closeSaleModal);
    document.getElementById('sale-modal-backdrop').addEventListener('click', closeSaleModal);
    document.getElementById('sale-modal-cancel').addEventListener('click', closeSaleModal);
    document.getElementById('sale-modal-print').addEventListener('click', () => printCurrentSale());

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

    document.addEventListener('keydown', handleHotkeys);
}

function handleHotkeys(e) {
    if (e.key === 'F1') { e.preventDefault(); document.getElementById('sku-input').focus(); }
    if (e.key === 'F2') { e.preventDefault(); document.getElementById('qty-input').focus(); }
    if (e.key === 'F3') { e.preventDefault(); document.getElementById('customer-name').focus(); }
    if (e.key === 'F8') { e.preventDefault(); voidCart(); }
    if (e.key === 'F12') { e.preventDefault(); checkout(); }

    if (SparkBill.currentView !== 'billing') return;
    const active = document.activeElement;
    const inInput = active && (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA');

    if (e.key === 'Escape') {
        e.preventDefault();
        if (inInput) active.blur();
        if (SparkBill.cartNavIndex >= 0) {
            SparkBill.cartNavIndex = -1;
            renderCart();
        }
        return;
    }

    if (e.key === 'Delete' && !inInput && SparkBill.cartItems.length > 0) {
        e.preventDefault();
        if (SparkBill.cartNavIndex === -1) {
            SparkBill.cartNavIndex = 0;
        } else {
            SparkBill.cartNavIndex = Math.min(SparkBill.cartNavIndex, SparkBill.cartItems.length - 1);
        }
        renderCart();
        return;
    }

    if (SparkBill.cartNavIndex >= 0) {
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            SparkBill.cartNavIndex = Math.min(SparkBill.cartNavIndex + 1, SparkBill.cartItems.length - 1);
            renderCart();
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            SparkBill.cartNavIndex = Math.max(SparkBill.cartNavIndex - 1, 0);
            renderCart();
        } else if (e.key === 'Enter') {
            e.preventDefault();
            removeFromCartByIndex(SparkBill.cartNavIndex);
        }
    }
}

init();
