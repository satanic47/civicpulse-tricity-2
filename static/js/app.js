// Client-Side Deterministic Gemini 2.0 Triage Engine for Static GitHub Pages
function clientSideGeminiTriage(text, channel) {
  const t = text.toLowerCase();

  // 1. Language Detection
  const punjabiMarkers = ["ਸਾਡੇ", "ਸੈਕਟਰ", "ਪਾਣੀ", "ਸੜਕ", "ਲਾਈਟਾਂ", "ਗੰਦਗੀ", "ਖੱਡੇ", "ਬਿਜਲੀ", "ਨਹੀਂ", "ਆ ਰਿਹਾ", "ਬੰਦ ਹੈ", "ਤਾਰਾਂ", "ਤੋੜਿਆ", "ਜੀ"];
  const hindiMarkers = ["हमारे", "सेक्टर", "पानी", "सड़क", "बिजली", "कचरा", "गड्ढे", "नाली", "सफाई", "नहीं", "हो रहा", "खराब", "है", "तार"];

  let lang = "English";
  if (punjabiMarkers.some(m => text.includes(m)) || ["sade", "paani", "sadak", "khatam", "bijli"].some(m => t.includes(m))) {
    lang = "Punjabi";
  } else if (hindiMarkers.some(m => text.includes(m)) || ["hamare", "gaddha", "kachra"].some(m => t.includes(m))) {
    lang = "Hindi";
  }

  // 2. Category & Department Routing
  let category = "General Public Infrastructure";
  let department = "Municipal Corporation Chandigarh (Central Grievance Cell)";
  let urgency = 5;

  if (["pothole", "road", "sadak", "khadda", "gaddha", "accident", "ਸੜਕ", "ਖੱਡੇ", "सड़क", "गड्ढे"].some(w => t.includes(w))) {
    category = "Roads & Traffic";
    department = "Engineering Department (B&R - Roads Wing)";
    urgency = t.includes("accident") || t.includes("huge") || t.includes("एक्सीडेंट") ? 8 : 6;
  } else if (["water", "paani", "pipeline", "burst", "leak", "sewage", "overflow", "ਪਾਣੀ", "ਫਟ", "पानी", "सीवर"].some(w => t.includes(w))) {
    category = "Water Supply & Sewage";
    department = "Public Health & Water Supply Division";
    urgency = t.includes("burst") || t.includes("ਫਟ") || t.includes("leak") ? 9 : 7;
  } else if (["wire", "light", "spark", "shock", "dark", "pole", "bijli", "ਤਾਰਾਂ", "ਲਾਈਟ", "बिजली", "तार"].some(w => t.includes(w))) {
    category = "Street Lighting & Power";
    department = "Electricity Department & Smart Street Lighting Division";
    urgency = t.includes("wire") || t.includes("school") || t.includes("spark") || t.includes("ਤਾਰਾਂ") ? 10 : 8;
  } else if (["garbage", "kachra", "waste", "smell", "dump", "ਕੂੜਾ", "ਗੰਦਗੀ", "कचरा", "सफाई"].some(w => t.includes(w))) {
    category = "Sanitation & Waste Management";
    department = "Medical Officer of Health (Sanitation Wing)";
    urgency = 6;
  }

  // 3. Sector Geocoding (exact coordinates aligned with Le Corbusier centroids)
  let sector = "Sector 17";
  let lat = 30.7398;
  let lng = 76.7827;

  if (t.includes("22") || t.includes("shastri") || text.includes("੨੨")) {
    sector = "Sector 22"; lat = 30.7300; lng = 76.7740;
  } else if (t.includes("35") || text.includes("३५") || text.includes("੩੫")) {
    sector = "Sector 35"; lat = 30.7290; lng = 76.7540;
  } else if (t.includes("phase 7") || t.includes("mohali") || text.includes("ਮੋਹਾਲੀ") || t.includes("ਫੇਜ਼ 7")) {
    sector = "Phase 7 Mohali"; lat = 30.7055; lng = 76.7125;
  } else if (t.includes("15") || t.includes("patel") || text.includes("੧੫")) {
    sector = "Sector 15"; lat = 30.7510; lng = 76.7620;
  } else if (t.includes("8") || t.includes("madhya") || text.includes("dav")) {
    sector = "Sector 8"; lat = 30.7350; lng = 76.7960;
  } else if (t.includes("20")) {
    sector = "Sector 20"; lat = 30.7170; lng = 76.7920;
  } else if (t.includes("43") || t.includes("isbt")) {
    sector = "Sector 43"; lat = 30.7160; lng = 76.7490;
  }

  const id = `INC-${Date.now().toString().slice(-6)}`;
  return {
    id: id,
    channel: channel,
    language_detected: lang,
    category: category,
    department: department,
    sector: sector,
    lat: lat,
    lng: lng,
    urgency_score: urgency,
    summary: `${category} issue reported in ${sector}.`,
    translated_text: `Standardized Report: Citizen filed a ${category} notice regarding '${text.slice(0, 80)}' in ${sector}.`,
    status: "TRIAGED",
    upvotes: 1
  };
}

