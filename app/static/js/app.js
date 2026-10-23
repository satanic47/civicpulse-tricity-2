
function onInputFeedback() {
  const el = document.getElementById('rawInput');
  const countEl = document.getElementById('charCount');
  const warningEl = document.getElementById('hazardWarning');
  if (!el) return;

  const val = el.value || '';
  if (countEl) countEl.textContent = `${val.length} / 2500`;

  const lower = val.toLowerCase();
  const hazardKeywords = ['wire', 'spark', 'shock', 'accident', 'burst', 'overflow', 'fire', 'current', 'death', 'hospital', 'school', 'danger', 'ਤਾਰਾਂ', 'ਫਟ', 'ਕਰੰਟ', 'ਖ਼ਤਰਾ', 'तार', 'करंट', 'खतरा'];
  const hasHazard = hazardKeywords.some(kw => lower.includes(kw));

  if (warningEl) {
    if (hasHazard) {
      warningEl.classList.remove('hidden');
    } else {
      warningEl.classList.add('hidden');
    }
  }
}

function showToast(title, message, type = 'success') {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const toast = document.createElement('div');
  const isErr = type === 'error';
  const borderCol = isErr ? 'border-rose-500' : 'border-emerald-500';
  const bgCol = isErr ? 'bg-rose-950/95 text-rose-200' : 'bg-slate-900/95 text-slate-100';
  const icon = isErr ? 'fa-circle-xmark text-rose-400' : 'fa-circle-check text-emerald-400';

  toast.className = `pointer-events-auto flex items-start gap-3 p-3.5 rounded-xl border ${borderCol} ${bgCol} shadow-xl shadow-black/40 text-xs backdrop-blur-md transition-all duration-300 transform translate-y-2 opacity-0 max-w-sm`;
  toast.innerHTML = `
    <i class="fa-solid ${icon} text-base mt-0.5"></i>
    <div class="flex-1">
      <div class="font-bold text-white">${title}</div>
      <div class="text-[11px] text-slate-300 mt-0.5">${message}</div>
    </div>
  `;

  container.appendChild(toast);
  requestAnimationFrame(() => {
    toast.classList.remove('translate-y-2', 'opacity-0');
  });

  setTimeout(() => {
    toast.classList.add('opacity-0', 'translate-y-2');
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

let map;
let markersLayer;
let hotspotsLayer;
let categoryChart, channelChart, languageChart;

document.addEventListener('DOMContentLoaded', () => {
  initMap();
  initCharts();
});

function initMap() {
  // Center on Chandigarh (Sector 17)
  map = L.map('map').setView([30.7398, 76.7827], 12);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '© OpenStreetMap contributors | Chandigarh Smart City DPI'
  }).addTo(map);

  markersLayer = L.layerGroup().addTo(map);
  hotspotsLayer = L.layerGroup().addTo(map);

  renderHotspots(INITIAL_HOTSPOTS);
  renderMarkers(INITIAL_GRIEVANCES);
}

function resetMapView() {
  if (map) {
    map.setView([30.7398, 76.7827], 12);
  }
}

function renderHotspots(hotspots) {
  hotspotsLayer.clearLayers();
  hotspots.forEach(h => {
    // Large demand hotspot circle
    const circle = L.circle([h.center_lat, h.center_lng], {
      color: '#e11d48',
      fillColor: '#f43f5e',
      fillOpacity: 0.25,
      radius: 450 + (h.incident_count * 120)
    }).bindPopup(`
      <div class="text-xs font-sans">
        <strong class="text-rose-600 block text-sm font-bold">${h.cluster_id}</strong>
        <span class="font-bold text-slate-800">${h.sector}</span> • <span class="text-slate-500">${h.category}</span>
        <p class="mt-1 text-slate-700">${h.summary}</p>
        <div class="mt-1.5 text-[11px] font-semibold text-rose-700">Urgency: ${h.avg_urgency}/10 | Reports: ${h.incident_count}</div>
      </div>
    `);
    hotspotsLayer.addLayer(circle);
  });
}

function renderMarkers(grievances) {
  markersLayer.clearLayers();
  grievances.forEach(g => {
    const isCritical = g.urgency_score >= 8;
    const markerColor = isCritical ? '#e11d48' : (g.urgency_score >= 5 ? '#d97706' : '#059669');

    const marker = L.circleMarker([g.lat, g.lng], {
      radius: 7,
      fillColor: markerColor,
      color: '#ffffff',
      weight: 2,
      opacity: 1,
      fillOpacity: 0.9
    }).bindPopup(`
      <div class="text-xs font-sans p-1">
        <div class="flex items-center gap-1.5 mb-1">
          <span class="px-1.5 py-0.5 rounded text-[10px] font-bold text-white" style="background:${markerColor}">${g.urgency_score}/10</span>
          <span class="font-bold text-slate-900">${g.id}</span>
          <span class="text-slate-500">(${g.channel})</span>
        </div>
        <div class="font-bold text-emerald-800">${g.sector}</div>
        <p class="text-slate-700 my-1"><strong>Issue:</strong> ${g.summary}</p>
        <p class="text-slate-500 text-[11px]"><strong>Dept:</strong> ${g.department}</p>
        <p class="text-slate-500 text-[11px]"><strong>Lang:</strong> ${g.language_detected}</p>
        <div class="mt-1.5 pt-1 border-t border-slate-200 flex justify-between items-center">
          <span class="text-[10px] text-slate-400">${g.status}</span>
          <span class="text-[11px] font-bold text-slate-700">👍 ${g.upvotes} upvotes</span>
        </div>
      </div>
    `);
    markersLayer.addLayer(marker);
  });
}

function fillSample(id) {
  const input = document.getElementById('rawInput');
  const radios = document.getElementsByName('channel');
  
  if (id === 1) {
    radios[0].checked = true; // VOICE
    input.value = "ਸਾਡੇ ਸੈਕਟਰ 22 ਸ਼ਾਸਤਰੀ ਮਾਰਕੀਟ ਕੋਲ ਪਾਣੀ ਦੀ ਮੁੱਖ ਪਾਈਪ ਫਟ ਗਈ ਹੈ, ਪੂਰੀ ਸੜਕ ਤੇ ਪਾਣੀ ਭਰ ਗਿਆ ਹੈ ਤੇ ਦੁਕਾਨਾਂ ਵਿੱਚ ਜਾ ਰਿਹਾ ਹੈ।";
  } else if (id === 2) {
    radios[1].checked = true; // WHATSAPP
    input.value = "सेक्टर 35 सी होटल स्ट्रिप के पीछे मुख्य सड़क पर बहुत बड़े गड्ढे हैं जिससे कल रात एक स्कूटी वाले का एक्सीडेंट हो गया।";
  } else if (id === 3) {
    radios[0].checked = true; // VOICE
    input.value = "ਫੇਜ਼ 7 ਮੋਹਾਲੀ ਮਾਰਕੀਟ ਦੀਆਂ ਸਟਰੀਟ ਲਾਈਟਾਂ ਪਿਛਲੇ 10 ਦਿਨਾਂ ਤੋਂ ਬੰਦ ਹਨ, ਸ਼ਾਮ ਨੂੰ ਹਨੇਰੇ ਕਾਰਨ ਚੋਰੀਆਂ ਦਾ ਡਰ ਹੈ।";
  } else if (id === 4) {
    radios[2].checked = true; // WEB
    input.value = "Dangerous live wires hanging from electric pole outside school in Sector 15 Patel Market.";
  }
  onInputFeedback();
}

async function submitGrievance(event) {
  event.preventDefault();
  const submitBtn = document.getElementById('submitBtn');
  const rawInput = document.getElementById('rawInput').value.trim();
  const channel = document.querySelector('input[name="channel"]:checked').value;

  if (!rawInput) return;

  submitBtn.disabled = true;
  submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing via Google Gemini 2.0 Flash...';

  try {
    const res = await fetch('/api/v1/grievances', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ raw_input: rawInput, channel: channel })
    });

    if (!res.ok) throw new Error('Failed to record grievance');

    const data = await res.json();

    // Show result preview card
    const preview = document.getElementById('resultPreview');
    preview.classList.remove('hidden');
    document.getElementById('resUrgency').textContent = `Urgency: ${data.urgency_score}/10`;
    document.getElementById('resLangCategory').textContent = `${data.language_detected} • ${data.category} (${data.sector})`;
    document.getElementById('resTranslation').textContent = `"${data.translated_text}"`;
    document.getElementById('resDepartment').textContent = data.department;

    // Reset textarea
    document.getElementById('rawInput').value = '';

    // Prepend to feed
    prependGrievanceToFeed(data);
    showToast(`Grievance ${data.id} Triaged`, `${data.category} in ${data.sector} routed to ${data.department}.`, 'success');

    // Update markers
    INITIAL_GRIEVANCES.unshift(data);
    renderMarkers(INITIAL_GRIEVANCES);

    // Pan map to new incident
    if (map && data.lat && data.lng) {
      map.setView([data.lat, data.lng], 14);
    }

    // Increment count
    const totalEl = document.getElementById('statTotal');
    totalEl.textContent = parseInt(totalEl.textContent) + 1;

  } catch (err) {
    showToast("Submission Error", err.message, "error");
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = '<i class="fa-solid fa-paper-plane"></i> Triage via Google Gemini 2.0 Flash';
  }
}

