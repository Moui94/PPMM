function _isoToCH(s){if(!s)return "—";const d=s.substring(0,10).split("-");return d.length===3?`${d[2]}.${d[1]}.${d[0]}`:s;}
/**
 * app.js – SPA-Router, Hilfsfunktionen, Initialisierung.
 */

// ── Router ────────────────────────────────────────────────────────────────
const ROUTES = {
  "dashboard":   (p) => renderDashboard(p),
  "order":       (p) => renderOrder(p),
  "order-new":   (p) => renderOrderNew(p),
  "order-edit":  (p) => renderOrderEdit(p),
  "op-edit":     (p) => renderOpEdit(p),
  "feedback":    (p) => renderFeedback(p),
  "schedule":    (p) => renderSchedule(p),
  "haas-plan":   (p) => renderHaasKapazitaet(p),
  "quality":     (p) => renderQuality(p),
  "catalog":     (p) => renderCatalog(p),
  "users":       (p) => renderUsers(p),
  "user-new":    (p) => renderUserNew(p),
};

function navigate(route, params = {}) {
  // Sidebar active-State
  document.querySelectorAll(".sidebar .nav-link").forEach(a => a.classList.remove("active"));

  const handler = ROUTES[route];
  if (!handler) {
    document.getElementById("app-content").innerHTML =
      alertHtml(`Unbekannte Route: ${route}`, "warning");
    return;
  }
  // Schedule-Countdown stoppen bei Seitenwechsel
  if (typeof schedCountdownTimer !== "undefined" && schedCountdownTimer) {
    clearInterval(schedCountdownTimer);
    schedCountdownTimer = null;
  }
  handler(params);
}

// ── Benutzer-Seiten (einfach inline) ─────────────────────────────────────
async function renderUsers() {
  const el = document.getElementById("app-content");
  el.innerHTML = loadingHtml();
  let users;
  try { users = await Api.users.list(); }
  catch (e) { el.innerHTML = alertHtml(e.message); return; }

  const rows = users.map(u => `
    <tr>
      <td><strong>${esc(u.username)}</strong></td>
      <td><span class="badge bg-primary">${u.rolle}</span></td>
      <td><span class="badge bg-${u.aktiv?'success':'secondary'}">${u.aktiv?'Aktiv':'Inaktiv'}</span></td>
      <td>${_isoToCH(u.created_at||"")}</td>
      <td>
        <button class="btn btn-sm btn-outline-warning py-0 ms-1"
          onclick="toggleUser(${u.id},'${esc(u.username)}')">
          <i class="bi bi-toggle-${u.aktiv?'on':'off'}"></i></button>
      </td>
    </tr>`).join("");

  el.innerHTML = `
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h4 class="fw-bold mb-0"><i class="bi bi-people me-2"></i>Benutzerverwaltung</h4>
      <button class="btn btn-primary btn-sm" onclick="navigate('user-new')">
        <i class="bi bi-person-plus me-1"></i>Neuer Benutzer</button>
    </div>
    <div class="card">
      <div class="card-body p-0">
        <table class="table table-sm table-hover mb-0">
          <thead class="table-dark">
            <tr><th>Benutzername</th><th>Rolle</th><th>Status</th><th>Erstellt</th><th></th></tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
    </div>`;
}

async function toggleUser(id, username) {
  if (username === "admin") { showToast("Admin kann nicht deaktiviert werden.", "warning"); return; }
  try {
    await Api.users.toggle(id);
    showToast("Benutzer-Status geändert.", "success");
    renderUsers();
  } catch (e) { showToast(e.message, "danger"); }
}

function renderUserNew() {
  const el = document.getElementById("app-content");
  el.innerHTML = `
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h4 class="fw-bold mb-0">Neuer Benutzer</h4>
      <button class="btn btn-sm btn-outline-secondary" onclick="navigate('users')">← Zurück</button>
    </div>
    <div class="card" style="max-width:480px">
      <div class="card-body">
        <div id="user-alert" class="d-none"></div>
        <div class="mb-3">
          <label class="form-label fw-bold">Benutzername</label>
          <input type="text" id="u-username" class="form-control" required>
        </div>
        <div class="mb-3">
          <label class="form-label fw-bold">Passwort</label>
          <input type="password" id="u-password" class="form-control" required>
          <div class="form-text">Mind. 6 Zeichen.</div>
        </div>
        <div class="mb-3">
          <label class="form-label fw-bold">Rolle</label>
          <select id="u-rolle" class="form-select">
            <option value="ma">ma – Mitarbeiter</option>
            <option value="pl">pl – Projektleitung</option>
            <option value="admin">admin – Administrator</option>
          </select>
        </div>
        <button class="btn btn-primary" onclick="saveUser()">
          <i class="bi bi-person-plus me-1"></i>Benutzer anlegen</button>
      </div>
    </div>`;
}

async function saveUser() {
  const alert = document.getElementById("user-alert");
  alert.className = "d-none";
  try {
    await Api.users.create({
      username: document.getElementById("u-username").value.trim(),
      password: document.getElementById("u-password").value,
      rolle:    document.getElementById("u-rolle").value,
    });
    showToast("Benutzer angelegt.", "success");
    navigate("users");
  } catch (e) {
    alert.className   = "alert alert-danger py-2";
    alert.textContent = e.message;
  }
}

// ── Utility-Funktionen ────────────────────────────────────────────────────
function esc(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g,"&amp;").replace(/</g,"&lt;")
    .replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}

function cap(str) {
  return str ? str.charAt(0).toUpperCase() + str.slice(1) : "";
}

function loadingHtml(text = "Wird geladen...") {
  return `<div class="text-center text-muted py-5">
    <div class="spinner-border text-primary mb-2"></div>
    <div>${text}</div></div>`;
}

function alertHtml(msg, type = "danger") {
  return `<div class="alert alert-${type}"><i class="bi bi-exclamation-triangle me-1"></i>${esc(msg)}</div>`;
}

function showToast(message, type = "success") {
  const id  = "toast-" + Date.now();
  const bg  = { success:"bg-success", danger:"bg-danger", warning:"bg-warning text-dark",
                info:"bg-info text-dark" }[type] ?? "bg-secondary";
  const html = `<div id="${id}" class="toast align-items-center text-white ${bg} border-0"
    role="alert" aria-live="assertive">
    <div class="d-flex">
      <div class="toast-body">${esc(message)}</div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto"
              data-bs-dismiss="toast"></button>
    </div></div>`;
  document.getElementById("toast-container").insertAdjacentHTML("beforeend", html);
  const toastEl = document.getElementById(id);
  new bootstrap.Toast(toastEl, { delay: 4000 }).show();
  toastEl.addEventListener("hidden.bs.toast", () => toastEl.remove());
}

// Live-Uhr
function tick() {
  const el = document.getElementById("clock");
  if (el) el.textContent = new Date().toLocaleString("de-CH");
}
tick(); setInterval(tick, 1000);

// App starten



// App starten
document.addEventListener('DOMContentLoaded', () => authInit());
