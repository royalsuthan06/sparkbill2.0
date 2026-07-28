const API_BASE = '/api';

function escapeHtml(str) {
    if (str == null) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

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
        modal.offsetHeight;
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

function findProductBySku(sku) {
    return products.find(p => p.sku === sku)
        || products.find(p => p.sku === sku.padStart(3, '0'))
        || products.find(p => parseInt(p.sku) === parseInt(sku));
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
            <p class="text-base font-bold text-on-surface">${escapeHtml(message)}</p>
        </div>
        <button class="material-symbols-outlined text-[20px] text-on-surface-variant hover:text-on-surface ml-3" onclick="this.parentElement.remove()">close</button>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.className = toast.className.replace('translate-y-[-20px] opacity-0', 'translate-y-0 opacity-100');
    }, 10);

    setTimeout(() => {
        if (toast.parentNode) {
            toast.className = toast.className.replace('translate-y-0 opacity-100', 'translate-y-[-20px] opacity-0');
            setTimeout(() => {
                if (toast.parentNode) toast.remove();
            }, 300);
        }
    }, 3500);
}
