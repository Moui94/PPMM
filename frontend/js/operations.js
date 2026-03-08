/**
 * operations.js — AG bearbeiten + Rückmeldungsformular.
 */

// ── AG bearbeiten ─────────────────────────────────────────────────────────────
async function renderOpEdit(params = {}) {
  const { opId, paNr } = params;
  const el = document.getElementById("app-content");
  el.innerHTML = loadingHtml();
  let op;
  try { op = await Api.operations.get(opId); }
  catch (e) { el.innerHTML = alertHtml(e.message); return; }

  // Maschinen-Dropdown (Fräs-AG) oder Kapazitäts-Dropdown (andere AG)
  let kapazitaetHtml = "";
  if (op.ist_fraes_ag && op.maschinen_liste.length) {
    // AG01–03: Maschinen-Dropdown
    const opts = op.maschinen_liste.map(([nr, label]) =>
      `<option value="${nr}" ${op.maschine === nr ? "selected" : ""}>${nr} – ${label}</option>`
    ).join("");
    kapazitaetHtml = `
      <div class="col-md-3">
        <label class="form-label fw-bold">Maschine (Haas)</label>
        <select id="op-maschine" class="form-select">
          <option value="">— wählen —</option>${opts}
        </select>
      </div>`;
  } else if (op.kapazitaet_fix) {
    // AG04–14: fix, nur anzeigen
    kapazitaetHtml = `
      <div class="col-md-3">
        <label class="form-label fw-bold">Kapazität</label>
        <input type="text" class="form-control bg-light"
               value="${op.kapazitaet_fix}" readonly
               title="Kapazität ist fix hinterlegt">
      </div>`;
  }

  el.innerHTML = `
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h4 class="fw-bold mb-0">${op.ag_nr_fmt} bearbeiten – PA ${esc(op.pa_nr)}</h4>
      <button class="btn btn-sm btn-outline-secondary"
        onclick="navigate('order',{paNr:'${esc(op.pa_nr)}'})">← Zurück</button>
    </div>
    <div class="card">
      <div class="card-header">${esc(op.bezeichnung)}</div>
      <div class="card-body">
        <div id="op-alert" class="d-none"></div>
        <div class="row g-3">
          <div class="col-md-2">
            <label class="form-label fw-bold">Solldauer (Tage)</label>
            <input type="number" step="0.5" id="op-solldauer"
                   class="form-control" value="${op.solldauer_tage}" min="0.5">
          </div>
          <div class="col-md-3">
            <label class="form-label fw-bold">Start Soll</label>
            <input type="date" id="op-start_soll" class="form-control"
                   value="${op.start_soll}">
          </div>
          <div class="col-md-2">
            <label class="form-label fw-bold">Status</label>
            <select id="op-status" class="form-select">
              ${["offen","laufend","abgeschlossen"].map(s =>
                `<option value="${s}" ${op.status===s?"selected":""}>${cap(s)}</option>`
              ).join("")}
            </select>
          </div>
          ${kapazitaetHtml}
          <div class="col-md-4">
            <label class="form-label fw-bold">Bemerkung</label>
            <input type="text" id="op-bemerkung" class="form-control"
                   value="${esc(op.bemerkung ?? '')}">
          </div>
        </div>
        <div class="d-flex gap-2 mt-3">
          <button class="btn btn-primary" id="op-save-btn"
                  onclick="saveOp(${opId},'${esc(op.pa_nr)}',${op.ist_fraes_ag})">
            <i class="bi bi-save me-1"></i>Speichern</button>
          <button class="btn btn-outline-secondary"
            onclick="navigate('order',{paNr:'${esc(op.pa_nr)}'})">Abbrechen</button>
        </div>
      </div>
    </div>`;
}

async function saveOp(opId, paNr, isFraesAg) {
  const btn   = document.getElementById("op-save-btn");
  const alert = document.getElementById("op-alert");
  btn.disabled = true;
  alert.className = "d-none";
  const data = {
    solldauer_tage: parseFloat(document.getElementById("op-solldauer")?.value),
    start_soll:     document.getElementById("op-start_soll")?.value || null,
    maschine:       isFraesAg ? (document.getElementById("op-maschine")?.value || null) : null,
    kapazitaet:     !isFraesAg ? (document.getElementById("op-kapazitaet")?.value || null) : null,
    status:         document.getElementById("op-status")?.value,
    bemerkung:      document.getElementById("op-bemerkung")?.value.trim() || null,
  };
  Object.keys(data).forEach(k => { if (data[k] === null) delete data[k]; });
  try {
    await Api.operations.update(opId, data);
    showToast("Arbeitsgang gespeichert.", "success");
    navigate("order", { paNr });
  } catch (e) {
    alert.className   = "alert alert-danger py-2";
    alert.textContent = e.message;
    btn.disabled = false;
  }
}