function onInputFeedback() {
  const el = document.getElementById('rawInput');
  const countEl = document.getElementById('charCount');
  const warningEl = document.getElementById('hazardWarning');
  if (!el) return;

  const val = el.value || '';
  if (countEl) countEl.textContent = `${val.length} / 2500`;

  const lower = val.toLowerCase();
  const hazardKeywords = ['wire', 'spark', 'shock', 'accident', 'burst', 'overflow', 'fire', 'current', 'death', 'hospital', 'school', 'danger', 'ਤਾਰਾਂ', 'ਫਟ', 'ਕਰੰਟ', 'ਖ਼ਤਰਾ', 'तार', 'करंट', 'खतरा'];
  const hasHazard = hazardKeywords.some(k => lower.includes(k) || val.includes(k));

  if (warningEl) {
    if (hasHazard && val.length > 5) {
      warningEl.classList.remove('hidden');
      warningEl.classList.add('flex');
    } else {
      warningEl.classList.add('hidden');
      warningEl.classList.remove('flex');
    }
  }
}

function showToast(title, message, type = 'info') {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const toast = document.createElement('div');
  const isErr = type === 'error';
  const isWarn = type === 'warning';
  const bgCol = isErr ? 'bg-rose-950/90 text-rose-200' : (isWarn ? 'bg-amber-950/90 text-amber-200' : 'bg-slate-900/90 text-slate-100');
  const borderCol = isErr ? 'border-rose-700/80' : (isWarn ? 'border-amber-700/80' : 'border-emerald-700/80');
  const icon = isErr ? 'fa-circle-xmark text-rose-400' : (isWarn ? 'fa-triangle-exclamation text-amber-400' : 'fa-circle-check text-emerald-400');

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

// ---------------------------------------------------------------------------
// MAP & HOTSPOT INTERACTIVITY ENGINE
// ---------------------------------------------------------------------------
let map;
let markersLayer;
let hotspotsLayer;
let hotspotCircleMap = []; // Array of { sector, circle, data, baseRadius }
let grievanceMarkers = [];  // Array of { sector, marker, data }
let activeSelectedSector = null;
let categoryChart, channelChart, languageChart;

const SECTOR_COORDS = {
  'sector15': [30.7510, 76.7620],
  'sector22': [30.7300, 76.7740],
  'sector35': [30.7290, 76.7540],
  'phase7mohali': [30.7055, 76.7125],
  'sector20': [30.7170, 76.7920],
  'sector8': [30.7350, 76.7960],
  'sector43': [30.7160, 76.7490],
  'sector14panchkula': [30.6850, 76.8600],
  'sector17': [30.7398, 76.7827]
};

document.addEventListener('DOMContentLoaded', () => {
  initMap();
  initCharts();
});

function initMap() {
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
  hotspotCircleMap = [];

  hotspots.forEach(h => {
    const baseRadius = 450 + (h.incident_count * 120);
    const circle = L.circle([h.center_lat, h.center_lng], {
      color: '#e11d48',
      fillColor: '#f43f5e',
      fillOpacity: 0.28,
      weight: 2,
      radius: baseRadius
    }).bindPopup(`
      <div class="text-xs font-sans p-1">
        <div class="flex items-center gap-1.5 mb-1">
          <span class="px-1.5 py-0.5 rounded bg-rose-600 text-white font-bold text-[10px]">${h.cluster_id}</span>
          <span class="font-bold text-slate-800">${h.sector}</span>
        </div>
        <div class="font-semibold text-rose-700">${h.category}</div>
        <p class="mt-1 text-slate-700 leading-snug">${h.summary}</p>
        <div class="mt-2 pt-1 border-t border-slate-100 flex items-center justify-between text-[11px]">
          <span class="font-bold text-rose-600">Urgency: ${h.avg_urgency}/10</span>
          <span class="text-slate-500 font-semibold">${h.incident_count} reports</span>
        </div>
      </div>
    `);

    // Clicking the circle highlights the sector and shows toast
    circle.on('click', () => {
      highlightSectorOnMap(h.sector, false);
      showToast(`Hotspot Selected: ${h.sector}`, `${h.category} demand cluster with ${h.incident_count} reports.`, 'info');
    });

    hotspotsLayer.addLayer(circle);
    hotspotCircleMap.push({ sector: h.sector, circle: circle, data: h, baseRadius: baseRadius });
  });

  // Re-apply highlight if a sector is currently selected
  if (activeSelectedSector) {
    highlightSectorOnMap(activeSelectedSector, false);
  }
}

function renderMarkers(grievances) {
  markersLayer.clearLayers();
  grievanceMarkers = [];

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

    marker.on('click', () => {
      highlightSectorOnMap(g.sector, false);
    });

    markersLayer.addLayer(marker);
    grievanceMarkers.push({ sector: g.sector, marker: marker, data: g });
  });
}

