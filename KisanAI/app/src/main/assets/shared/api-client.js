/**
 * Kisan AI Frontend Configuration
 * Fetches config from Cloudflare Workers ONCE on app startup
 */

// Configuration endpoint
const CONFIG_URL = "https://kisanai.ajayhemanth90.workers.dev/";

// Global variables
let API_BASE_URL = "http://localhost:8000"; // Default fallback
let CONFIG_LOADED = false;

// Configuration Loader - Called ONLY ONCE when app starts
async function loadConfig() {
    try {
        console.log("⟳ [ONE-TIME] Fetching config from Cloudflare Workers...");
        const response = await fetch(CONFIG_URL, {
            cache: 'no-cache',
            headers: {
                'Cache-Control': 'no-cache',
                'Accept': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`Config fetch failed: ${response.status}`);
        }

        // Get response as text first to debug
        const text = await response.text();
        console.log("Raw response:", text);

        // Try to parse JSON
        let config;
        try {
            config = JSON.parse(text);
        } catch (parseError) {
            console.error("JSON parse error:", parseError.message);
            console.error("Response text:", text);
            throw new Error(`Invalid JSON response: ${parseError.message}`);
        }

        console.log("✓ Config received:", config);

        // Extract backend_url from the config
        if (config.backend_url) {
            let rawUrl = config.backend_url;
            console.log("Raw config backend_url:", rawUrl);

            // Clean the URL: It might come with a log prefix like "T17:01:36Z INF | https://..."
            // We look for the http/https part.
            const urlMatch = rawUrl.match(/(https?:\/\/[^\s]+)/);
            if (urlMatch) {
                API_BASE_URL = urlMatch[0];
            } else {
                API_BASE_URL = rawUrl.trim();
            }

            // Remove trailing slash if present to avoid double slashes later
            API_BASE_URL = API_BASE_URL.replace(/\/$/, "");

            CONFIG_LOADED = true;
            console.log("✓ Backend URL parsed and set to:", API_BASE_URL);
            console.log("✓ Config will be used for ALL subsequent API requests");
        } else {
            throw new Error("backend_url not found in config");
        }

        return config;
    } catch (error) {
        console.error("⚠ Config loading failed:", error.message);
        console.log("→ Using fallback URL:", API_BASE_URL);
        return null;
    }
}

// Initialize config ONCE on app load (this promise is awaited before first API call)
const configPromise = loadConfig();

class KisanAIApi {

    static async request(endpoint, method = "GET", body = null, isFileUpload = false) {
        // Wait for config to load before making any API request
        await configPromise;

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
                let errorMessage = data.detail || data.error || "An error occurred";
                if (typeof errorMessage === 'object') {
                    errorMessage = JSON.stringify(errorMessage);
                }
                throw new Error(errorMessage);
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

    static async register(mobile, password, username, user_type = 'farmer') {
        return await this.request("/auth/register", "POST", { mobile, password, username, user_type });
    }

    /* --- FEATURES --- */
    static async createProduct(productData, userId) {
        return await this.request(`/products/create?user_id=${userId}`, "POST", productData);
    }

    static async getFarmerProducts(userId) {
        return await this.request(`/products/farmer/${userId}`);
    }

    static async deleteProduct(productId, userId) {
        return await this.request(`/products/${productId}?user_id=${userId}`, "DELETE");
    }

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

    /* --- MARKETPLACE --- */
    static async listProducts(category = null, search = null) {
        let url = '/products/list';
        const params = [];
        if (category) params.push(`category=${encodeURIComponent(category)}`);
        if (search) params.push(`search=${encodeURIComponent(search)}`);
        if (params.length > 0) url += `?${params.join('&')}`;
        return await this.request(url);
    }

    static async getProduct(productId) {
        return await this.request(`/products/${productId}`);
    }

    static async updateProduct(productId, productData, userId) {
        return await this.request(`/products/${productId}?user_id=${userId}`, "PUT", productData);
    }

    /* --- ORDERS --- */
    static async createOrder(orderData, userId) {
        return await this.request(`/orders/create?user_id=${userId}`, "POST", orderData);
    }

    static async getCustomerOrders(userId) {
        return await this.request(`/orders/customer?user_id=${userId}`);
    }

    static async getFarmerOrders(userId, status = null) {
        let url = `/orders/farmer?user_id=${userId}`;
        if (status) url += `&status=${encodeURIComponent(status)}`;
        return await this.request(url);
    }

    static async getOrderDetails(orderId, userId) {
        return await this.request(`/orders/${orderId}/details?user_id=${userId}`);
    }

    static async acceptOrder(orderId, farmerLat, farmerLon, userId) {
        return await this.request(`/orders/${orderId}/accept?user_id=${userId}`, "POST", {
            farmer_lat: farmerLat,
            farmer_lon: farmerLon
        });
    }

    static async rejectOrder(orderId, userId) {
        return await this.request(`/orders/${orderId}/reject?user_id=${userId}`, "POST");
    }

    /* --- PAYMENTS --- */
    static async processPayment(orderId, amount, paymentMethod, userId) {
        return await this.request(`/payments/process?user_id=${userId}`, "POST", {
            order_id: orderId,
            amount: amount,
            payment_method: paymentMethod
        });
    }

    static async getPaymentStatus(orderId, userId) {
        return await this.request(`/payments/order/${orderId}?user_id=${userId}`);
    }

    // Community Methods
    static async createPost(postData, userId) {
        return await this.request(`/community/posts/create?user_id=${userId}`, "POST", postData);
    }

    static async listPosts(category = null, limit = 50, offset = 0) {
        let url = `/community/posts/list?limit=${limit}&offset=${offset}`;
        if (category) url += `&category=${encodeURIComponent(category)}`;
        return await this.request(url);
    }

    static async getPost(postId) {
        return await this.request(`/community/posts/${postId}`);
    }

    static async replyToPost(postId, content, userId) {
        return await this.request(`/community/posts/${postId}/reply?user_id=${userId}`, "POST", {
            content: content
        });
    }

    static async likePost(postId, userId) {
        return await this.request(`/community/posts/${postId}/like?user_id=${userId}`, "POST");
    }

    static async likeReply(replyId, userId) {
        return await this.request(`/community/replies/${replyId}/like?user_id=${userId}`, "POST");
    }

    static async deletePost(postId, userId) {
        return await this.request(`/community/posts/${postId}?user_id=${userId}`, "DELETE");
    }

    static async deleteReply(replyId, userId) {
        return await this.request(`/community/replies/${replyId}?user_id=${userId}`, "DELETE");
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