// ── Rückmeldung ───────────────────────────────────────────────────────────────
async function renderFeedback(params = {}) {
  const { opId, paNr } = params;
  const el = document.getElementById("app-content");
  el.innerHTML = loadingHtml();
  let op, catalog;
  try {
    op      = await Api.operations.get(opId);
    catalog = await Api.quality.catalog(op.ag_nr);
  } catch (e) { el.innerHTML = alertHtml(e.message); return; }

  const mengeVorschlag = op.vorgaenger_menge_gut ?? op.auftrag_menge ?? 0;
  const vorschlagHinweis = op.vorgaenger_menge_gut != null
    ? `<small class="text-success ms-1">
         <i class="bi bi-arrow-left-circle"></i> übernommen von Vorgänger-AG (${op.vorgaenger_menge_gut} Stk.)</small>`
    : `<small class="text-muted ms-1">Auftragsmenge</small>`;

  // Maschinen-Dropdown für Rückmeldung (Fräs-AG)
  let maschinenHtml = "";
  if (op.ist_fraes_ag && op.maschinen_liste.length) {
    const opts = op.maschinen_liste.map(([nr, label]) =>
      `<option value="${nr}" ${op.maschine === nr ? "selected" : ""}>${nr} – ${label}</option>`
    ).join("");
    maschinenHtml = `
      <div class="col-md-3">
        <label class="form-label fw-bold">Maschine (Haas) <span class="text-danger">*</span></label>
        <select id="fb-maschine" class="form-select">
          <option value="">— wählen —</option>${opts}
        </select>
      </div>`;
  } else if (op.kapazitaet_fix) {
    // fix-AG: Kapazität schreibgeschützt anzeigen
    maschinenHtml = `
      <div class="col-md-3">
        <label class="form-label fw-bold">Kapazität</label>
        <input type="text" class="form-control bg-light"
               value="${op.kapazitaet_fix}" readonly>
      </div>`;
  } else {
    maschinenHtml = `
      <div class="col-md-3">
        <label class="form-label fw-bold">Maschine</label>
        <input type="text" id="fb-maschine" class="form-control"
               value="${esc(op.maschine ?? '')}">
      </div>`;
  }

  el.innerHTML = `
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h4 class="fw-bold mb-0">
        <i class="bi bi-pencil-square me-2"></i>Rückmeldung
        ${op.ag_nr_fmt} – PA ${esc(op.pa_nr)}
      </h4>
      <button class="btn btn-sm btn-outline-secondary"
        onclick="navigate('order',{paNr:'${esc(op.pa_nr)}'})">← Zurück</button>
    </div>
    <div class="alert alert-warning small py-2">
      <i class="bi bi-exclamation-triangle me-1"></i>
      <strong>Keine Nacharbeit.</strong> Alle Teile sind entweder gut oder Ausschuss.
    </div>
    <div class="card">
      <div class="card-header">
        ${esc(op.bezeichnung)}
        <span class="badge bg-secondary ms-2">Solldauer: ${op.solldauer_tage}T</span>
      </div>
      <div class="card-body">
        <div id="fb-alert" class="d-none"></div>
        <div class="row g-3">
          <div class="col-md-3">
            <label class="form-label fw-bold">
              Eingabemenge <span class="text-danger">*</span> ${vorschlagHinweis}
            </label>
            <input type="number" id="fb-input" class="form-control"
                   value="${mengeVorschlag}" min="1" oninput="calcMengen()">
          </div>
          <div class="col-md-2">
            <label class="form-label fw-bold">Ausschuss</label>
            <input type="number" id="fb-ausschuss" class="form-control"
                   value="0" min="0" oninput="calcMengen()">
          </div>
          <div class="col-md-2">
            <label class="form-label fw-bold">Gut-Menge</label>
            <input type="number" id="fb-gut" class="form-control bg-light" readonly>
          </div>
          <div class="col-md-3">
            <label class="form-label fw-bold">&nbsp;</label>
            <div id="fb-check" class="form-control bg-light text-center">—</div>
          </div>
          <div class="col-md-3">
            <label class="form-label fw-bold">Start Ist</label>
            <input type="datetime-local" id="fb-start_ist" class="form-control">
          </div>
          <div class="col-md-3">
            <label class="form-label fw-bold">Ende Ist</label>
            <input type="datetime-local" id="fb-ende_ist" class="form-control">
          </div>
          ${maschinenHtml}
          <div class="col-md-3">
            <label class="form-label fw-bold">Bemerkung</label>
            <input type="text" id="fb-bemerkung" class="form-control">
          </div>
        </div>
        <div class="mt-3">
          <label class="form-label fw-bold">Fehlercodes (bei Ausschuss > 0)</label>
          <div id="fehler-liste"></div>
          <button class="btn btn-sm btn-outline-secondary mt-1" onclick="addFehlerRow()">
            <i class="bi bi-plus me-1"></i>Fehlercode hinzufügen</button>
        </div>
        <div class="d-flex gap-2 mt-3">
          <button class="btn btn-primary" id="fb-save-btn"
                  onclick="saveFeedback(${opId},'${esc(op.pa_nr)}',${op.ist_fraes_ag})">
            <i class="bi bi-save me-1"></i>Rückmeldung speichern</button>
          <button class="btn btn-outline-secondary"
            onclick="navigate('order',{paNr:'${esc(op.pa_nr)}'})">Abbrechen</button>
        </div>
      </div>
    </div>`;

  window._currentCatalog = catalog;
  calcMengen();
}