function highlightSectorOnMap(sectorName, flyTo = true) {
  if (!sectorName) return;

  activeSelectedSector = sectorName;
  const targetNorm = sectorName.toLowerCase().replace(/[^a-z0-9]/g, '');
  let matchedEntry = null;

  // 1. DYNAMICALLY UPDATE HEATMAP CIRCLES
  hotspotCircleMap.forEach(item => {
    const itemNorm = item.sector.toLowerCase().replace(/[^a-z0-9]/g, '');
    const isMatch = itemNorm.includes(targetNorm) || targetNorm.includes(itemNorm);

    if (isMatch) {
      matchedEntry = item;
      // Highlighting circle: larger radius, prominent border, vibrant fill
      item.circle.setStyle({
        color: '#be123c',
        fillColor: '#f43f5e',
        fillOpacity: 0.65,
        weight: 4
      });
      item.circle.setRadius(item.baseRadius * 1.35);
      item.circle.bringToFront();
    } else {
      // Dim other circles
      item.circle.setStyle({
        color: '#94a3b8',
        fillColor: '#cbd5e1',
        fillOpacity: 0.08,
        weight: 1
      });
      item.circle.setRadius(item.baseRadius * 0.85);
    }
  });

  // 2. HIGHLIGHT / DIM GRIEVANCE MARKERS
  grievanceMarkers.forEach(item => {
    const itemNorm = item.sector.toLowerCase().replace(/[^a-z0-9]/g, '');
    const isMatch = itemNorm.includes(targetNorm) || targetNorm.includes(itemNorm);
    if (isMatch) {
      item.marker.setStyle({ opacity: 1, fillOpacity: 0.95, radius: 9, weight: 3 });
      item.marker.bringToFront();
    } else {
      item.marker.setStyle({ opacity: 0.25, fillOpacity: 0.15, radius: 5, weight: 1 });
    }
  });

  // 3. PAN / FLY TO SECTOR
  let targetCoords = null;
  for (const [k, coords] of Object.entries(SECTOR_COORDS)) {
    if (targetNorm.includes(k) || k.includes(targetNorm)) {
      targetCoords = coords;
      break;
    }
  }
  if (!targetCoords && matchedEntry) {
    targetCoords = [matchedEntry.data.center_lat, matchedEntry.data.center_lng];
  }

  if (map && targetCoords && flyTo) {
    map.flyTo(targetCoords, 14, { duration: 0.8 });
  }

  // 4. OPEN POPUP IF MATCHED
  if (matchedEntry && matchedEntry.circle) {
    setTimeout(() => {
      matchedEntry.circle.openPopup();
    }, 450);
  }

  // 5. UPDATE SECTOR PILL UI
  document.querySelectorAll('.sector-pill').forEach(btn => {
    btn.classList.remove('bg-emerald-600', 'text-white', 'shadow-sm');
    btn.classList.add('bg-white', 'text-slate-700');
  });
  const activeBtn = document.getElementById(`filter-${sectorName.replace(/\s+/g, '-')}`);
  if (activeBtn) {
    activeBtn.classList.remove('bg-white', 'text-slate-700');
    activeBtn.classList.add('bg-emerald-600', 'text-white', 'shadow-sm');
  }

  // 6. UPDATE ACTIVE BADGE
  const badge = document.getElementById('activeHotspotBadge');
  const badgeText = document.getElementById('activeHotspotText');
  if (badge && badgeText) {
    badge.classList.remove('hidden');
    badge.classList.add('inline-flex');
    badgeText.textContent = `${sectorName} Heatmap Active`;
  }
}

