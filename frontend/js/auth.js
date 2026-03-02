/**
 * auth.js
 */

let currentUser = null;

async function authInit() {
  // Alles ist bereits per inline style="display:none !important" versteckt
  try {
    currentUser = await Api.auth.me();
    _showApp();
  } catch (_) {
    _showLogin();
  }
}

function _show(id, displayValue) {
  const el = document.getElementById(id);
  if (!el) return;
  // inline-style !important überschreiben durch removeProperty + neu setzen
  el.style.removeProperty("display");
  el.style.setProperty("display", displayValue, "important");
}

function _hide(id) {
  const el = document.getElementById(id);
  if (!el) return;
  el.style.setProperty("display", "none", "important");
}

function _showLogin() {
  _hide("app-navbar");
  _hide("app-wrapper");
  _show("login-page", "block");
  const u = document.getElementById("login-username");
  const p = document.getElementById("login-password");
  if (u) { u.value = ""; u.focus(); }
  if (p)   p.value = "";
  const err = document.getElementById("login-error");
  if (err) err.classList.add("d-none");
}

function _showApp() {
  _hide("login-page");
  _show("app-navbar",  "block");
  _show("app-wrapper", "flex");

  document.getElementById("nav-username").textContent = currentUser.username;
  document.getElementById("nav-rolle").textContent    = currentUser.rolle;

  document.querySelectorAll(".pl-only").forEach(el => {
    el.style.display = ["admin","pl"].includes(currentUser.rolle) ? "" : "none";
  });
  document.querySelectorAll(".admin-only").forEach(el => {
    el.style.display = currentUser.rolle === "admin" ? "" : "none";
  });

  navigate("dashboard");
}

function hasRole(...roles) {
  return currentUser && roles.includes(currentUser.rolle);
}

document.getElementById("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const btn   = document.getElementById("login-btn");
  const errEl = document.getElementById("login-error");
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Anmelden...';
  errEl.classList.add("d-none");
  try {
    currentUser = await Api.auth.login(
      document.getElementById("login-username").value.trim(),
      document.getElementById("login-password").value,
    );
    _showApp();
  } catch (e) {
    errEl.textContent = e.message;
    errEl.classList.remove("d-none");
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="bi bi-box-arrow-in-right me-1"></i>Anmelden';
  }
});

async function authLogout() {
  try { await Api.auth.logout(); } catch (_) {}
  currentUser = null;
  _showLogin();
}
