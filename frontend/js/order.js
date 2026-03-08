/**
 * order.js – Auftragsdetail, Anlegen (Dropdown + Ceramaret), Bearbeiten.
 */

async function renderOrder(params = {}) {
  const { paNr } = params;
  const el = document.getElementById("app-content");
  el.innerHTML = loadingHtml();
  let order, ops;
  try {
    [order, ops] = await Promise.all([Api.orders.get(paNr), Api.orders.ops(paNr)]);
  } catch (e) { el.innerHTML = alertHtml(e.message); return; }

  const abw      = order.abweichung_tage;
  const abwClass = abw > 0 ? "abw-pos" : abw < 0 ? "abw-neg" : "abw-null";
  const abwStr   = (abw > 0 ? "+" : "") + abw + "T";

  const opRows = ops.map(op => {
    const sc  = {offen:"ag-open", laufend:"ag-active", abgeschlossen:"ag-done"}[op.status] ?? "ag-open";
    const fb  = op.latest_feedback;
    const fbHtml = fb
      ? `<span class="badge bg-success">${fb.menge_gut} gut</span>
         <span class="badge bg-danger ms-1">${fb.menge_ausschuss} Ausschuss</span>`
      : "";
    const editBtn = hasRole("admin","pl")
      ? `<button class="btn btn-sm btn-outline-secondary py-0 ms-1"
           onclick="navigate('op-edit',{opId:${op.id},paNr:'${paNr}'})">
           <i class="bi bi-gear"></i></button>` : "";
    return `<tr class="${sc} ag-row">
      <td class="ps-2 fw-bold">${op.ag_nr_fmt}</td>
      <td>${esc(op.bezeichnung)}</td>
      <td class="text-center"><span class="badge bg-secondary">${op.solldauer_tage}T</span></td>
      <td>${op.start_soll_fmt}</td><td>${op.ende_soll_fmt}</td>
      <td>${esc(op.maschine||"—")}</td>
      <td>${op.start_ist ? op.start_ist.substring(0,10) : "—"}</td>
      <td>${op.ende_ist  ? op.ende_ist.substring(0,10)  : "—"}</td>
      <td>${fbHtml}</td>
      <td>
        <button class="btn btn-sm btn-outline-primary py-0"
                onclick="navigate('feedback',{opId:${op.id},paNr:'${paNr}'})">
          <i class="bi bi-pencil-square"></i></button>${editBtn}
      </td>
    </tr>`;
  }).join("");

  const ceramaretBadge = order.ceramaret
    ? `<span class="badge bg-warning text-dark ms-1"><i class="bi bi-stars me-1"></i>Ceramaret</span>` : "";

  el.innerHTML = `
    <div class="d-flex justify-content-between align-items-center mb-3">
      <div>
        <h4 class="fw-bold mb-0">
          <i class="bi bi-file-earmark-text me-2"></i>PA ${esc(order.pa_nr)}
          <span class="badge bg-${order.art==='I'?'primary':'info'} ms-2">${order.art_label}</span>
          <span class="badge badge-prio-${order.prioritaet} text-white ms-1">P${order.prioritaet}</span>
          ${ceramaretBadge}
        </h4>
        <small class="text-muted">${esc(order.artikel)}</small>
      </div>
      <div class="d-flex gap-2">
        ${hasRole("admin","pl") ? `<button class="btn btn-sm btn-outline-secondary"
          onclick="navigate('order-edit',{paNr:'${paNr}'})">
          <i class="bi bi-pencil me-1"></i>Bearbeiten</button>` : ""}
        <button class="btn btn-sm btn-outline-dark" onclick="navigate('dashboard')">← Zurück</button>
      </div>
    </div>

    <div class="card mb-3">
      <div class="card-body">
        <div class="row g-2">
          ${detailItem("Artikel",         esc(order.artikel))}
          ${detailItem("Menge",           order.menge)}
          ${detailItem("PA-Start",        order.pa_start_fmt)}
          ${detailItem("Endtermin Soll",  `<strong>${order.endtermin_soll_fmt}</strong>`)}
          ${detailItem("Lieferung Kunde", order.auslieferung_fmt)}
          ${detailItem("Abweichung",      `<span class="${abwClass}">${abwStr}</span>`)}
          ${detailItem("Haas-Nr",         esc(order.haas_nr||"—"))}
          ${detailItem("Status",          `<span class="badge bg-primary">${order.status}</span>`)}
        </div>
        ${order.spezielles ? `<div class="mt-2"><span class="badge bg-warning text-dark">
          <i class="bi bi-exclamation-triangle me-1"></i>${esc(order.spezielles)}</span></div>` : ""}
      </div>
    </div>

    <div class="card">
      <div class="card-header bg-dark text-white">
        Arbeitsgänge <span class="badge bg-secondary ms-2">${ops.length} AGs</span>
        ${order.ceramaret ? '<span class="badge bg-warning text-dark ms-1">AG01 entfällt (Ceramaret)</span>' : ""}
      </div>
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-sm mb-0">
            <thead class="table-secondary">
              <tr>
                <th>AG</th><th>Bezeichnung</th><th class="text-center">Solldauer</th>
                <th>Start Soll</th><th>Ende Soll</th><th>Maschine</th>
                <th>Start Ist</th><th>Ende Ist</th><th>Rückmeldung</th><th></th>
              </tr>
            </thead>
            <tbody>${opRows}</tbody>
          </table>
        </div>
      </div>
    </div>`;
}

