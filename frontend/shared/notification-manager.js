
document.addEventListener('DOMContentLoaded', () => {
    // Inject Notification Modal HTML
    const modalHtml = `
    <div id="notificationModal" class="lang-modal">
        <div class="lang-modal-content">
            <span class="close-modal" onclick="toggleNotificationModal()">&times;</span>
            <h3 style="margin-bottom: 20px;">Notifications</h3>
            <div id="notificationList" style="min-height: 100px; display: flex; align-items: center; justify-content: center; flex-direction: column;">
                <img src="${getRelativeAssetPath('notify.png')}" style="width: 48px; opacity: 0.3; margin-bottom: 10px;">
                <p style="color: var(--text-secondary);">No new notifications</p>
            </div>
            <button onclick="toggleNotificationModal()" class="btn-secondary" style="margin-top: 20px;">Close</button>
        </div>
    </div>`;
    document.body.insertAdjacentHTML('beforeend', modalHtml);
});

// Helper to find assets relative to current page depth
function getRelativeAssetPath(assetName) {
    // Check if we are in a subfolder (based on dots in script src or location)
    // Simple heuristic: if window.location.pathname has more than 2 segments (/, frontend, index.html)
    // Better: use relative path from the script location logic?
    // Hardcoded simple check:
    const path = window.location.pathname;
    // If we are in 'disease/' or 'market/', we need '../shared/assets/'
    // If we are in root, we need 'shared/assets/'

    // Quick crude check: look for subdirectories
    if (path.includes('/disease/') || path.includes('/market/') || path.includes('/weather/') || path.includes('/advice/') || path.includes('/fertilizer/') || path.includes('/protect/') || path.includes('/auth/')) {
        return '../shared/assets/' + assetName;
    }
    return 'shared/assets/' + assetName;
}

window.toggleNotificationModal = function () {
    const modal = document.getElementById('notificationModal');
    if (!modal) return;
    if (modal.style.display === 'flex') {
        modal.style.display = 'none';
    } else {
        modal.display = 'flex'; // This might fail if flex is not set in CSS request
        modal.style.display = 'flex';
    }
}

// Global Toast function for other interactions
window.showToast = function (message) {
    // Remove existing toast
    const existing = document.getElementById('farmx-toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.id = 'farmx-toast';
    toast.style.cssText = `
        position: fixed;
        bottom: 100px;
        left: 50%;
        transform: translateX(-50%);
        background: #323232;
        color: white;
        padding: 12px 24px;
        border-radius: 24px;
        font-size: 0.9rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 5000;
        opacity: 0;
        transition: opacity 0.3s ease;
    `;
    toast.textContent = message;
    document.body.appendChild(toast);

    // Fade in
    requestAnimationFrame(() => {
        toast.style.opacity = '1';
    });

    // Remove
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 2500);
}
