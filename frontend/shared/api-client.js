/**
 * Kisan AI Frontend Configuration
 * Dynamically loaded from GitHub
 */

// Configuration Loader - Fetches config from GitHub
class ConfigLoader {
    static GITHUB_CONFIG_URL = "https://raw.githubusercontent.com/Nagineni-Ajay-Hemanth/Kisan-AI/main/config.json";
    static LOCAL_CONFIG_URL = "config.json"; // Local fallback in assets

    static async loadConfig() {
        // Try GitHub first
        try {
            console.log("⟳ Fetching fresh config from GitHub...");
            const response = await fetch(this.GITHUB_CONFIG_URL, {
                cache: 'no-cache',
                headers: {
                    'Cache-Control': 'no-cache',
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`GitHub fetch failed: ${response.status} ${response.statusText}`);
            }

            // Check if response is actually JSON
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                throw new Error('GitHub returned HTML instead of JSON');
            }

            const config = await response.json();

            // Validate config
            if (!config.API_URL) {
                throw new Error("Invalid config: API_URL missing");
            }

            console.log("✓ Config loaded from GitHub:", config);
            return config;

        } catch (githubError) {
            console.warn("⚠ GitHub fetch failed:", githubError.message);

            // Try local config.json file
            try {
                console.log("⟳ Trying local config.json...");
                const response = await fetch(this.LOCAL_CONFIG_URL);

                if (response.ok) {
                    const config = await response.json();
                    if (config.API_URL) {
                        console.log("✓ Config loaded from local file:", config);
                        return config;
                    }
                }
            } catch (localError) {
                console.warn("⚠ Local config fetch failed:", localError.message);
            }

            // Final fallback to localhost
            console.log("→ Using default localhost config");
            return this.getDefaultConfig();
        }
    }

    static getDefaultConfig() {
        return {
            API_URL: "http://localhost:8000",
            DEBUG: true
        };
    }
}

// Global config object (will be populated after loading)
window.FARMX_CONFIG = null;
let API_BASE_URL = "http://localhost:8000"; // Default fallback

// Initialize config asynchronously
(async function initializeConfig() {
    window.FARMX_CONFIG = await ConfigLoader.loadConfig();
    API_BASE_URL = window.FARMX_CONFIG.API_URL;

    if (window.FARMX_CONFIG.DEBUG) {
        console.log("Kisan AI Config initialized:", window.FARMX_CONFIG);
    }
    console.log("Kisan AI API Base URL:", API_BASE_URL);
})();

class KisanAIApi {

    static async request(endpoint, method = "GET", body = null, isFileUpload = false) {
        const url = `${API_BASE_URL}${endpoint}`;

        const headers = {};
        if (!isFileUpload) {
            headers["Content-Type"] = "application/json";
        }

        const config = {
            method,
            headers,
        };

        if (body) {
            config.body = isFileUpload ? body : JSON.stringify(body);
        }

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || data.error || "An error occurred");
            }
            return data;
        } catch (error) {
            console.error("API Request Error:", error);
            throw error;
        }
    }

    /* --- AUTH --- */
    static async login(mobile, password) {
        const data = await this.request("/auth/login", "POST", { mobile, password });
        return data;
    }

    static async sendOtp(mobile) {
        return await this.request("/auth/send-otp", "POST", { mobile });
    }

    static async loginWithOtp(mobile, otp) {
        return await this.request("/auth/login-with-otp", "POST", { mobile, otp });
    }

    static async register(mobile, password, username) {
        return await this.request("/auth/register", "POST", { mobile, password, username });
    }

    /* --- FEATURES --- */
    static async predictDisease(imageFile, userId) {
        const formData = new FormData();
        formData.append("file", imageFile);
        formData.append("user_id", userId);
        return await this.request("/predict", "POST", formData, true);
    }

    static async predictSoil(imageFile, userId) {
        const formData = new FormData();
        formData.append("file", imageFile);
        formData.append("user_id", userId);
        return await this.request("/predict_soil", "POST", formData, true);
    }

    static async getUserAdvice(userId, lat = null, lon = null) {
        let url = `/get_user_advice/${userId}`;
        const params = [];
        if (lat) params.push(`lat=${lat}`);
        if (lon) params.push(`lon=${lon}`);

        // Add language param
        const lang = localStorage.getItem('appLanguage') || 'en';
        params.push(`language=${lang}`);

        if (params.length > 0) {
            url += `?${params.join('&')}`;
        }
        return await this.request(url);
    }

    static async recommendFertilizer(crop, soilType) {
        return await this.request(`/recommend_fertilizer?crop=${crop}&soil_type=${soilType}`);
    }

    static async getWeather(lat, lon) {
        return await this.request(`/api/weather?lat=${lat}&lon=${lon}`);
    }
}

// User Session Management
const SessionManager = {
    setUser(user) {
        localStorage.setItem("farmx_user", JSON.stringify(user));
    },
    getUser() {
        return JSON.parse(localStorage.getItem("farmx_user"));
    },
    logout() {
        localStorage.removeItem("farmx_user");
        this.redirectToLogin();
    },
    isLoggedIn() {
        return !!this.getUser();
    },
    redirectToLogin() {
        if (window.location.protocol === 'file:') {
            const path = window.location.pathname;
            // /android_asset/index.html -> split gives ["", "android_asset", "index.html"] (length 3)
            // /android_asset/disease/index.html -> split gives ["", "android_asset", "disease", "index.html"] (length 4)
            if (path.split('/').length <= 3) {
                window.location.href = "auth/login.html";
            } else {
                window.location.href = "../auth/login.html";
            }
        } else {
            window.location.href = "/auth/login.html";
        }
    },
    requireAuth() {
        if (!this.isLoggedIn()) {
            // Avoid redirect loop if already on login page
            if (window.location.href.includes('auth/login.html')) return;
            this.redirectToLogin();
        }
    }
};