function detailItem(label, value) {
  return `<div class="col-6 col-md-2">
    <div class="text-muted small">${label}</div><div>${value}</div></div>`;
}

// ── Neuer Auftrag ─────────────────────────────────────────────────────────────
function renderOrderNew() { renderOrderForm(null); }

async function renderOrderEdit(params = {}) {
  const el = document.getElementById("app-content");
  el.innerHTML = loadingHtml();
  try {
    const order = await Api.orders.get(params.paNr);
    renderOrderForm(order);
  } catch (e) { el.innerHTML = alertHtml(e.message); }
}

async function renderOrderForm(order = null) {
  const isNew = !order;
  const el    = document.getElementById("app-content");

  // Produktliste laden
  let produkte = {};
  const menge0 = order?.menge || 0;
  try { produkte = await Api.orders.produkte(null, menge0);
        window._produkteCache = produkte; }
  catch (e) { el.innerHTML = alertHtml("Produkte konnten nicht geladen werden: " + e.message); return; }

  // Dropdown nach Art gruppieren
  const abutments  = Object.entries(produkte).filter(([,v]) => v.art === "A");
  const implantate = Object.entries(produkte).filter(([,v]) => v.art === "I");

  const produktOptionen = (art) => {
    const list = art === "A" ? abutments : implantate;
    return list.map(([artikel, info]) =>
      `<option value="${artikel}" data-ceramaret="${info.ceramaret_moeglich}"
        ${order?.artikel === artikel ? "selected" : ""}>${artikel}</option>`
    ).join("");
  };

  const currentArt = order?.art ?? "A";

  el.innerHTML = `
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h4 class="fw-bold mb-0">
        <i class="bi bi-${isNew?'plus-circle':'pencil'} me-2"></i>
        ${isNew ? "Neuer Auftrag" : "Auftrag " + esc(order.pa_nr) + " bearbeiten"}
      </h4>
      <button class="btn btn-sm btn-outline-secondary"
        onclick="${isNew ? "navigate('dashboard')" : "navigate('order',{paNr:'"+order?.pa_nr+"'})"}">
        ← Zurück</button>
    </div>
    <div class="card">
      <div class="card-body">
        <div id="form-alert" class="d-none"></div>
        <div class="row g-3">

          ${isNew ? `
          <!-- PA-Nr -->
          <div class="col-md-3">
            <label class="form-label fw-bold">PA-Nr <span class="text-danger">*</span></label>
            <input type="text" id="f-pa_nr" class="form-control" placeholder="z.B. 7700" required>
          </div>

          <!-- Typ-Auswahl -->
          <div class="col-md-2">
            <label class="form-label fw-bold">Typ <span class="text-danger">*</span></label>
            <select id="f-art" class="form-select" onchange="onArtChange()" required>
              <option value="A" ${currentArt==='A'?'selected':''}>A – Abutment</option>
              <option value="I" ${currentArt==='I'?'selected':''}>I – Implantat</option>
            </select>
          </div>

          <!-- Artikel-Dropdown -->
          <div class="col-md-4">
            <label class="form-label fw-bold">Artikel <span class="text-danger">*</span></label>
            <select id="f-artikel" class="form-select" onchange="onArtikelChange()" required>
              <option value="">— Artikel wählen —</option>
              <optgroup label="Abutments (A)" id="opt-A">${produktOptionen("A")}</optgroup>
              <optgroup label="Implantate (I)" id="opt-I">${produktOptionen("I")}</optgroup>
            </select>
          </div>` :

          /* Edit-Modus: Artikel anzeigen (nicht änderbar) */
          `<div class="col-md-4">
            <label class="form-label fw-bold">Artikel</label>
            <input type="text" class="form-control bg-light"
                   value="${esc(order?.artikel??'')}" readonly>
          </div>`}

          <!-- Ceramaret Toggle (nur sichtbar wenn möglich) -->
          <div class="col-md-3" id="ceramaret-wrapper" style="display:none">
            <label class="form-label fw-bold">Ceramaret</label>
            <div class="form-check form-switch mt-2">
              <input class="form-check-input" type="checkbox" id="f-ceramaret"
                     role="switch" ${order?.ceramaret ? "checked" : ""}
                     onchange="onCameraretChange()">
              <label class="form-check-label" id="ceramaret-label">
                ${order?.ceramaret
                  ? '<span class="text-warning fw-bold"><i class="bi bi-stars me-1"></i>Ceramaret (AG01 entfällt)</span>'
                  : 'Standard'}
              </label>
            </div>
          </div>

          <!-- Menge -->
          <div class="col-md-2">
            <label class="form-label fw-bold">Menge <span class="text-danger">*</span></label>
            <input type="number" id="f-menge" class="form-control"
                   value="${order?.menge??''}" min="1" required
                   oninput="updateAgVorschau()">
          </div>

          <!-- Priorität -->
          <div class="col-md-2">
            <label class="form-label fw-bold">Priorität</label>
            <select id="f-prioritaet" class="form-select">
              ${[1,2,3].map(p => `<option value="${p}" ${(order?.prioritaet??2)==p?"selected":""}>${p} – ${["","Hoch","Mittel","Tief"][p]}</option>`).join("")}
            </select>
          </div>

          ${isNew ? `
          <div class="col-md-3">
            <label class="form-label fw-bold">PA-Start</label>
            <input type="date" id="f-pa_start" class="form-control">
          </div>` : ""}

          <div class="col-md-3">
            <label class="form-label fw-bold">Auslieferung Kunde</label>
            <input type="date" id="f-auslieferung_kunde" class="form-control"
                   value="${order?.auslieferung_kunde??''}">
          </div>

          <div class="col-md-2">
            <label class="form-label fw-bold">Status</label>
            <select id="f-status" class="form-select">
              ${["geplant","aktiv","abgeschlossen","archiviert"].map(s =>
                `<option value="${s}" ${(order?.status??'geplant')===s?"selected":""}>${cap(s)}</option>`
              ).join("")}
            </select>
          </div>

          <div class="col-md-2">
            <label class="form-label fw-bold">Haas-Nr</label>
            <input type="text" id="f-haas_nr" class="form-control"
                   value="${esc(order?.haas_nr??'')}">
          </div>

          <div class="col-md-3">
            <label class="form-label fw-bold">Spezielles</label>
            <input type="text" id="f-spezielles" class="form-control"
                   value="${esc(order?.spezielles??'')}">
          </div>

          <div class="col-12">
            <label class="form-label fw-bold">Bemerkung</label>
            <textarea id="f-bemerkung" class="form-control" rows="2">${esc(order?.bemerkung??'')}</textarea>
          </div>
        </div>

        ${isNew ? `
        <div id="ag-vorschau" class="alert alert-info mt-3 small" style="display:none">
          <strong><i class="bi bi-list-check me-1"></i>AG-Vorschau:</strong>
          <span id="ag-vorschau-text"></span>
        </div>` : ""}

        <div class="d-flex gap-2 mt-3">
          <button class="btn btn-primary" id="save-btn"
                  onclick="saveOrder('${isNew?'new':order?.pa_nr}')">
            <i class="bi bi-save me-1"></i>${isNew?"Auftrag anlegen":"Speichern"}</button>
          <button class="btn btn-outline-secondary"
            onclick="${isNew?"navigate('dashboard')":"navigate('order',{paNr:'"+order?.pa_nr+"'})"}">
            Abbrechen</button>
        </div>
      </div>
    </div>`;

  // Initiale Sichtbarkeit anpassen
  if (isNew) {
    onArtChange();
    if (order?.ceramaret_moeglich) {
      document.getElementById("ceramaret-wrapper").style.display = "";
    }
  } else if (order) {
    // Edit: Ceramaret-Wrapper nur zeigen wenn möglich
    if (isNew === false) {
      // Im Edit-Modus nicht änderbar — nur anzeigen
    }
  }
}

