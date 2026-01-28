class VoiceAssistant {
    constructor() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            console.warn("Voice API not supported");
            return;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = false;

        // Default to English, but ideally should match app language
        this.recognition.lang = 'en-IN';

        this.isListening = false;
        this.btn = null;

        this.initUI();
        this.setupListeners();
    }

    initUI() {
        this.btn = document.createElement('button');
        this.btn.className = 'voice-fab';
        this.btn.innerHTML = '🎤';
        this.btn.onclick = () => this.toggleListen();
        document.body.appendChild(this.btn);

        // Feedback Toast
        this.toast = document.createElement('div');
        this.toast.className = 'voice-toast';
        this.toast.style.display = 'none';
        document.body.appendChild(this.toast);
    }

    setupListeners() {
        this.recognition.onstart = () => {
            this.isListening = true;
            this.btn.classList.add('listening');
            this.showFeedback("Listening...");
        };

        this.recognition.onend = () => {
            this.isListening = false;
            this.btn.classList.remove('listening');
        };

        this.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript.toLowerCase();
            this.showFeedback(`Head: "${transcript}"`);
            this.processCommand(transcript);
        };

        this.recognition.onerror = (event) => {
            console.error("Voice Error", event.error);
            this.showFeedback("Error: " + event.error);
            this.isListening = false;
            this.btn.classList.remove('listening');
        };
    }

    toggleListen() {
        if (this.isListening) {
            this.recognition.stop();
        } else {
            // Check current language from localStorage if available
            const savedLang = localStorage.getItem('appLanguage');
            if (savedLang) {
                // Map app lang codes to Speech API codes
                const langMap = {
                    'hi': 'hi-IN',
                    'te': 'te-IN',
                    'ta': 'ta-IN',
                    'bn': 'bn-IN',
                    'gu': 'gu-IN',
                    'mr': 'mr-IN',
                    'kn': 'kn-IN',
                    'ml': 'ml-IN',
                    'pa': 'pa-IN',
                    'ur': 'ur-IN',
                    'en': 'en-IN'
                };
                this.recognition.lang = langMap[savedLang] || 'en-IN';
            }
            try {
                this.recognition.start();
            } catch (e) {
                console.error(e);
            }
        }
    }

    showFeedback(text) {
        this.toast.innerText = text;
        this.toast.style.display = 'block';
        setTimeout(() => {
            this.toast.style.display = 'none';
        }, 3000);
    }

    processCommand(cmd) {
        // Base navigation logic
        // We need to handle relative paths depending on where we are
        const isRoot = window.location.pathname.endsWith('frontend/index.html') || window.location.pathname.endsWith('/app/src/main/assets/index.html');
        const prefix = isRoot ? '' : '../';

        if (cmd.includes('home') || cmd.includes('ghar')) {
            window.location.href = prefix + 'index.html';
        }
        else if (cmd.includes('weather') || cmd.includes('mausam')) {
            window.location.href = prefix + 'weather/index.html';
        }
        else if (cmd.includes('market') || cmd.includes('mandi') || cmd.includes('bazaar')) {
            window.location.href = prefix + 'market/index.html';
        }
        else if (cmd.includes('water') || cmd.includes('pani') || cmd.includes('irrigation')) {
            window.location.href = prefix + 'water/index.html';
        }
        else if (cmd.includes('scheme') || cmd.includes('yojana')) {
            window.location.href = prefix + 'schemes/index.html';
        }
        else if (cmd.includes('info') || cmd.includes('fasal') || cmd.includes('guide')) {
            window.location.href = prefix + 'info/index.html';
        }
        else if (cmd.includes('disease') || cmd.includes('rog') || cmd.includes('doctor')) {
            window.location.href = prefix + 'disease/index.html';
        }
    }
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    window.voiceAssistant = new VoiceAssistant();
});
