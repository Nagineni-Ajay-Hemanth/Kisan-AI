//login page components 
/* UI TOGGLES */
function showRegister() {
    document.getElementById("loginBox").style.display = "none";
    document.getElementById("registerBox").style.display = "block";
    clearErrors();
}

function showLogin() {
    document.getElementById("registerBox").style.display = "none";
    document.getElementById("loginBox").style.display = "block";
    clearErrors();
}

function clearErrors() {
    document.getElementById("loginError").style.display = "none";
    document.getElementById("regError").style.display = "none";
}

function togglePassword(inputId, icon) {
    const input = document.getElementById(inputId);
    if (input.type === "password") {
        input.type = "text";
        icon.textContent = "🙈";
    } else {
        input.type = "password";
        icon.textContent = "👁️";
    }
}

function switchLoginMode(mode) {
    const tabPass = document.getElementById('tabPassword');
    const tabOtp = document.getElementById('tabOtp');
    const secPass = document.getElementById('sectionPassword');
    const secOtp = document.getElementById('sectionOtp');

    clearErrors();

    if (mode === 'password') {
        tabPass.classList.add('active');
        tabOtp.classList.remove('active');

        secPass.style.display = 'block';
        secOtp.style.display = 'none';
    } else {
        tabOtp.classList.add('active');
        tabPass.classList.remove('active');

        secPass.style.display = 'none';
        secOtp.style.display = 'block';
    }
}

/* API ACTIONS */
async function login() {
    const mobile = document.getElementById("loginMobile").value;
    const password = document.getElementById("loginPassword").value;
    const btn = document.getElementById("btnLogin");
    const errorEl = document.getElementById("loginError");

    if (!mobile || !password) {
        showError(errorEl, "Please enter both mobile number and password.");
        return;
    }

    try {
        btn.innerHTML = "Logging in...";
        btn.disabled = true;

        const response = await KisanAIApi.login(mobile, password);
        handleLoginSuccess(response, mobile);

    } catch (error) {
        handleApiError(error, errorEl);
        btn.innerHTML = "Login";
        btn.disabled = false;
    }
}

async function sendOtp() {
    const mobile = document.getElementById("loginMobile").value;
    const btn = document.getElementById("btnGetOtp");
    const errorEl = document.getElementById("loginError");

    if (!mobile) {
        showError(errorEl, "Please enter your mobile number first.");
        return;
    }

    try {
        btn.innerHTML = "Sending...";
        btn.disabled = true;

        const response = await KisanAIApi.sendOtp(mobile);

        // Show OTP Input
        document.getElementById('otpRequestStep').style.display = 'none';
        document.getElementById('otpVerifyStep').style.display = 'block';

        // DEMO: Alert the OTP
        if (response.otp) {
            setTimeout(() => alert(`Kisan AI DEMO OTP: ${response.otp}`), 500);
        }

    } catch (error) {
        handleApiError(error, errorEl);
        btn.innerHTML = "Get OTP Code";
        btn.disabled = false;
    }
}

async function verifyOtpAndLogin() {
    const mobile = document.getElementById("loginMobile").value;
    const otp = document.getElementById("loginOtpInput").value;
    const btn = document.getElementById("btnVerifyOtp");
    const errorEl = document.getElementById("loginError");

    if (!otp) {
        showError(errorEl, "Please enter the 4-digit OTP.");
        return;
    }

    try {
        btn.innerHTML = "Verifying...";
        btn.disabled = true;

        const response = await KisanAIApi.loginWithOtp(mobile, otp);
        handleLoginSuccess(response, mobile);

    } catch (error) {
        handleApiError(error, errorEl);
        btn.innerHTML = "Verify & Login";
        btn.disabled = false;
    }
}

function resetOtpFlow() {
    document.getElementById('otpRequestStep').style.display = 'block';
    document.getElementById('otpVerifyStep').style.display = 'none';
    document.getElementById('loginOtpInput').value = "";
    document.getElementById('btnGetOtp').disabled = false;
    document.getElementById('btnGetOtp').innerHTML = "Get OTP Code";
    clearErrors();
}

function handleLoginSuccess(response, mobile) {
    SessionManager.setUser({
        id: response.user_id,
        username: response.username,
        mobile: mobile,
        user_type: response.user_type || 'farmer'
    });
    window.location.href = "../index.html";
}

async function register() {
    const name = document.getElementById("regName").value;
    const mobile = document.getElementById("regMobile").value;
    const pass = document.getElementById("regPassword").value;
    const confirm = document.getElementById("regConfirm").value;
    const btn = document.getElementById("btnRegister");
    const errorEl = document.getElementById("regError");

    if (!name || !mobile || !pass || !confirm) {
        showError(errorEl, "Please fill in all fields.");
        return;
    }

    if (pass !== confirm) {
        showError(errorEl, "Passwords do not match.");
        return;
    }

    try {
        btn.innerHTML = "Creating Account...";
        btn.disabled = true;

        await KisanAIApi.register(mobile, pass, name, 'farmer');

        alert("Registration Successful! Please login.");
        showLogin();

    } catch (error) {
        handleApiError(error, errorEl);
    } finally {
        btn.innerHTML = "Register";
        btn.disabled = false;
    }
}

function showError(element, message) {
    element.textContent = message;
    element.style.display = "block";
}

function handleApiError(error, element) {
    let msg = error.message;
    if (msg.includes("Failed to fetch") || msg.includes("NetworkError")) {
        msg = "Cannot connect to server. Please ensure backend is running.";
    }
    showError(element, msg);
}

// Auto-redirect if already logged in (optional check)
if (SessionManager.isLoggedIn()) {
    // window.location.href = "../index.html"; 
}