// Art-Wechsel → Dropdown filtern
function onArtChange() {
  const art = document.getElementById("f-art")?.value;
  if (!art) return;
  const sel = document.getElementById("f-artikel");
  if (!sel) return;
  sel.value = "";
  // Optgroups ein-/ausblenden
  document.querySelectorAll("#f-artikel optgroup").forEach(og => {
    og.style.display = og.id === `opt-${art}` ? "" : "none";
    og.querySelectorAll("option").forEach(o => {
      o.disabled = og.id !== `opt-${art}`;
    });
  });
  // Ceramaret ausblenden bis Artikel gewählt
  document.getElementById("ceramaret-wrapper").style.display = "none";
  document.getElementById("f-ceramaret").checked = false;
  updateAgVorschau();
}

// Artikel-Wechsel → Ceramaret-Toggle anzeigen/ausblenden
function onArtikelChange() {
  const sel    = document.getElementById("f-artikel");
  const opt    = sel?.options[sel.selectedIndex];
  const moegl  = opt?.dataset?.ceramaret === "true";
  const wrap   = document.getElementById("ceramaret-wrapper");
  const chk    = document.getElementById("f-ceramaret");
  if (wrap) wrap.style.display = moegl ? "" : "none";
  if (!moegl && chk) chk.checked = false;
  // Produkte neu laden mit aktueller Menge für korrekte Solldauer
  const m = parseInt(document.getElementById('f-menge')?.value) || 0;
  if (m > 0) {
    Api.orders.produkte(null, m).then(p => {
      window._produkteCache = p;
      updateAgVorschau();
    });
  }
  onCameraretChange();
  updateAgVorschau();
}

