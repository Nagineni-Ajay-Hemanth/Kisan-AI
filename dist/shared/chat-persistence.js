const ChatPersistence = {
    KEY: 'kisan_chat_history',

    saveMessage(text, sender) {
        const history = this.getHistory();
        history.push({
            text,
            sender,
            timestamp: Date.now()
        });
        // Limit to last 50 messages to prevent storage overflow
        if (history.length > 50) {
            history.shift();
        }
        localStorage.setItem(this.KEY, JSON.stringify(history));
    },

    getHistory() {
        const stored = localStorage.getItem(this.KEY);
        return stored ? JSON.parse(stored) : [];
    },

    clearHistory() {
        localStorage.removeItem(this.KEY);
    }
};