function calcMengen() {
  const inp = parseInt(document.getElementById("fb-input")?.value)     || 0;
  const aus = parseInt(document.getElementById("fb-ausschuss")?.value) || 0;
  const gut = Math.max(0, inp - aus);
  const gutEl = document.getElementById("fb-gut");
  const chk   = document.getElementById("fb-check");
  if (gutEl) gutEl.value = gut;
  if (!chk) return;
  if (inp > 0 && (gut + aus) !== inp) {
    chk.style.background = "#f8d7da";
    chk.textContent = `⚠️ ${gut} + ${aus} ≠ ${inp}`;
  } else {
    chk.style.background = "#d1e7dd";
    chk.textContent = `✅ Gut: ${gut}  Ausschuss: ${aus}`;
  }
}

function addFehlerRow() {
  const catalog  = window._currentCatalog || {};
  const options  = Object.entries(catalog).map(([code, info]) =>
    `<option value="${code}">[${info.kategorie}] ${code} – ${esc(info.bezeichnung)}</option>`
  ).join("");
  const div = document.createElement("div");
  div.className = "d-flex gap-2 mb-1 align-items-center fehler-row";
  div.innerHTML = `
    <select class="form-select form-select-sm fehler-code" style="max-width:320px">
      <option value="">— Fehler wählen —</option>${options}
    </select>
    <input type="number" class="form-control form-control-sm fehler-menge"
           value="1" min="1" style="max-width:80px">
    <button class="btn btn-sm btn-outline-danger py-0"
            onclick="this.parentElement.remove()">
      <i class="bi bi-trash"></i></button>`;
  document.getElementById("fehler-liste").appendChild(div);
}

async function saveFeedback(opId, paNr, isFraesAg) {
  const btn   = document.getElementById("fb-save-btn");
  const alert = document.getElementById("fb-alert");
  btn.disabled = true;
  alert.className = "d-none";

  // Maschine: bei Fräs-AG aus Select, sonst aus Text-Input
  let maschine;
  if (isFraesAg) {
    const sel = document.getElementById("fb-maschine");
    maschine  = sel?.value || null;
  } else {
    maschine = document.getElementById("fb-maschine")?.value.trim() || null;
  }

  const fehler = [...document.querySelectorAll(".fehler-row")]
    .map(row => ({
      code:  row.querySelector(".fehler-code").value,
      menge: parseInt(row.querySelector(".fehler-menge").value) || 1,
    })).filter(f => f.code);

  const data = {
    menge_input:     parseInt(document.getElementById("fb-input").value)     || 0,
    menge_ausschuss: parseInt(document.getElementById("fb-ausschuss").value) || 0,
    start_ist:  document.getElementById("fb-start_ist")?.value || null,
    ende_ist:   document.getElementById("fb-ende_ist")?.value  || null,
    maschine, bemerkung: document.getElementById("fb-bemerkung")?.value.trim() || null,
    fehler,
  };

  try {
    const result = await Api.operations.feedback(opId, data);
    showToast(`✅ Gut: ${result.menge_gut}  Ausschuss: ${result.menge_ausschuss}`, "success");
    navigate("order", { paNr });
  } catch (e) {
    alert.className   = "alert alert-danger py-2";
    alert.textContent = e.message;
    btn.disabled = false;
  }
}

window.renderOpEdit = renderOpEdit;
window.renderFeedback = renderFeedback;