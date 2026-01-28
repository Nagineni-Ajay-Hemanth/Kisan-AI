
document.addEventListener('DOMContentLoaded', () => {
    // Inject Modal HTML
    const modalHtml = `
    <div id="languageModal" class="lang-modal">
        <div class="lang-modal-content">
            <span class="close-modal" onclick="toggleLanguageModal()">&times;</span>
            <h3>Select Language / भाषा चुनें / భాషను ఎంచుకోండి</h3>
            <div class="lang-options" style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                <button onclick="setLanguage('en')">English</button>
                <button onclick="setLanguage('hi')">Hindi (हिंदी)</button>
                <button onclick="setLanguage('te')">Telugu (తెలుగు)</button>
                <button onclick="setLanguage('bn')">Bengali (বাংলা)</button>
                <button onclick="setLanguage('mr')">Marathi (मराठी)</button>
                <button onclick="setLanguage('ta')">Tamil (தமிழ்)</button>
                <button onclick="setLanguage('gu')">Gujarati (ગુજરાતી)</button>
                <button onclick="setLanguage('kn')">Kannada (ಕನ್ನಡ)</button>
                <button onclick="setLanguage('ml')">Malayalam (മലയാളം)</button>
                <button onclick="setLanguage('pa')">Punjabi (ਪੰਜਾਬੀ)</button>
                <button onclick="setLanguage('or')">Odia (ଓଡ଼ିଆ)</button>
                <button onclick="setLanguage('as')">Assamese (অসমীয়া)</button>
                <button onclick="setLanguage('ur')">Urdu (اردو)</button>
            </div>
        </div>
    </div>`;
    document.body.insertAdjacentHTML('beforeend', modalHtml);

    // Apply saved language
    const savedLang = localStorage.getItem('appLanguage') || 'en';
    applyLanguage(savedLang);
});

window.toggleLanguageModal = function () {
    const modal = document.getElementById('languageModal');
    if (!modal) return;
    if (modal.style.display === 'flex') {
        modal.style.display = 'none';
    } else {
        modal.style.display = 'flex';
    }
}

window.setLanguage = function (lang) {
    localStorage.setItem('appLanguage', lang);
    applyLanguage(lang);
    toggleLanguageModal();

    // Explicitly reload if on home page to force refresh dynamic content if needed
    // location.reload(); 
    // ^ No, reload is bad UX. applyLanguage should be enough.
}

function applyLanguage(lang) {
    if (!window.translations || !window.translations[lang]) return;

    const elements = document.querySelectorAll('[data-i18n]');
    elements.forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (window.translations[lang][key]) {
            if (el.tagName === 'INPUT' && el.getAttribute('placeholder')) {
                el.placeholder = window.translations[lang][key];
            } else {
                el.textContent = window.translations[lang][key];
            }
        }
    });
}
window.applyLanguage = applyLanguage;
