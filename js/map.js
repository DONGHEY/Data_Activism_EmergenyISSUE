/* ── Leaflet 인터랙티브 지도 ── */

const GRADE_STYLE = {
  "권역응급의료센터":    { color: "#e63946", radius: 10 },
  "지역응급의료센터":   { color: "#ff8c42", radius: 8 },
  "지역응급의료기관":   { color: "#d29922", radius: 7 },
  "응급실운영신고기관": { color: "#6b7280", radius: 6 },
};

function getStyle(grade) {
  return GRADE_STYLE[grade] || { color: "#6b7280", radius: 6 };
}

async function initMap() {
  const map = L.map("map", {
    center: [37.563, 126.979],
    zoom: 11,
    zoomControl: true,
  });

  L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
    attribution: '© <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors © <a href="https://carto.com/">CARTO</a>',
    subdomains: "abcd",
    maxZoom: 19,
  }).addTo(map);

  let hospitals;
  try {
    const res = await fetch("data/er_map.json");
    hospitals = await res.json();
  } catch {
    console.error("er_map.json 로드 실패. python -m http.server 8080으로 실행하세요.");
    return;
  }

  hospitals.forEach(h => {
    const style = getStyle(h.grade);
    const marker = L.circleMarker([h.lat, h.lon], {
      radius: style.radius,
      fillColor: style.color,
      color: "#fff",
      weight: 1.5,
      opacity: 0.9,
      fillOpacity: 0.85,
    });

    const bedsText = h.beds !== null ? `${h.beds}개` : "정보 없음";
    marker.bindPopup(`
      <div style="font-family:'Noto Sans KR',sans-serif;min-width:180px;">
        <strong style="font-size:0.95rem;">${h.name}</strong>
        <div style="margin:0.4rem 0;font-size:0.78rem;color:#9ca3af;">${h.addr}</div>
        <div style="display:flex;gap:0.5rem;margin-top:0.5rem;flex-wrap:wrap;">
          <span style="background:#1f2937;border:1px solid #374151;color:#f0f6fc;border-radius:4px;padding:0.15em 0.5em;font-size:0.72rem;">${h.grade || "등급 미상"}</span>
          <span style="background:#1f2937;border:1px solid #374151;color:#58a6ff;border-radius:4px;padding:0.15em 0.5em;font-size:0.72rem;">가용병상 ${bedsText}</span>
        </div>
      </div>
    `, { className: "dark-popup" });

    marker.addTo(map);
  });
}

// 팝업 커스텀 스타일 인라인 주입
const style = document.createElement("style");
style.textContent = `
  .dark-popup .leaflet-popup-content-wrapper {
    background: #1f2937; color: #f0f6fc;
    border: 1px solid #374151; border-radius: 10px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
  }
  .dark-popup .leaflet-popup-tip { background: #1f2937; }
  .dark-popup .leaflet-popup-close-button { color: #8b949e; }
`;
document.head.appendChild(style);

initMap();