function resetSectorFilter() {
  activeSelectedSector = null;

  // Restore all hotspot circles
  hotspotCircleMap.forEach(item => {
    item.circle.setStyle({
      color: '#e11d48',
      fillColor: '#f43f5e',
      fillOpacity: 0.28,
      weight: 2
    });
    item.circle.setRadius(item.baseRadius);
  });

  // Restore all markers
  grievanceMarkers.forEach(item => {
    const isCritical = item.data.urgency_score >= 8;
    const col = isCritical ? '#e11d48' : (item.data.urgency_score >= 5 ? '#d97706' : '#059669');
    item.marker.setStyle({
      radius: 7,
      fillColor: col,
      color: '#ffffff',
      weight: 2,
      opacity: 1,
      fillOpacity: 0.9
    });
  });

  // Reset sample button active states
  document.querySelectorAll('.sample-btn').forEach(btn => {
    btn.classList.remove('ring-2', 'ring-emerald-500', 'ring-blue-500', 'ring-purple-500', 'ring-rose-500', 'bg-emerald-50', 'bg-blue-50', 'bg-purple-50', 'bg-rose-50');
  });

  // Reset sector pills
  document.querySelectorAll('.sector-pill').forEach(btn => {
    btn.classList.remove('bg-emerald-600', 'text-white', 'shadow-sm');
    btn.classList.add('bg-white', 'text-slate-700');
  });
  const allBtn = document.getElementById('filter-all');
  if (allBtn) {
    allBtn.classList.remove('bg-white', 'text-slate-700');
    allBtn.classList.add('bg-emerald-600', 'text-white', 'shadow-sm');
  }

  const badge = document.getElementById('activeHotspotBadge');
  if (badge) {
    badge.classList.add('hidden');
    badge.classList.remove('inline-flex');
  }

  resetMapView();
  showToast("Heatmap Filter Reset", "Viewing all Tricity infrastructure clusters.", "info");
}

