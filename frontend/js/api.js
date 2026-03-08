/**
 * api.js – Zentralisierte fetch()-Aufrufe zur Backend-API.
 * Alle Funktionen geben Promises zurück und werfen bei Fehler eine Exception.
 */

const API_BASE = "/api";

async function apiFetch(path, options = {}) {
  const defaults = {
    headers: { "Content-Type": "application/json" },
    credentials: "same-origin",
  };
  const res = await fetch(API_BASE + path, { ...defaults, ...options });
  const json = await res.json().catch(() => ({ ok: false, error: "Ungültige Server-Antwort" }));
  if (!json.ok) throw new ApiError(json.error || "Unbekannter Fehler", res.status);
  return json.data ?? json;
}

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

// ── Auth ──────────────────────────────────────────────────────────────────
const Api = {
  auth: {
    login:  (username, password) =>
      apiFetch("/auth/login",  { method: "POST", body: JSON.stringify({ username, password }) }),
    logout: () =>
      apiFetch("/auth/logout", { method: "POST" }),
    me:     () => apiFetch("/auth/me"),
  },

  // ── Orders ───────────────────────────────────────────────────────────────
  orders: {
    list:   (params = {}) => {
      const qs = new URLSearchParams(
        Object.fromEntries(Object.entries(params).filter(([,v]) => v !== "" && v != null))
      ).toString();
      return apiFetch("/orders" + (qs ? "?" + qs : ""));
    },
    produkte: (art=null, menge=0) => apiFetch("/orders/produkte" + `?${art?"art="+art+"&":""}${menge?"menge="+menge:""}`),
    kpis:   () => apiFetch("/orders/kpis"),
    get:    (paNr) => apiFetch(`/orders/${paNr}`),
    create: (data) => apiFetch("/orders", { method: "POST", body: JSON.stringify(data) }),
    update: (paNr, data) =>
      apiFetch(`/orders/${paNr}`, { method: "PUT", body: JSON.stringify(data) }),
    ops:    (paNr) => apiFetch(`/orders/${paNr}/ops`),
  },

  // ── Operations ────────────────────────────────────────────────────────────
  operations: {
    get:      (opId) => apiFetch(`/operations/${opId}`),
    update:   (opId, data) =>
      apiFetch(`/operations/${opId}`, { method: "PUT", body: JSON.stringify(data) }),
    feedback: (opId, data) =>
      apiFetch(`/operations/${opId}/feedback`, { method: "POST", body: JSON.stringify(data) }),
    feedbacks:(opId) => apiFetch(`/operations/${opId}/feedbacks`),
  },

  // ── Quality ───────────────────────────────────────────────────────────────
  quality: {
    pareto:    (agNr = null, limit = 10) =>
      apiFetch(agNr ? `/quality/pareto/${agNr}?limit=${limit}` : `/quality/pareto?limit=${limit}`),
    ausschuss: (paNr) => apiFetch(`/quality/ausschuss/${paNr}`),
    catalog:   (agNr = null) =>
      apiFetch(agNr ? `/quality/catalog?ag_nr=${agNr}` : "/quality/catalog"),
  },

  // ── Users ─────────────────────────────────────────────────────────────────
  users: {
    list:   () => apiFetch("/users"),
    create: (data) => apiFetch("/users", { method: "POST", body: JSON.stringify(data) }),
    update: (id, data) =>
      apiFetch(`/users/${id}`, { method: "PUT", body: JSON.stringify(data) }),
    changePw: (id, password) =>
      apiFetch(`/users/${id}/pw`, { method: "PUT", body: JSON.stringify({ password }) }),
    toggle: (id) =>
      apiFetch(`/users/${id}/toggle`, { method: "PUT" }),
  },
};
