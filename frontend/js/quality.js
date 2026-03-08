/**
 * quality.js – Qualitäts-Dashboard und Fehlerkatalog.
 */

async function renderQuality() {
  const el = document.getElementById("app-content");
  el.innerHTML = loadingHtml("Qualitätsdaten werden geladen...");
  let pareto;
  try { pareto = await Api.quality.pareto(null, 10); }
  catch (e) { el.innerHTML = alertHtml(e.message); return; }

  const maxMenge = pareto[0]?.total_menge || 1;
  const paretoRows = pareto.map((f, i) => `
    <tr>
      <td>${i+1}</td>
      <td><span class="badge bg-secondary">${f.fehler_code}</span></td>
      <td>${esc(f.bezeichnung)}</td>
      <td class="text-center">${f.kategorie}</td>
      <td class="text-center fw-bold">${f.total_menge}</td>
      <td style="min-width:140px">
        <div class="pareto-bar" style="width:${Math.round(f.total_menge/maxMenge*100)}%"></div>
      </td>
      <td class="text-center">${f.anteil_pct}%</td>
    </tr>`).join("");

  el.innerHTML = `
    <h4 class="fw-bold mb-3"><i class="bi bi-shield-check me-2"></i>Qualitäts-Dashboard</h4>

    <!-- Pareto AG-Filter -->
    <div class="card mb-3">
      <div class="card-body py-2 d-flex align-items-center gap-2">
        <label class="form-label mb-0 fw-bold">AG-Filter:</label>
        <select id="pareto-ag" class="form-select form-select-sm" style="max-width:180px"
                onchange="reloadPareto()">
          <option value="">Alle AGs</option>
          ${Array.from({length:14},(_,i)=>`<option value="${i+1}">AG${String(i+1).padStart(2,'0')}</option>`).join("")}
        </select>
        <span class="text-muted small ms-2">Top-10 Ausschussgründe</span>
      </div>
    </div>

    <!-- Pareto Tabelle -->
    <div class="card">
      <div class="card-header bg-dark text-white">Top-10 Fehlercodes</div>
      <div class="card-body p-0">
        <table class="table table-sm mb-0" id="pareto-table">
          <thead class="table-secondary">
            <tr>
              <th>#</th><th>Code</th><th>Bezeichnung</th>
              <th class="text-center">Kat.</th>
              <th class="text-center">Menge</th>
              <th>Anteil</th>
              <th class="text-center">%</th>
            </tr>
          </thead>
          <tbody>${paretoRows || '<tr><td colspan="7" class="text-center text-muted py-3">Keine Daten.</td></tr>'}</tbody>
        </table>
      </div>
    </div>`;
}

async function reloadPareto() {
  const agNr = document.getElementById("pareto-ag")?.value || null;
  const maxMenge_ref = { val: 1 };
  try {
    const pareto = await Api.quality.pareto(agNr ? parseInt(agNr) : null, 10);
    const maxMenge = pareto[0]?.total_menge || 1;
    const rows = pareto.map((f, i) => `
      <tr>
        <td>${i+1}</td>
        <td><span class="badge bg-secondary">${f.fehler_code}</span></td>
        <td>${esc(f.bezeichnung)}</td>
        <td class="text-center">${f.kategorie}</td>
        <td class="text-center fw-bold">${f.total_menge}</td>
        <td style="min-width:140px">
          <div class="pareto-bar" style="width:${Math.round(f.total_menge/maxMenge*100)}%"></div>
        </td>
        <td class="text-center">${f.anteil_pct}%</td>
      </tr>`).join("");
    const tbody = document.querySelector("#pareto-table tbody");
    if (tbody) tbody.innerHTML = rows || '<tr><td colspan="7" class="text-center text-muted py-3">Keine Daten.</td></tr>';
  } catch (e) { showToast(e.message, "danger"); }
}

async function renderCatalog() {
  const el = document.getElementById("app-content");
  el.innerHTML = loadingHtml();
  let catalog;
  try { catalog = await Api.quality.catalog(); }
  catch (e) { el.innerHTML = alertHtml(e.message); return; }

  const KAT_COLORS = {M:"primary",O:"info",P:"warning",H:"secondary",Q:"success",S:"dark"};
  const rows = Object.entries(catalog).map(([code, info]) => `
    <tr>
      <td><span class="badge bg-secondary">${code}</span></td>
      <td>${esc(info.bezeichnung)}</td>
      <td><span class="badge bg-${KAT_COLORS[info.kategorie]??'secondary'}">${info.kategorie}</span></td>
    </tr>`).join("");

  el.innerHTML = `
    <h4 class="fw-bold mb-3"><i class="bi bi-journal-text me-2"></i>Fehlerkatalog</h4>
    <div class="card">
      <div class="card-body p-0">
        <table class="table table-sm mb-0">
          <thead class="table-dark">
            <tr><th>Code</th><th>Bezeichnung</th><th>Kategorie</th></tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
    </div>
    <div class="alert alert-info small mt-3">
      <strong>Kategorien:</strong>
      M = Masse &nbsp;|&nbsp; O = Optik &nbsp;|&nbsp; P = Prozess &nbsp;|&nbsp;
      H = Handling &nbsp;|&nbsp; Q = Qualität &nbsp;|&nbsp; S = Sonstiges
    </div>`;
}

window.renderQuality = renderQuality;