function fillSample(id) {
  const input = document.getElementById('rawInput');
  const radios = document.getElementsByName('channel');

  // Reset sample button styles
  document.querySelectorAll('.sample-btn').forEach(btn => {
    btn.classList.remove('ring-2', 'ring-emerald-500', 'ring-blue-500', 'ring-purple-500', 'ring-rose-500', 'bg-emerald-50', 'bg-blue-50', 'bg-purple-50', 'bg-rose-50');
  });

  let targetSector = "Sector 22";
  const btn = document.getElementById(`sample-btn-${id}`);

  if (id === 1) {
    radios[0].checked = true; // VOICE
    input.value = "ਸਾਡੇ ਸੈਕਟਰ 22 ਸ਼ਾਸਤਰੀ ਮਾਰਕੀਟ ਕੋਲ ਪਾਣੀ ਦੀ ਮੁੱਖ ਪਾਈਪ ਫਟ ਗਈ ਹੈ, ਪੂਰੀ ਸੜਕ ਤੇ ਪਾਣੀ ਭਰ ਗਿਆ ਹੈ ਤੇ ਦੁਕਾਨਾਂ ਵਿੱਚ ਜਾ ਰਿਹਾ ਹੈ।";
    targetSector = "Sector 22";
    if (btn) btn.classList.add('ring-2', 'ring-emerald-500', 'bg-emerald-50');
    showToast("Sector 22 Selected", "Heatmap focused on Sector 22 water supply burst cluster.", "info");
  } else if (id === 2) {
    radios[1].checked = true; // WHATSAPP
    input.value = "सेक्टर 35 सी होटल स्ट्रिप के पीछे मुख्य सड़क पर बहुत बड़े गड्ढे हैं जिससे कल रात एक स्कूटी वाले का एक्सीडेंट हो गया।";
    targetSector = "Sector 35";
    if (btn) btn.classList.add('ring-2', 'ring-blue-500', 'bg-blue-50');
    showToast("Sector 35 Selected", "Heatmap focused on Sector 35 pothole risk cluster.", "info");
  } else if (id === 3) {
    radios[0].checked = true; // VOICE
    input.value = "ਫੇਜ਼ 7 ਮੋਹਾਲੀ ਮਾਰਕੀਟ ਦੀਆਂ ਸਟਰੀਟ ਲਾਈਟਾਂ ਪਿਛਲੇ 10 ਦਿਨਾਂ ਤੋਂ ਬੰਦ ਹਨ, ਸ਼ਾਮ ਨੂੰ ਹਨੇਰੇ ਕਾਰਨ ਚੋਰੀਆਂ ਦਾ ਡਰ ਹੈ।";
    targetSector = "Phase 7 Mohali";
    if (btn) btn.classList.add('ring-2', 'ring-purple-500', 'bg-purple-50');
    showToast("Phase 7 Mohali Selected", "Heatmap focused on Phase 7 Mohali dark streetlight zone.", "info");
  } else if (id === 4) {
    radios[2].checked = true; // WEB
    input.value = "Dangerous live wires hanging from electric pole outside school in Sector 15 Patel Market.";
    targetSector = "Sector 15";
    if (btn) btn.classList.add('ring-2', 'ring-rose-500', 'bg-rose-50');
    showToast("Sector 15 Selected", "Heatmap focused on Sector 15 school live wires critical hazard.", "warning");
  }

  onInputFeedback();
  highlightSectorOnMap(targetSector, true);
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
    let data = null;
    try {
      const res = await fetch('/api/v1/grievances', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ raw_input: rawInput, channel: channel })
      });
      if (res.ok) {
        data = await res.json();
      }
    } catch (e) {
      // Running on Static GitHub Pages
    }

    if (!data) {
      data = clientSideGeminiTriage(rawInput, channel);
    }

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

    // 1. Add new marker to map & update markers list
    INITIAL_GRIEVANCES.unshift(data);
    renderMarkers(INITIAL_GRIEVANCES);

    // 2. DYNAMICALLY UPDATE OR CREATE HOTSPOT CLUSTER FOR THIS SECTOR
    const targetNorm = data.sector.toLowerCase().replace(/[^a-z0-9]/g, '');
    let h = INITIAL_HOTSPOTS.find(item => item.sector.toLowerCase().replace(/[^a-z0-9]/g, '') === targetNorm);
    if (h) {
      h.incident_count += 1;
      h.avg_urgency = Number(((h.avg_urgency * (h.incident_count - 1) + data.urgency_score) / h.incident_count).toFixed(1));
      h.summary = `${h.incident_count} reported issues concerning ${h.category} in ${h.sector} (Avg Urgency: ${h.avg_urgency}/10)`;
      if (!h.sample_grievances) h.sample_grievances = [];
      h.sample_grievances.unshift(data.summary);
    } else {
      h = {
        cluster_id: `HOTSPOT-TRICITY-0${INITIAL_HOTSPOTS.length + 1}`,
        sector: data.sector,
        category: data.category,
        center_lat: data.lat,
        center_lng: data.lng,
        incident_count: 1,
        avg_urgency: data.urgency_score,
        summary: `1 reported issue concerning ${data.category} in ${data.sector} (Avg Urgency: ${data.urgency_score}/10)`,
        sample_grievances: [data.summary]
      };
      INITIAL_HOTSPOTS.push(h);
    }

    // 3. RE-RENDER HEATMAP CIRCLES WITH EXPANDED RADIUS & PULSE!
    renderHotspots(INITIAL_HOTSPOTS);

    // 4. FOCUS & HIGHLIGHT THE UPDATED CIRCLE ON THE HEATMAP!
    highlightSectorOnMap(data.sector, true);

    // Increment total stat count
    const totalEl = document.getElementById('statTotal');
    if (totalEl) totalEl.textContent = parseInt(totalEl.textContent) + 1;

  } catch (err) {
    showToast("Submission Error", err.message, "error");
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = '<i class="fa-solid fa-paper-plane"></i> Triage via Google Gemini 2.0 Flash';
  }
}

