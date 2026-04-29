// main.js - Shared utilities used across all pages

const API_BASE = "https://internmitra-backend-t6o3.onrender.com";

function getUserId() {
  let userId = localStorage.getItem("internmitra_user_id");
  if (!userId) {
    userId = "user_" + Math.random().toString(36).substr(2, 9);
    localStorage.setItem("internmitra_user_id", userId);
  }
  return userId;
}

function getSessionId() {
  let sessionId = localStorage.getItem("internmitra_session_id");
  if (!sessionId) {
    sessionId = "session_" + Math.random().toString(36).substr(2, 9);
    localStorage.setItem("internmitra_session_id", sessionId);
  }
  return sessionId;
}

function newSessionId() {
  const sessionId = "session_" + Math.random().toString(36).substr(2, 9);
  localStorage.setItem("internmitra_session_id", sessionId);
  return sessionId;
}

// ── Safer API helper with detailed error logging ──────────────────────────────
async function apiCall(endpoint, method = "GET", body = null) {
  try {
    const options = {
      method,
      headers: { "Content-Type": "application/json" },
    };

    if (body) options.body = JSON.stringify(body);

    console.log(`🔵 API Call: ${method} ${API_BASE}${endpoint}`, body || "");

    const response = await fetch(`${API_BASE}${endpoint}`, options);
    const json = await response.json();

    if (!response.ok) {
      console.error(`🔴 API Error ${response.status}:`, json);
      throw new Error(json.detail || `HTTP ${response.status}`);
    }

    console.log(`🟢 API Response:`, json);
    return json;

  } catch (error) {
    console.error(`❌ Fetch failed [${endpoint}]:`, error.message);
    throw error;
  }
}

function showToast(message, type = "default", duration = 3000) {
  const container = document.getElementById("toastContainer");
  if (!container) return;
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.animation = "slideIn 0.3s ease reverse";
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

function formatDate(dateStr) {
  if (!dateStr) return "—";
  const date = new Date(dateStr);
  return date.toLocaleDateString("en-IN", {
    day: "numeric", month: "short", year: "numeric"
  });
}

function truncate(text, maxLength = 60) {
  if (!text) return "—";
  return text.length > maxLength ? text.substring(0, maxLength) + "..." : text;
}

window.InternMitra = {
  API_BASE,
  getUserId,
  getSessionId,
  newSessionId,
  apiCall,
  showToast,
  formatDate,
  truncate
};