function prependGrievanceToFeed(g) {
  const feed = document.getElementById('grievanceFeed');
  const item = document.createElement('div');
  item.className = 'pt-2.5 bg-emerald-50/50 p-2 rounded-lg border border-emerald-200 transition';
  item.innerHTML = `
    <div class="flex items-start justify-between gap-2">
      <div>
        <div class="flex items-center gap-1.5 flex-wrap">
          <span class="text-[10px] font-bold px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">${g.channel}</span>
          <span class="text-[10px] font-bold px-1.5 py-0.5 rounded bg-blue-50 text-blue-700">${g.language_detected}</span>
          <span class="text-[10px] font-bold text-emerald-700">${g.sector}</span>
        </div>
        <p class="text-xs font-semibold text-slate-800 mt-1">${g.summary}</p>
        <p class="text-[11px] text-slate-500 mt-0.5">${g.department}</p>
      </div>
      <div class="text-right shrink-0">
        <span class="text-[10px] font-bold px-1.5 py-0.5 rounded ${g.urgency_score >= 8 ? 'bg-rose-100 text-rose-700' : 'bg-amber-100 text-amber-700'}">
          ${g.urgency_score}/10
        </span>
        <div class="mt-1.5">
          <button onclick="upvoteIssue('${g.id}')" class="text-[11px] text-slate-500 hover:text-emerald-600 transition flex items-center gap-1 ml-auto">
            <i class="fa-solid fa-thumbs-up"></i> <span id="upvotes-${g.id}">${g.upvotes}</span>
          </button>
        </div>
      </div>
    </div>
  `;
  feed.insertBefore(item, feed.firstChild);
}

