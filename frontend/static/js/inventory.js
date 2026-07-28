let editingProductId = null;

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

async function saveProduct() {
    const sku = document.getElementById('product-sku').value.trim();
    const name = document.getElementById('product-name').value.trim();
    const category = document.getElementById('product-category').value;
    const price = parseFloat(document.getElementById('product-price').value);

    if (!sku || !name) {
        showToast('Please fill SKU and product name!', 'error');
        return;
    }

    if (isNaN(price) || price < 0) {
        showToast('Please enter a valid price!', 'error');
        return;
    }

    const data = { sku, name, category, price };

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

function populateCategoryFilter() {
    const filterCategory = document.getElementById('filter-category');
    if (!filterCategory) return;

    const currentValue = filterCategory.value || 'all';
    const categories = [...new Set(products.map(p => p.category).filter(Boolean))].sort();

    let html = '<option value="all">All Categories</option>';
    categories.forEach(cat => {
        html += `<option value="${escapeHtml(cat)}">${escapeHtml(cat)}</option>`;
    });

    filterCategory.innerHTML = html;

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
                <td class="px-4 py-2 font-mono text-primary font-semibold text-[13px]">${escapeHtml(p.sku)}</td>
                <td class="px-4 py-2 text-on-surface font-semibold outline-none">${escapeHtml(p.name)}</td>
                <td class="px-4 py-2 text-on-surface-variant outline-none">${escapeHtml(p.category) || '-'}</td>
                <td class="px-4 py-2 font-mono text-right text-on-surface outline-none">₹${p.price.toFixed(2)}</td>
                <td class="px-4 py-2 text-center flex justify-center gap-2">
                    <button class="text-on-surface-variant hover:text-primary transition-colors p-1 rounded-md edit-product-btn" data-id="${p.id}">
                        <span class="material-symbols-outlined text-[18px]">edit</span>
                    </button>
                    <button class="text-on-surface-variant hover:text-error transition-colors p-1 rounded-md delete-product-btn" data-id="${p.id}" data-name="${escapeHtml(p.name)}">
                        <span class="material-symbols-outlined text-[18px]">delete</span>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

function resetFilters() {
    document.getElementById('filter-category').value = 'all';
    document.getElementById('filter-price').value = 'all';
    renderInventoryTable();
}

document.addEventListener('click', (e) => {
    const editBtn = e.target.closest('.edit-product-btn');
    if (editBtn) {
        openEditProductModal(parseInt(editBtn.dataset.id));
        return;
    }
    const deleteBtn = e.target.closest('.delete-product-btn');
    if (deleteBtn) {
        deleteProduct(parseInt(deleteBtn.dataset.id), deleteBtn.dataset.name);
    }
});
