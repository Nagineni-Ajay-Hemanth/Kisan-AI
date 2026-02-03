/* crop analyzer,soil analyzer components*/
// --- CHAT LOGIC ---
function openChat() {
    document.getElementById('chatModal').style.display = 'flex';
    loadChatMessages();
    // Scroll to bottom
    const history = document.getElementById('chatHistory');
    history.scrollTop = history.scrollHeight;
}

function closeChat() {
    document.getElementById('chatModal').style.display = 'none';
}

function handleEnter(e) {
    if (e.key === 'Enter') sendMessage();
}

function loadChatMessages() {
    const history = ChatPersistence.getHistory();
    const chatContainer = document.getElementById('chatHistory');

    // Clear current list except welcome message (optional, or remove welcome msg if history exists)
    chatContainer.innerHTML = '';

    if (history.length === 0) {
        chatContainer.innerHTML = `
            <div class="chat-message ai-message">
                Namaste! Ask me anything about farming.
            </div>
        `;
    }

    history.forEach(msg => {
        appendMessageUI(msg.text, msg.sender);
    });
}

function appendMessageUI(text, sender) {
    const chatContainer = document.getElementById('chatHistory');
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('chat-message');
    msgDiv.style.wordWrap = 'break-word';

    if (sender === 'user') {
        msgDiv.classList.add('user-message');
    } else {
        msgDiv.classList.add('ai-message');
    }

    msgDiv.innerText = text;
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function sendMessage() {
    const input = document.getElementById('chatInput');
    const text = input.value.trim();
    if (!text) return;

    // 1. User Message
    appendMessageUI(text, 'user');
    ChatPersistence.saveMessage(text, 'user');
    input.value = '';

    // 2. AI Response Simulation (replace with API call later)
    setTimeout(() => {
        const lang = localStorage.getItem('appLanguage') || 'en';

        const responses = {
            en: "I am processing your query... Please check specific sections for details.",
            hi: "मैं आपके प्रश्न पर कार्रवाई कर रहा हूं... कृपया विवरण के लिए विशिष्ट अनुभाग देखें।",
            te: "నేను మీ ప్రశ్నను ప్రాసెస్ చేస్తున్నాను... వివరాల కోసం దయచేసి నిర్దిష్ట విభాగాలను తనిఖీ చేయండి.",
            bn: "আমি আপনার প্রশ্ন প্রক্রিয়া করছি...",
            mr: "मी आपल्या प्रश्नावर प्रक्रिया करत आहे...",
            ta: "உங்கள் கேள்வியை நான் செயலாக்குகிறேன்...",
            gu: "હું તમારી ક્વેરી પર પ્રક્રિયા કરી રહ્યો છું...",
            kn: "ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ನಾನು ಪ್ರಕ್ರಿಯೆಗೊಳಿಸುತ್ತಿದ್ದೇನೆ...",
            ml: "ഞാൻ ನಿಮ್ಮ ചോദ്യം ಪ್ರോസಸ್സ് ചെയ്യുന്നു...",
            pa: "ਮੈਂ ਤੁਹਾਡੀ ਪੁੱਛਗਿੱਛ 'ਤੇ ਕਾਰਵਾਈ ਕਰ ਰਿਹਾ ਹਾਂ...",
            or: "ମୁଁ ଆପଣଙ୍କର ପ୍ରଶ୍ନର ପ୍ରକ୍ରିୟାକରଣ କରୁଛି...",
            as: "মই আপোনাৰ প্ৰଶ୍ନটো প্ৰক্ৰিয়াকৰণ কৰি আছো...",
            ur: "میں آپ کے سوال پر کارروائی کر رہا ہوں..."
        };

        let response = responses[lang] || responses['en'];

        // Simple keyword matching (only works for English inputs mostly)
        if (lang === 'en') {
            if (text.toLowerCase().includes('weather')) response = "Please check the Weather section for detailed forecasts.";
            else if (text.toLowerCase().includes('price')) response = "Market prices vary. Check the Market section.";
        }

        appendMessageUI(response, 'ai');
        ChatPersistence.saveMessage(response, 'ai');

    }, 1000);
}

function clearChatHistory() {
    if (confirm("Clear chat history?")) {
        ChatPersistence.clearHistory();
        loadChatMessages();
    }
}

// --- HOME PAGE LOGIC ---
document.addEventListener('DOMContentLoaded', () => {
    SessionManager.requireAuth();

    const user = SessionManager.getUser();
    if (user && user.username) {
        const hours = new Date().getHours();
        let timeGreeting = "Hello";
        if (hours < 12) timeGreeting = "Good Morning";
        else if (hours < 18) timeGreeting = "Good Afternoon";
        else timeGreeting = "Good Evening";

        // Use translation for greeting if possible (or keep simple)
        // For strict translation, we'd need keys for "Good Morning" etc.
        // Let's stick to name insertion into fixed element or update via i18n
        // Ideally: window.translations[lang]['greeting_morning']...
        document.getElementById('greetingUser').textContent = `${timeGreeting}, ${user.username}`;

        // Show Farmer Tools if applicable
        if (user.user_type === 'farmer') {
            const farmerSection = document.getElementById('farmerToolsSection');
            if (farmerSection) {
                farmerSection.style.display = 'block';
                // Move it to top for better visibility (optional but good)
                // const container = document.querySelector('.container');
                // const quickAccess = document.querySelector('.quick-access-grid').parentElement; // This is a bit risky with selector structure
                // But simplified: just show it.
            }
        }
    }

    // Fetch Weather for Home Widget
    loadHomeWeather();
});

function loadHomeWeather() {
    // Try cache first
    const cached = localStorage.getItem('last_weather');
    if (cached) {
        updateHomeWeatherUI(JSON.parse(cached));
    }

    // Fetch fresh if location available
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(async (position) => {
            try {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                const data = await KisanAIApi.getWeather(lat, lon);


                localStorage.setItem('last_weather', JSON.stringify(data));
                updateHomeWeatherUI(data);
            } catch (e) {
                console.error("Weather fetch failed", e);
                setWeatherText('weather_fail', 'weather_retry');
            }
        }, (err) => {
            console.log("Location denied or unavailable: ", err);
            setWeatherText('weather_denied', 'weather_gps_error');
        });
    } else {
        setWeatherText('weather_gps_error', 'weather_retry');
    }
}

function setWeatherText(condKey, tempKey) {
    // Helper to set text using translation keys if available
    const lang = localStorage.getItem('appLanguage') || 'en';
    const t = window.translations && window.translations[lang] ? window.translations[lang] : {};

    document.getElementById('wConditionHome').textContent = t[condKey] || condKey;
    document.getElementById('wTempHome').textContent = t[tempKey] || tempKey;
}

function updateHomeWeatherUI(data) {
    let icon = "☀️";
    if (data.condition.includes("Cloud")) icon = "☁️";
    if (data.condition.includes("Rain")) icon = "🌧️";

    // Use API condition (English) + Translated Label if we expanded system
    // For now: API Condition + Icon
    document.getElementById('wConditionHome').textContent = `${data.condition} ${icon}`; // Keeping API condition usually in English
    document.getElementById('wTempHome').innerHTML = `${data.temperature}°C &bull; Humidity: ${data.humidity}%`;
}