function prependGrievanceToFeed(g) {
  const feed = document.getElementById('grievanceFeed');
  if (!feed) return;

  const item = document.createElement('div');
  item.className = 'pt-2.5 bg-emerald-50/50 p-2.5 rounded-lg border border-emerald-200 transition cursor-pointer hover:bg-emerald-100/60';
  item.onclick = () => highlightSectorOnMap(g.sector, true);

  item.innerHTML = `
    <div class="flex items-start justify-between gap-2">
      <div>
        <div class="flex items-center gap-1.5 flex-wrap">
          <span class="px-1.5 py-0.5 rounded text-[10px] font-bold text-white bg-rose-600">${g.urgency_score}/10</span>
          <span class="text-xs font-bold text-slate-800">${g.id}</span>
          <span class="text-[10px] bg-slate-100 text-slate-600 px-1 rounded">${g.channel}</span>
          <span class="text-[10px] text-emerald-700 font-bold hover:underline">${g.sector} <i class="fa-solid fa-location-crosshairs text-[9px]"></i></span>
        </div>
        <p class="text-xs font-semibold text-slate-800 mt-1">${g.summary}</p>
        <p class="text-[11px] text-slate-500 italic mt-0.5">${g.translated_text || ''}</p>
        <p class="text-[10px] text-slate-400 mt-1">Routed to: <strong class="text-slate-600">${g.department}</strong></p>
      </div>
      <div class="flex flex-col items-end gap-1">
        <button onclick="event.stopPropagation(); upvoteIssue('${g.id}')" class="px-2 py-1 rounded bg-slate-100 hover:bg-emerald-100 text-slate-700 hover:text-emerald-800 text-[11px] font-bold border border-slate-200 transition flex items-center gap-1">
          👍 <span id="upvotes-${g.id}">${g.upvotes}</span>
        </button>
      </div>
    </div>
  `;
  feed.prepend(item);
}

async function upvoteIssue(id) {
  let done = false;
  try {
    const res = await fetch(`/api/v1/grievances/${id}/upvote`, { method: 'POST' });
    if (res.ok) {
      const data = await res.json();
      const el = document.getElementById(`upvotes-${id}`);
      if (el) el.textContent = data.upvotes;
      showToast("Consensus Upvoted", `Grievance #${id} prioritized by community.`, "success");
      done = true;
    }
  } catch (err) {}

  if (!done) {
    const el = document.getElementById(`upvotes-${id}`);
    if (el) {
      const current = parseInt(el.textContent) || 0;
      el.textContent = current + 1;
      showToast("Consensus Upvoted", `Grievance #${id} prioritized by community.`, "success");
    }
  }
}

function initCharts() {
  const catCounts = {};
  const chanCounts = {};
  const langCounts = {};

  INITIAL_GRIEVANCES.forEach(g => {
    catCounts[g.category] = (catCounts[g.category] || 0) + 1;
    chanCounts[g.channel] = (chanCounts[g.channel] || 0) + 1;
    langCounts[g.language_detected] = (langCounts[g.language_detected] || 0) + 1;
  });

  const catCtx = document.getElementById('categoryChart');
  if (catCtx) {
    categoryChart = new Chart(catCtx, {
      type: 'doughnut',
      data: {
        labels: Object.keys(catCounts),
        datasets: [{
          data: Object.values(catCounts),
          backgroundColor: ['#059669', '#d97706', '#dc2626', '#4f46e5', '#0891b2', '#7c3aed']
        }]
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { boxWidth: 10, font: { size: 10 } } } } }
    });
  }

  const chanCtx = document.getElementById('channelChart');
  if (chanCtx) {
    channelChart = new Chart(chanCtx, {
      type: 'pie',
      data: {
        labels: Object.keys(chanCounts),
        datasets: [{
          data: Object.values(chanCounts),
          backgroundColor: ['#10b981', '#25D366', '#3b82f6', '#6366f1']
        }]
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { boxWidth: 10, font: { size: 10 } } } } }
    });
  }

  const langCtx = document.getElementById('languageChart');
  if (langCtx) {
    languageChart = new Chart(langCtx, {
      type: 'bar',
      data: {
        labels: Object.keys(langCounts),
        datasets: [{
          label: 'Grievances by Language',
          data: Object.values(langCounts),
          backgroundColor: '#059669'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: { y: { beginAtZero: true, ticks: { stepSize: 1, font: { size: 10 } } }, x: { ticks: { font: { size: 10 } } } },
        plugins: { legend: { display: false } }
      }
    });
  }
}