async function upvoteIssue(id) {
  try {
    const res = await fetch(`/api/v1/grievances/${id}/upvote`, { method: 'POST' });
    if (res.ok) {
      const data = await res.json();
      const el = document.getElementById(`upvotes-${id}`);
      if (el) el.textContent = data.upvotes;
      showToast("Consensus Upvoted", `Grievance #${id} prioritized by community.`, "success");
    }
  } catch (err) {
    console.error("Upvote failed", err);
  }
}

function initCharts() {
  // Aggregate initial counts
  const catCounts = {};
  const chCounts = {};
  const langCounts = {};

  INITIAL_GRIEVANCES.forEach(g => {
    catCounts[g.category] = (catCounts[g.category] || 0) + 1;
    chCounts[g.channel] = (chCounts[g.channel] || 0) + 1;
    langCounts[g.language_detected] = (langCounts[g.language_detected] || 0) + 1;
  });

  // 1. Category Chart
  const ctxCat = document.getElementById('categoryChart').getContext('2d');
  categoryChart = new Chart(ctxCat, {
    type: 'doughnut',
    data: {
      labels: Object.keys(catCounts),
      datasets: [{
        data: Object.values(catCounts),
        backgroundColor: ['#0284c7', '#059669', '#d97706', '#e11d48', '#7c3aed', '#64748b']
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom', labels: { boxWidth: 10, font: { size: 10 } } } }
    }
  });

  // 2. Channel Chart
  const ctxCh = document.getElementById('channelChart').getContext('2d');
  channelChart = new Chart(ctxCh, {
    type: 'bar',
    data: {
      labels: Object.keys(chCounts),
      datasets: [{
        label: 'Reports',
        data: Object.values(chCounts),
        backgroundColor: '#10b981'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true, ticks: { stepSize: 1, font: { size: 10 } } }, x: { ticks: { font: { size: 10 } } } }
    }
  });

  // 3. Language Chart
  const ctxLang = document.getElementById('languageChart').getContext('2d');
  languageChart = new Chart(ctxLang, {
    type: 'polarArea',
    data: {
      labels: Object.keys(langCounts),
      datasets: [{
        data: Object.values(langCounts),
        backgroundColor: ['#6366f1cc', '#ec4899cc', '#14b8a6cc']
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom', labels: { boxWidth: 10, font: { size: 10 } } } }
    }
  });
}
