/**
 * dashboard.js – Auftragsübersicht mit KPIs, Filter, Tabelle.
 */

const STATUS_BADGE = {
  geplant:       "secondary",
  aktiv:         "primary",
  abgeschlossen: "success",
  archiviert:    "dark",
};

async function renderDashboard(params = {}) {
  const el = document.getElementById("app-content");
  el.innerHTML = loadingHtml("Aufträge werden geladen...");

  let kpis = {}, orders = [];
  const filters = {
    status: params.status ?? "aktiv",
    art:    params.art    ?? "",
    prio:   params.prio   ?? "",
    q:      params.q      ?? "",
  };

  try {
    [kpis, orders] = await Promise.all([Api.orders.kpis(), Api.orders.list(filters)]);
  } catch (e) { showToast(e.message, "danger"); el.innerHTML = alertHtml(e.message); return; }

  const orderRows = orders.map(o => {
    const abwClass = o.abweichung_tage > 0 ? "abw-pos" : o.abweichung_tage < 0 ? "abw-neg" : "abw-null";
    const abwStr   = (o.abweichung_tage > 0 ? "+" : "") + o.abweichung_tage + "T";
    const prog     = o.progress?.percent ?? 0;
    const progBar  = `<div class="progress" style="height:16px;min-width:80px">
      <div class="progress-bar bg-${prog===100?"success":"primary"}" style="width:${prog}%">${prog}%</div></div>`;
    const editBtn  = hasRole("admin","pl")
      ? `<button class="btn btn-sm btn-outline-secondary py-0 ms-1" onclick="navigate('order-edit',{paNr:'${o.pa_nr}'})">
           <i class="bi bi-pencil"></i></button>` : "";
    return `<tr>
      <td><a href="#" class="fw-bold text-decoration-none" onclick="navigate('order',{paNr:'${o.pa_nr}'})">${o.pa_nr}</a></td>
      <td><span class="badge bg-${o.art==='I'?'primary':'info'}">${o.art_label}</span></td>
      <td>${esc(o.artikel)}</td>
      <td class="text-center">${o.menge}</td>
      <td class="text-center"><span class="badge badge-prio-${o.prioritaet} text-white">P${o.prioritaet}</span></td>
      <td>${o.endtermin_soll_fmt}</td>
      <td>${o.auslieferung_fmt}</td>
      <td class="text-center ${abwClass}">${abwStr}</td>
      <td>${progBar}</td>
      <td><span class="badge bg-${STATUS_BADGE[o.status]??'secondary'}">${o.status}</span></td>
      <td>
        <button class="btn btn-sm btn-outline-primary py-0" onclick="navigate('order',{paNr:'${o.pa_nr}'})">
          <i class="bi bi-eye"></i></button>${editBtn}
      </td>
    </tr>`;
  }).join("");

  el.innerHTML = `
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h4 class="fw-bold mb-0"><i class="bi bi-grid-3x3-gap me-2"></i>Auftragsübersicht</h4>
      ${hasRole("admin","pl") ? `<button class="btn btn-primary btn-sm" onclick="navigate('order-new')">
        <i class="bi bi-plus-circle me-1"></i>Neuer Auftrag</button>` : ""}
    </div>

    <!-- KPIs -->
    <div class="row g-2 mb-3">
      ${kpiCard(kpis.aktiv,      "Aktive Aufträge",    "primary")}
      ${kpiCard(kpis.geplant,    "Geplante Aufträge",  "secondary")}
      ${kpiCard(kpis.verzug,     "In Verzug",          "danger")}
      ${kpiCard(kpis.abgeschlossen,"Abgeschlossen",    "success")}
    </div>

    <!-- Filter -->
    <div class="card mb-3">
      <div class="card-body py-2">
        <div class="row g-2 align-items-end">
          <div class="col-auto">
            <input type="text" id="f-q" class="form-control form-control-sm"
                   placeholder="PA-Nr / Artikel" value="${esc(filters.q)}">
          </div>
          <div class="col-auto">
            <select id="f-status" class="form-select form-select-sm">
              <option value="">Alle Status</option>
              ${["geplant","aktiv","abgeschlossen","archiviert"].map(s=>
                `<option value="${s}" ${filters.status===s?"selected":""}>${cap(s)}</option>`).join("")}
            </select>
          </div>
          <div class="col-auto">
            <select id="f-art" class="form-select form-select-sm">
              <option value="">Alle Typen</option>
              <option value="A" ${filters.art==="A"?"selected":""}>Abutment</option>
              <option value="I" ${filters.art==="I"?"selected":""}>Implantat</option>
            </select>
          </div>
          <div class="col-auto">
            <select id="f-prio" class="form-select form-select-sm">
              <option value="">Alle Prioritäten</option>
              <option value="1" ${filters.prio==="1"?"selected":""}>P1 – Hoch</option>
              <option value="2" ${filters.prio==="2"?"selected":""}>P2 – Mittel</option>
              <option value="3" ${filters.prio==="3"?"selected":""}>P3 – Tief</option>
            </select>
          </div>
          <div class="col-auto">
            <button class="btn btn-sm btn-primary" onclick="applyDashboardFilter()">
              <i class="bi bi-funnel"></i> Filtern</button>
            <button class="btn btn-sm btn-outline-secondary ms-1" onclick="navigate('dashboard')">Reset</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabelle -->
    <div class="card">
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-orders table-hover table-sm mb-0">
            <thead class="table-dark">
              <tr>
                <th>PA-Nr</th><th>Typ</th><th>Artikel</th>
                <th class="text-center">Menge</th><th class="text-center">Prio</th>
                <th>Endtermin Soll</th><th>Lieferung Kunde</th>
                <th class="text-center">Abw.</th><th>Fortschritt</th>
                <th>Status</th><th></th>
              </tr>
            </thead>
            <tbody>${orderRows || '<tr><td colspan="11" class="text-center text-muted py-4">Keine Aufträge gefunden.</td></tr>'}</tbody>
          </table>
        </div>
      </div>
    </div>`;
}

function applyDashboardFilter() {
  navigate("dashboard", {
    status: document.getElementById("f-status").value,
    art:    document.getElementById("f-art").value,
    prio:   document.getElementById("f-prio").value,
    q:      document.getElementById("f-q").value.trim(),
  });
}

function kpiCard(value, label, color) {
  return `<div class="col-6 col-md-3">
    <div class="card p-3 text-center kpi-card">
      <div class="fs-2 fw-bold text-${color}">${value ?? 0}</div>
      <div class="text-muted small">${label}</div>
    </div></div>`;
}

window.renderDashboard = renderDashboard;