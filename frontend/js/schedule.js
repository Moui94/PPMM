/**
 * schedule.js – Fräsplanung Dashboard (AG01–AG03 Maschinenübersicht).
 */

async function renderSchedule(params = {}) {
  const agNr = params.ag || 1;
  const el   = document.getElementById("app-content");
  el.innerHTML = loadingHtml("Fräsplan wird geladen...");

  // Aufträge laden die AG offen/laufend haben
  let orders;
  try { orders = await Api.orders.list({ status: "aktiv" }); }
  catch (e) { el.innerHTML = alertHtml(e.message); return; }

  // Ops für alle aktiven Aufträge laden und nach AG + Maschine gruppieren
  const machineMap = {};  // { "Haas 2001": [slotObj, ...] }

  await Promise.all(orders.map(async (o) => {
    try {
      const ops = await Api.orders.ops(o.pa_nr);
      const agOp = ops.find(op => op.ag_nr === agNr);
      if (!agOp) return;
      const maschine = agOp.maschine || "Nicht zugewiesen";
      if (!machineMap[maschine]) machineMap[maschine] = [];
      machineMap[maschine].push({
        pa_nr:      o.pa_nr,
        artikel:    o.artikel,
        menge:      o.menge,
        prioritaet: o.prioritaet,
        status:     agOp.status,
        start_soll: agOp.start_soll_fmt,
        ende_soll:  agOp.ende_soll_fmt,
        solldauer:  agOp.solldauer_tage,
        op_id:      agOp.id,
      });
    } catch {}
  }));

  // Maschinen-Kacheln
  const machineCards = Object.entries(machineMap).map(([maschine, slots]) => {
    const hasActive = slots.some(s => s.status === "laufend");
    const cardClass = hasActive ? "busy" : "free";
    const slotHtml  = slots.map(s => {
      const sc = s.status === "abgeschlossen" ? "slot-done"
               : s.status === "laufend" ? "slot-active" : "slot-planned";
      return `<div class="slot-item ${sc}">
        <strong>${esc(s.pa_nr)}</strong> – ${esc(s.artikel)}
        <span class="float-end text-muted">${s.solldauer}T</span><br>
        <small>${s.start_soll} → ${s.ende_soll}</small>
        <span class="badge badge-prio-${s.prioritaet} text-white ms-1 float-end">P${s.prioritaet}</span>
      </div>`;
    }).join("");
    return `<div class="col-md-3 col-sm-6 mb-3">
      <div class="machine-card ${cardClass}">
        <div class="d-flex justify-content-between align-items-center mb-2">
          <strong>${esc(maschine)}</strong>
          <span class="badge bg-${hasActive?'warning text-dark':'success'}">${hasActive?'Aktiv':'Frei'}</span>
        </div>
        <div class="small text-muted mb-1">${slots.length} Auftrag/Aufträge</div>
        ${slotHtml || '<div class="text-muted small">Keine Aufträge</div>'}
      </div>
    </div>`;
  }).join("");

  // AG-Tabs
  const agTabs = [1,2,3].map(n => `
    <li class="nav-item">
      <a class="nav-link ${agNr===n?'active':''}" href="#"
         onclick="navigate('schedule',{ag:${n}})">AG0${n}</a>
    </li>`).join("");

  el.innerHTML = `
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h4 class="fw-bold mb-0">
        <i class="bi bi-diagram-3 me-2"></i>Fräsplanung AG0${agNr}
      </h4>
      <small class="text-muted" id="sched-refresh-info">
        Automatisch aktualisiert <span id="sched-countdown">60</span>s
      </small>
    </div>

    <!-- AG-Tabs -->
    <ul class="nav nav-tabs mb-3">${agTabs}</ul>

    <!-- Legende -->
    <div class="d-flex gap-3 mb-3 small">
      <span><span style="background:#fff3cd;display:inline-block;width:12px;height:12px;border-radius:2px"></span> In Bearbeitung</span>
      <span><span style="background:#e3f0ff;display:inline-block;width:12px;height:12px;border-radius:2px"></span> Geplant</span>
      <span><span style="background:#d1f0db;display:inline-block;width:12px;height:12px;border-radius:2px"></span> Abgeschlossen</span>
    </div>

    <!-- Maschinenkacheln -->
    <div class="row" id="machine-grid">
      ${machineCards || '<div class="col-12"><div class="alert alert-info">Keine aktiven Aufträge für AG0'+agNr+' gefunden.</div></div>'}
    </div>`;

  // Auto-Refresh
  startScheduleCountdown(agNr);
}

let schedCountdownTimer = null;

function startScheduleCountdown(agNr) {
  if (schedCountdownTimer) clearInterval(schedCountdownTimer);
  let seconds = 60;
  const el = document.getElementById("sched-countdown");
  schedCountdownTimer = setInterval(() => {
    seconds--;
    if (el) el.textContent = seconds;
    if (seconds <= 0) {
      clearInterval(schedCountdownTimer);
      renderSchedule({ ag: agNr });
    }
  }, 1000);
}

window.renderSchedule = renderSchedule;