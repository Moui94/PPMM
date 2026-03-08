/**
 * schedule_haas.js — Kapazitätsplanung Haas-Maschinen
 */

async function renderHaasKapazitaet() {
  const el = document.getElementById("app-content");
  el.innerHTML = loadingHtml("Kapazitätsplanung wird berechnet...");
  let plan;
  try { plan = await Api.capacity.plan(); }
  catch (e) { el.innerHTML = alertHtml(e.message); return; }

  if (!plan.length) {
    el.innerHTML = `<div class="alert alert-info">Keine offenen Fräs-AGs vorhanden.</div>`;
    return;
  }

  // Nach Maschine gruppieren
  const byMaschine = {};
  for (const slot of plan) {
    if (!byMaschine[slot.maschinen_nr]) byMaschine[slot.maschinen_nr] = [];
    byMaschine[slot.maschinen_nr].push(slot);
  }

  const wechselBadge = (typ) => {
    const cfg = {
      "gleich":      ["success",  "Gleich"],
      "produkt":     ["warning",  "Produktwechsel"],
      "ag":          ["info",     "AG-Wechsel"],
      "ag+produkt":  ["danger",   "AG+Produkt"],
      "neu":         ["secondary","Neu"],
    };
    const [col, label] = cfg[typ] || ["secondary", typ];
    return `<span class="badge bg-${col} ms-1">${label}</span>`;
  };

  const prioBadge = (p) =>
    `<span class="badge badge-prio-${p} text-white">P${p}</span>`;

  const userRolle = window._userRolle || "ma";

  const maschineCards = Object.entries(byMaschine)
    .sort((a,b) => parseInt(a[0]) - parseInt(b[0]))
    .map(([nr, slots]) => {
      const rows = slots.map((s, idx) => `
        <tr>
          <td class="ps-2">${s.start_fmt}</td>
          <td>${s.ende_fmt}</td>
          <td class="fw-bold">${esc(s.pa_nr)}</td>
          <td>${s.ag_nr_fmt}</td>
          <td><small>${esc(s.artikel)}</small></td>
          <td class="text-center">${s.menge}</td>
          <td class="text-center">${s.solldauer_tage}T</td>
          <td>${prioBadge(s.prioritaet)}</td>
          <td>${wechselBadge(s.wechsel_typ)}</td>
          <td>
            ${userRolle !== "ma" ? `
            <button class="btn btn-sm btn-outline-success py-0"
              onclick="applySlot(${s.op_id},'${s.maschinen_nr}','${s.start_vorschlag}','${s.ende_vorschlag}')"
              title="Planung übernehmen">
              <i class="bi bi-check-lg"></i>
            </button>` : ""}
          </td>
        </tr>`).join("");

      return `
        <div class="card mb-3">
          <div class="card-header bg-dark text-white d-flex justify-content-between">
            <span><i class="bi bi-cpu me-2"></i><strong>Haas ${parseInt(nr)-2000 < 10 ? "0"+(parseInt(nr)-2000) : (parseInt(nr)-2000)}</strong>
              <small class="ms-2 text-muted">(${nr})</small></span>
            <span class="badge bg-secondary">${slots.length} Jobs</span>
          </div>
          <div class="card-body p-0">
            <table class="table table-sm table-hover mb-0">
              <thead class="table-light">
                <tr>
                  <th>Start</th><th>Ende</th><th>PA-Nr</th><th>AG</th>
                  <th>Artikel</th><th class="text-center">Menge</th>
                  <th class="text-center">Dauer</th><th>Prio</th>
                  <th>Wechsel</th><th></th>
                </tr>
              </thead>
              <tbody>${rows}</tbody>
            </table>
          </div>
        </div>`;
    }).join("");

  // Zusammenfassung
  const totalJobs    = plan.length;
  const totalWechsel = plan.filter(s => s.wechsel_typ !== "gleich" && s.wechsel_typ !== "neu").length;

  el.innerHTML = `
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h4 class="fw-bold mb-0">
        <i class="bi bi-diagram-3 me-2"></i>Kapazitätsplanung Haas-Maschinen
      </h4>
      <button class="btn btn-sm btn-outline-primary" onclick="renderHaasKapazitaet()">
        <i class="bi bi-arrow-clockwise me-1"></i>Neu berechnen
      </button>
    </div>
    <div class="row g-2 mb-3">
      <div class="col-auto">
        <span class="badge bg-primary fs-6">${totalJobs} Jobs geplant</span>
      </div>
      <div class="col-auto">
        <span class="badge bg-warning text-dark fs-6">${totalWechsel} Wechsel</span>
      </div>
      <div class="col-auto">
        <span class="badge bg-secondary fs-6">${Object.keys(byMaschine).length} Maschinen belegt</span>
      </div>
    </div>
    ${maschineCards}`;
}

async function applySlot(opId, maschinenNr, startVorschlag, endeVorschlag) {
  try {
    await Api.capacity.apply({
      op_id:           opId,
      maschinen_nr:    maschinenNr,
      start_vorschlag: startVorschlag,
      ende_vorschlag:  endeVorschlag,
    });
    showToast(`AG ${opId} → Haas ${maschinenNr} übernommen.`, "success");
    renderHaasKapazitaet(); // neu laden
  } catch (e) {
    showToast(e.message, "danger");
  }
}

window.renderHaasKapazitaet = renderHaasKapazitaet;
window.applySlot = applySlot;
