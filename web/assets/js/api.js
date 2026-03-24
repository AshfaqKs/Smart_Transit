/**
 * SmartTransit — Shared API Helper
 * Wraps fetch() with JWT auth headers and toast notifications.
 */

const API_URL = "http://127.0.0.1:5000";
const API_BASE = `${API_URL}/api`;
const API_BASE_URL = API_URL; // Alias for backward compatibility in some pages

// ── Token helpers ─────────────────────────────────────────────────────────────
function getToken() { return localStorage.getItem("st_token"); }
function getRole() { return localStorage.getItem("st_role"); }

function setAuth(token, role) {
    localStorage.setItem("st_token", token);
    localStorage.setItem("st_role", role);
}

function clearAuth() {
    localStorage.removeItem("st_token");
    localStorage.removeItem("st_role");
}

function requireAuth(expectedRole) {
    const token = getToken();
    const role = getRole();
    if (!token) { window.location.href = "/web/index.html"; return false; }
    if (expectedRole && role !== expectedRole) {
        alert("Access denied. Wrong role.");
        window.location.href = "/web/index.html";
        return false;
    }
    return true;
}

// ── Core fetch wrapper ────────────────────────────────────────────────────────
async function apiFetch(endpoint, options = {}) {
    const token = getToken();
    const headers = {
        "Content-Type": "application/json",
        ...(token ? { "Authorization": `Bearer ${token}` } : {}),
        ...(options.headers || {}),
    };

    // Don't set Content-Type for FormData (let browser set boundary)
    if (options.body instanceof FormData) {
        delete headers["Content-Type"];
    }

    try {
        const res = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });
        const data = await res.json().catch(() => ({}));

        // ── Auto-logout on invalid/expired token ─────────────────────────────
        const isAuthEndpoint = endpoint.includes('/login') || endpoint.includes('/register');
        if ((res.status === 401 || res.status === 422) && !isAuthEndpoint) {
            clearAuth();
            showToast("Session expired. Please log in again.", "error");
            setTimeout(() => { window.location.href = "/web/index.html"; }, 1500);
            throw new Error("Session expired");
        }

        // ── Allow 400 Bad Request payloads to pass through for graceful UI handling
        if (res.status === 400) {
            return data;
        }

        if (!res.ok) {
            throw new Error(data.error || data.message || `HTTP ${res.status}`);
        }
        return data;
    } catch (err) {
        if (err.message !== "Session expired") showToast(err.message, "error");
        throw err;
    }
}

// ── Shorthand methods ─────────────────────────────────────────────────────────
const api = {
    get: (url) => apiFetch(url),
    post: (url, body) => apiFetch(url, { method: "POST", body: JSON.stringify(body) }),
    put: (url, body) => apiFetch(url, { method: "PUT", body: JSON.stringify(body) }),
    delete: (url) => apiFetch(url, { method: "DELETE" }),
    upload: (url, formData) => apiFetch(url, { method: "POST", body: formData }),
};

// ── Toast notifications ───────────────────────────────────────────────────────
function showToast(message, type = "success") {
    let container = document.getElementById("toast-container");
    if (!container) {
        container = document.createElement("div");
        container.id = "toast-container";
        document.body.appendChild(container);
    }
    const toast = document.createElement("div");
    toast.className = `st-toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3500);
}

// ── Logout ────────────────────────────────────────────────────────────────────
function logout() {
    clearAuth();
    window.location.href = "/web/index.html";
}

// ── HTML escaping ─────────────────────────────────────────────────────────────
function esc(str) {
    if (str == null) return "—";
    return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// ── Build a status badge ──────────────────────────────────────────────────────
function badge(status) {
    const cls = {
        pending: "badge-pending",
        resolved: "badge-resolved",
        rejected: "badge-rejected",
        active: "badge-active",
        inactive: "badge-inactive",
        unresolved: "badge-pending",
        approved: "badge-resolved",
    }[status?.toLowerCase()] || "badge-pending";
    return `<span class="${cls}">${esc(status)}</span>`;
}

/**
 * Reverse Geocode coordinates using OpenStreetMap (Nominatim)
 */
async function reverseGeocode(lat, lng) {
    try {
        const resp = await fetch(
            `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json`,
            { headers: { "Accept-Language": "en" } }
        );
        const geo = await resp.json();
        if (geo.display_name) {
            // Return top 3 parts for conciseness (e.g. "Locality, City, State")
            return geo.display_name.split(",").slice(0, 3).join(", ");
        }
    } catch (err) { console.error("Geocode failed", err); }
    return `${lat}, ${lng}`;
}
