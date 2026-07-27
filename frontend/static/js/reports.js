let allSales = [];
let activePeriod = 'today';
let currentViewingSaleId = null;

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

function filterReports() {
    if (!allSales || allSales.length === 0) {
        updateReportStats(0, 0, 0);
        renderReportsTable([]);
        return;
    }

    const today = new Date();
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
        startDate = startVal ? getStartOfDay(new Date(startVal)) : new Date(0);
        endDate = endVal ? getEndOfDay(new Date(endVal)) : getEndOfDay(today);
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
    
    document.querySelectorAll('#period-btn-group [data-period]').forEach(btn => {
        if (btn.dataset.period === period) {
            btn.className = "px-3 py-1 text-sm font-bold bg-primary text-white rounded shadow-sm";
        } else {
            btn.className = "px-3 py-1 text-sm font-bold text-on-surface-variant hover:bg-surface-container-low rounded";
        }
    });

    const customContainer = document.getElementById('custom-date-container');
    if (period === 'custom') {
        customContainer.classList.remove('hidden');
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
