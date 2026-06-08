/* ── 차트 공통 설정 ── */
Chart.defaults.color = "#8b949e";
Chart.defaults.font.family = "'Noto Sans KR', sans-serif";
Chart.defaults.font.size = 12;

const PALETTE = {
  yes:     "rgba(63,185,80,0.85)",
  no:      "rgba(88,166,255,0.85)",
  unknown: "rgba(230,57,70,0.85)",
};

/* ════════════════════════════════════════════════════════════
   1. 자치구별 응급실 분포 (수평 막대)
════════════════════════════════════════════════════════════ */
async function drawDistrictChart() {
  let data;
  try {
    const res = await fetch("data/district_stats.json");
    data = await res.json();
  } catch { return; }

  new Chart(document.getElementById("districtChart"), {
    type: "bar",
    data: {
      labels: data.labels,
      datasets: [{
        label: "응급의료기관 수",
        data: data.counts,
        backgroundColor: data.labels.map((_, i) =>
          i === 0 ? "rgba(230,57,70,0.9)" : "rgba(88,166,255,0.65)"
        ),
        borderRadius: 4,
      }],
    },
    options: {
      indexAxis: "y",
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.raw}개 응급의료기관`,
          },
        },
      },
      scales: {
        x: {
          grid: { color: "#21262d" },
          ticks: { color: "#8b949e" },
        },
        y: {
          grid: { display: false },
          ticks: { color: "#f0f6fc", font: { size: 11 } },
        },
      },
    },
  });
}

/* ════════════════════════════════════════════════════════════
   2. 중증질환별 정보 공개 현황 (수평 누적 막대)
════════════════════════════════════════════════════════════ */
async function drawCapacityChart() {
  let data;
  try {
    const res = await fetch("data/er_seoul_stats.json");
    data = await res.json();
  } catch { return; }

  const total = data.yes.map((v, i) => v + data.no[i] + data.unknown[i]);
  const yesPct = data.yes.map((v, i) => +(v / total[i] * 100).toFixed(1));
  const noPct  = data.no.map((v, i)  => +(v / total[i] * 100).toFixed(1));
  const unkPct = data.unknown.map((v, i) => +(v / total[i] * 100).toFixed(1));

  new Chart(document.getElementById("capacityChart"), {
    type: "bar",
    data: {
      labels: data.conditions,
      datasets: [
        { label: "Y (수용 가능)",  data: yesPct,  backgroundColor: PALETTE.yes,     borderRadius: { topLeft: 0, bottomLeft: 4, topRight: 0, bottomRight: 0 } },
        { label: "N (불가)",       data: noPct,   backgroundColor: PALETTE.no },
        { label: "미공개 (NaN)",   data: unkPct,  backgroundColor: PALETTE.unknown, borderRadius: { topLeft: 0, bottomLeft: 0, topRight: 4, bottomRight: 4 } },
      ],
    },
    options: {
      indexAxis: "y",
      responsive: true,
      plugins: {
        legend: {
          position: "bottom",
          labels: { color: "#8b949e", usePointStyle: true, padding: 16 },
        },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.dataset.label}: ${ctx.raw}%`,
          },
        },
      },
      scales: {
        x: {
          stacked: true,
          max: 100,
          grid: { color: "#21262d" },
          ticks: { color: "#8b949e", callback: v => v + "%" },
        },
        y: {
          stacked: true,
          grid: { display: false },
          ticks: { color: "#f0f6fc", font: { size: 11 } },
        },
      },
    },
  });
}