// Ceramaret-Toggle → Label + AG-Vorschau aktualisieren
function onCameraretChange() {
  const chk   = document.getElementById("f-ceramaret");
  const label = document.getElementById("ceramaret-label");
  if (!chk || !label) return;
  label.innerHTML = chk.checked
    ? '<span class="text-warning fw-bold"><i class="bi bi-stars me-1"></i>Ceramaret (AG01 entfällt)</span>'
    : 'Standard';
  updateAgVorschau();
}

function updateAgVorschau() {
  const vorschau = document.getElementById("ag-vorschau");
  const txt      = document.getElementById("ag-vorschau-text");
  const artikel  = document.getElementById("f-artikel")?.value;
  const ceramaret= document.getElementById("f-ceramaret")?.checked;
  const menge    = parseInt(document.getElementById("f-menge")?.value) || 0;
  if (!vorschau || !txt || !artikel) {
    if (vorschau) vorschau.style.display = "none";
    return;
  }
  const pInfo = window._produkteCache?.[artikel];
  if (!pInfo) { vorschau.style.display = "none"; return; }

  const seq      = ceramaret ? pInfo.ag_sequenz_ceramaret : pInfo.ag_sequenz;
  const dauern   = pInfo.fraes_solldauern || {};
  const ausbrgMap = pInfo.ausbringung_pro_ag || {};

  // Solldauern für Fräs-AGs berechnen (pro AG eigene Ausbringung)
  const fraesBerechnet = {};
  if (menge > 0) {
    for (const agNr of [1,2,3]) {
      if (seq.includes(agNr)) {
        const ausbrg = ausbrgMap[agNr] || 26;
        fraesBerechnet[agNr] = Math.ceil(menge / ausbrg);
      }
    }
  }

  txt.innerHTML = seq.map(n => {
    const ag  = `AG${String(n).padStart(2,'0')}`;
    const dauer = n <= 3
      ? (fraesBerechnet[n] ? `<strong>${fraesBerechnet[n]}T</strong>` : "")
      : "";
    return dauer ? `${ag}(${dauer})` : ag;
  }).join(" → ");
  vorschau.style.display = "";
}

async function saveOrder(mode) {
  const btn   = document.getElementById("save-btn");
  const alert = document.getElementById("form-alert");
  btn.disabled = true;
  alert.className = "d-none";

  const data = {
    menge:              parseInt(document.getElementById("f-menge")?.value),
    prioritaet:         parseInt(document.getElementById("f-prioritaet")?.value),
    auslieferung_kunde: document.getElementById("f-auslieferung_kunde")?.value || null,
    status:             document.getElementById("f-status")?.value,
    haas_nr:            document.getElementById("f-haas_nr")?.value?.trim()     || null,
    spezielles:         document.getElementById("f-spezielles")?.value?.trim()  || null,
    bemerkung:          document.getElementById("f-bemerkung")?.value?.trim()   || null,
  };

  try {
    if (mode === "new") {
      data.pa_nr    = document.getElementById("f-pa_nr")?.value.trim();
      data.artikel  = document.getElementById("f-artikel")?.value;
      data.ceramaret= document.getElementById("f-ceramaret")?.checked ?? false;
      data.pa_start = document.getElementById("f-pa_start")?.value || null;
      if (!data.pa_nr)   throw new Error("PA-Nr ist Pflichtfeld.");
      if (!data.artikel) throw new Error("Bitte Artikel auswählen.");
      await Api.orders.create(data);
      showToast(`Auftrag ${data.pa_nr} erfolgreich angelegt.`, "success");
      navigate("order", { paNr: data.pa_nr });
    } else {
      await Api.orders.update(mode, data);
      showToast(`Auftrag ${mode} gespeichert.`, "success");
      navigate("order", { paNr: mode });
    }
  } catch (e) {
    alert.className   = "alert alert-danger py-2";
    alert.textContent = e.message;
    btn.disabled = false;
  }
}