/* ════════════════════════════════════════════════════════════
   3. 설문: 응급상황 시 정보 탐색 방법 (도넛)
════════════════════════════════════════════════════════════ */
function drawSearchMethodChart() {
  new Chart(document.getElementById("searchMethodChart"), {
    type: "doughnut",
    data: {
      labels: ["가족·지인 연락", "포털 검색", "119 문의", "공공앱 사용"],
      datasets: [{
        data: [38.9, 27.8, 22.2, 0],
        backgroundColor: ["#58a6ff", "#3fb950", "#d29922", "#e63946"],
        borderColor: "#161b22",
        borderWidth: 3,
      }],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: "bottom",
          labels: { color: "#8b949e", usePointStyle: true, padding: 12, font: { size: 11 } },
        },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.label}: ${ctx.raw}%`,
          },
        },
      },
      cutout: "60%",
    },
  });
}

/* ════════════════════════════════════════════════════════════
   4. 설문: 응급상황에서 필요한 정보 (수평 막대)
════════════════════════════════════════════════════════════ */
function drawNeedInfoChart() {
  const labels = ["진료 가능 병원", "응급실 혼잡도", "전문의 유무", "병상 현황"];
  const data   = [41.0, 12.8, 12.8, 10.3];
  new Chart(document.getElementById("needInfoChart"), {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label: "응답 비율 (%)",
        data,
        backgroundColor: data.map((v, i) => i === 0 ? "rgba(230,57,70,0.9)" : "rgba(88,166,255,0.65)"),
        borderRadius: 4,
      }],
    },
    options: {
      indexAxis: "y",
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        x: {
          grid: { color: "#21262d" },
          ticks: { color: "#8b949e", callback: v => v + "%" },
          max: 50,
        },
        y: { grid: { display: false }, ticks: { color: "#f0f6fc" } },
      },
    },
  });
}

/* ════════════════════════════════════════════════════════════
   5. 설문: 원하는 앱 기능 (수평 막대)
════════════════════════════════════════════════════════════ */
function drawWantFeatureChart() {
  const labels = ["진료 가능 여부 확인", "실시간 병상 현황", "응급실 혼잡도", "위치 기반 병원 안내"];
  const data   = [71.8, 66.7, 61.5, 43.6];
  new Chart(document.getElementById("wantFeatureChart"), {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label: "응답 비율 (%)",
        data,
        backgroundColor: "rgba(63,185,80,0.75)",
        borderRadius: 4,
      }],
    },
    options: {
      indexAxis: "y",
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        x: {
          grid: { color: "#21262d" },
          ticks: { color: "#8b949e", callback: v => v + "%" },
          max: 80,
        },
        y: { grid: { display: false }, ticks: { color: "#f0f6fc" } },
      },
    },
  });
}

/* ════════════════════════════════════════════════════════════
   6. 능력 테이블 + 클릭 시 병원 목록
════════════════════════════════════════════════════════════ */
const CAPABILITY_DATA = [
  { condition: "뇌졸중",       old_rate: "53.9%", new_rate: "32.7%", count: 17, level: "mid",
    hospitals: [
      { name: "경찰병원",               grade: "지역응급의료기관" },
      { name: "구로성심병원",            grade: "지역응급의료기관" },
      { name: "기쁨병원",               grade: "지역응급의료기관" },
      { name: "녹색병원",               grade: "지역응급의료기관" },
      { name: "대림성모병원",            grade: "지역응급의료기관" },
      { name: "부민병원",               grade: "지역응급의료기관" },
      { name: "서울산보람병원",           grade: "지역응급의료기관" },
      { name: "서울성심병원",            grade: "지역응급의료기관" },
      { name: "서울적십자병원",           grade: "지역응급의료기관" },
      { name: "서울특별시동부병원",        grade: "지역응급의료기관" },
      { name: "서울특별시서남병원",        grade: "지역응급의료기관" },
      { name: "세란병원",               grade: "지역응급의료기관" },
      { name: "의료법인동신의료재단동신병원", grade: "지역응급의료기관" },
      { name: "의료법인청구성심병원",      grade: "지역응급의료기관" },
      { name: "의료법인풍산의료재단동부제일병원", grade: "지역응급의료기관" },
      { name: "한국원자력의학원원자력병원", grade: "지역응급의료기관" },
      { name: "혜민병원",               grade: "지역응급의료기관" },
    ]
  },
  { condition: "심근경색", old_rate: "57.9%", new_rate: "13.5%", count: 5, level: "low",
    hospitals: [
      { name: "구로성심병원",   grade: "지역응급의료기관" },
      { name: "기쁨병원",     grade: "지역응급의료기관" },
      { name: "부민병원",     grade: "지역응급의료기관" },
      { name: "서울산보람병원", grade: "지역응급의료기관" },
      { name: "세란병원",     grade: "지역응급의료기관" },
    ]
  },
  { condition: "외상",   old_rate: "57.9%", new_rate: "38.8%", count: 19, level: "mid",
    hospitals: [
      { name: "경찰병원",               grade: "지역응급의료기관" },
      { name: "구로성심병원",            grade: "지역응급의료기관" },
      { name: "기쁨병원",               grade: "지역응급의료기관" },
      { name: "녹색병원",               grade: "지역응급의료기관" },
      { name: "대림성모병원",            grade: "지역응급의료기관" },
      { name: "명지성모병원",            grade: "지역응급의료기관" },
      { name: "부민병원",               grade: "지역응급의료기관" },
      { name: "서울산보람병원",           grade: "지역응급의료기관" },
      { name: "서울성심병원",            grade: "지역응급의료기관" },
      { name: "서울적십자병원",           grade: "지역응급의료기관" },
      { name: "서울특별시동부병원",        grade: "지역응급의료기관" },
      { name: "서울특별시서남병원",        grade: "지역응급의료기관" },
      { name: "세란병원",               grade: "지역응급의료기관" },
      { name: "의료법인동신의료재단동신병원", grade: "지역응급의료기관" },
      { name: "의료법인청구성심병원",      grade: "지역응급의료기관" },
      { name: "의료법인풍산의료재단동부제일병원", grade: "지역응급의료기관" },
      { name: "의료법인한전의료재단한일병원", grade: "지역응급의료센터" },
      { name: "한국원자력의학원원자력병원", grade: "지역응급의료기관" },
      { name: "혜민병원",               grade: "지역응급의료기관" },
    ]
  },
  { condition: "화상",   old_rate: "50.0%", new_rate: "28.0%", count: 14, level: "mid",
    hospitals: []
  },
  { condition: "고압산소", old_rate: "72.4%", new_rate: "60.0%", count: 3, level: "high",
    hospitals: [
      { name: "삼육서울병원",          grade: "지역응급의료센터" },
      { name: "서울특별시서울의료원",   grade: "권역응급의료센터" },
      { name: "의료법인한전의료재단한일병원", grade: "지역응급의료센터" },
    ]
  },
  { condition: "소아",   old_rate: "46.1%", new_rate: "10.0%", count: 3, level: "low",
    hospitals: []
  },
  { condition: "산과",   old_rate: "53.9%", new_rate: "34.0%", count: 17, level: "mid",
    hospitals: []
  },
  { condition: "신생아", old_rate: "48.7%", new_rate: "9.1%",  count: 3, level: "low",
    hospitals: []
  },
  { condition: "투석",   old_rate: "76.3%", new_rate: "59.5%", count: 25, level: "high",
    hospitals: []
  },
  { condition: "코로나19(호흡기)", old_rate: "50.0%", new_rate: "26.9%", count: 14, level: "mid",
    hospitals: []
  },
  { condition: "기타중증", old_rate: "67.1%", new_rate: "51.9%", count: 27, level: "high",
    hospitals: [
      { name: "경찰병원",               grade: "지역응급의료기관" },
      { name: "구로성심병원",            grade: "지역응급의료기관" },
      { name: "국립중앙의료원",           grade: "지역응급의료센터" },
      { name: "기쁨병원",               grade: "지역응급의료기관" },
      { name: "노원을지대학교병원",        grade: "지역응급의료센터" },
      { name: "녹색병원",               grade: "지역응급의료기관" },
      { name: "대림성모병원",            grade: "지역응급의료기관" },
      { name: "명지성모병원",            grade: "지역응급의료기관" },
      { name: "부민병원",               grade: "지역응급의료기관" },
      { name: "서울산보람병원",           grade: "지역응급의료기관" },
      { name: "서울성심병원",            grade: "지역응급의료기관" },
      { name: "서울적십자병원",           grade: "지역응급의료기관" },
      { name: "서울특별시동부병원",        grade: "지역응급의료기관" },
      { name: "서울특별시서남병원",        grade: "지역응급의료기관" },
      { name: "서울특별시서울의료원",      grade: "권역응급의료센터" },
      { name: "성애의료재단성애병원",      grade: "지역응급의료센터" },
      { name: "세란병원",               grade: "지역응급의료기관" },
      { name: "의료법인동신의료재단동신병원", grade: "지역응급의료기관" },
      { name: "의료법인서울효천의료재단에이치플러스양지병원", grade: "지역응급의료센터" },
      { name: "의료법인청구성심병원",      grade: "지역응급의료기관" },
      { name: "의료법인풍산의료재단동부제일병원", grade: "지역응급의료기관" },
      { name: "의료법인한전의료재단한일병원", grade: "지역응급의료센터" },
      { name: "이화여자대학교의과대학부속서울병원", grade: "지역응급의료센터" },
      { name: "한국원자력의학원원자력병원", grade: "지역응급의료기관" },
      { name: "혜민병원",               grade: "지역응급의료기관" },
      { name: "홍익병원",               grade: "지역응급의료기관" },
      { name: "희명병원",               grade: "지역응급의료기관" },
    ]
  },
];

function buildCapabilityTable() {
  const tbody = document.getElementById("capabilityTableBody");
  if (!tbody) return;

  CAPABILITY_DATA.forEach((row, idx) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.condition}</td>
      <td>${row.old_rate}</td>
      <td class="rate-${row.level}">${row.new_rate}</td>
      <td>${row.count}개 병원</td>
    `;
    tr.addEventListener("click", () => {
      document.querySelectorAll("#capabilityTableBody tr").forEach(r => r.classList.remove("active"));
      tr.classList.add("active");
      showHospitalDetail(row);
    });
    tbody.appendChild(tr);
  });
}

function showHospitalDetail(row) {
  const el = document.getElementById("capability-hospitals");
  if (!el) return;

  if (!row.hospitals || row.hospitals.length === 0) {
    el.innerHTML = `<p style="color:#8b949e;font-size:0.875rem;">※ ${row.condition}: 상세 병원 목록 준비 중입니다.</p>`;
    return;
  }

  el.innerHTML = `
    <h4>「${row.condition}」 — 장비가 있는데도 미공개인 병원 (${row.hospitals.length}개)</h4>
    <ul>
      ${row.hospitals.map(h => `
        <li>
          <span>${h.name}</span>
          <span class="grade-tag">${h.grade}</span>
        </li>
      `).join("")}
    </ul>
  `;
}

/* ── 초기화 ── */
document.addEventListener("DOMContentLoaded", () => {
  drawDistrictChart();
  drawCapacityChart();
  drawSearchMethodChart();
  drawNeedInfoChart();
  drawWantFeatureChart();
  buildCapabilityTable();
});
