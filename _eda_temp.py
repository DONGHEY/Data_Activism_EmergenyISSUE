import pandas as pd
import numpy as np
from datetime import datetime

inst   = pd.read_csv("data/raw/er_institutions.csv", encoding="utf-8-sig")
real   = pd.read_csv("data/raw/er_realtime_full.csv", encoding="utf-8-sig")
detail = pd.read_csv("data/raw/er_seoul_detail.csv", encoding="utf-8-sig")

# 서울 기관 필터
seoul_inst = inst[inst["dutyAddr"].str.contains("서울", na=False)].copy()
seoul_inst["gu"] = seoul_inst["dutyAddr"].str.extract(r"서울특별시\s+(\S+구)")
seoul_hpids = seoul_inst["hpid"].tolist()
seoul_real  = real[real["hpid"].isin(seoul_hpids)].copy()

MKIOSK_LABELS = {
    "MKioskTy1": "뇌졸중",    "MKioskTy2": "심근경색",  "MKioskTy3": "외상",
    "MKioskTy4": "화상",       "MKioskTy5": "고압산소",  "MKioskTy6": "정신과",
    "MKioskTy7": "소아",       "MKioskTy8": "산과",      "MKioskTy9": "신생아",
    "MKioskTy10": "투석",      "MKioskTy11": "코로나19(호흡기)", "MKioskTy25": "기타중증",
}
AYN_LABELS = {
    "hvangioayn": "혈관조영술",  "hvcrrtayn": "CRRT(지속신대체)",
    "hvctayn": "CT",            "hvecmoayn": "ECMO(체외막산소화)",
    "hvhypoayn": "저체온치료",   "hvincuayn": "인큐베이터",
    "hvmriayn": "MRI",          "hvoxyayn": "고압산소",
    "hvventiayn": "인공호흡기",  "hvventisoayn": "인공호흡기(소아)",
}
GRADE_LABELS = {
    "권역응급의료센터": "권역응급의료센터",
    "지역응급의료센터": "지역응급의료센터",
    "지역응급의료기관": "지역응급의료기관",
    "의원급응급의료기관": "의원급응급의료기관",
}

# ─── 1. 구별 응급실 분포 ───────────────────────────────────────────────
gu_count = seoul_inst.groupby("gu").size().sort_values(ascending=False)
gu_grade = seoul_inst.groupby(["gu", "dutyEmclsName"]).size().unstack(fill_value=0)

# ─── 2. 등급별 분포 ───────────────────────────────────────────────────
grade_seoul = seoul_inst["dutyEmclsName"].value_counts()
grade_total = inst["dutyEmclsName"].value_counts()

# ─── 3. 실시간 가용 병상 (hvec) ──────────────────────────────────────
hvec = pd.to_numeric(seoul_real["hvec"], errors="coerce")
hvec_zero  = (hvec == 0).sum()
hvec_pos   = (hvec > 0).sum()
hvec_nan   = hvec.isna().sum()
hvec_total = len(seoul_real)

# ─── 4. 장비/처치 가용 여부 (ayn 계열) ─────────────────────────────────
ayn_cols = [c for c in real.columns if c.endswith("ayn")]
ayn_rows = []
for col in ayn_cols:
    y  = (seoul_real[col] == "Y").sum()
    n1 = (seoul_real[col] == "N1").sum()
    n  = (seoul_real[col] == "N").sum()
    ayn_rows.append({"항목": AYN_LABELS.get(col, col), "가능(Y)": y, "일시불가(N1)": n1, "불가(N)": n})
ayn_df = pd.DataFrame(ayn_rows)

# ─── 5. 중증질환 Y/N/정보미공개 ─────────────────────────────────────────
mk_cols  = [c for c in detail.columns if c.startswith("MKiosk")]
total_76 = len(detail)
mk_rows  = []
for col in mk_cols:
    y    = (detail[col] == "Y").sum()
    n    = (detail[col] == "N").sum()
    n1   = (detail[col] == "N1").sum()
    miss = detail[col].isna().sum()
    mk_rows.append({
        "중증질환": MKIOSK_LABELS.get(col, col),
        "수용가능(Y)": y,
        "N1": n1,
        "수용불가(N)": n,
        "정보미공개": miss,
        "정보미공개율(%)": round(miss / total_76 * 100, 1),
    })
mk_df = pd.DataFrame(mk_rows).sort_values("정보미공개율(%)", ascending=False)

# ─── 결과를 dict로 패키징 ────────────────────────────────────────────────
results = {
    "total_national": len(inst),
    "total_seoul": len(seoul_inst),
    "grade_seoul": grade_seoul,
    "grade_total": grade_total,
    "gu_count": gu_count,
    "gu_grade": gu_grade,
    "hvec_zero": hvec_zero,
    "hvec_pos": hvec_pos,
    "hvec_nan": hvec_nan,
    "hvec_total": hvec_total,
    "hvec_max": int(hvec.max()) if not hvec.isna().all() else 0,
    "hvec_median": float(hvec.median()) if not hvec.isna().all() else 0,
    "ayn_df": ayn_df,
    "mk_df": mk_df,
    "total_76": total_76,
}

# ─── Markdown 생성 ───────────────────────────────────────────────────────
lines = []

lines.append("# 응급실 뺑뺑이 프로젝트 — 공공데이터 EDA 요약")
lines.append(f"\n> 수집일시: {datetime.now().strftime('%Y-%m-%d %H:%M')}  ")
lines.append("> 출처: 공공데이터포털 국립응급의료원_전국 응급의료기관 정보 조회 서비스  ")
lines.append("> 분석 대상: 서울특별시 응급의료기관\n")
lines.append("---\n")

# ── 1. 데이터 개요
lines.append("## 1. 데이터 개요\n")
lines.append(f"- 전국 응급의료기관: **{results['total_national']}곳**")
lines.append(f"- 서울 응급의료기관: **{results['total_seoul']}곳**")
lines.append(f"- 실시간 가용병상 수집: **{len(real)}곳** (전국 기준, 서울 {len(seoul_real)}곳)\n")

lines.append("### 전국 vs 서울 기관 등급 분포\n")
lines.append("| 등급 | 전국 | 서울 |")
lines.append("|---|---|---|")
for grade in results["grade_total"].index:
    total_n = results["grade_total"].get(grade, 0)
    seoul_n = results["grade_seoul"].get(grade, 0)
    lines.append(f"| {grade} | {total_n} | {seoul_n} |")
lines.append("")

# ── 2. 서울 구별 분포
lines.append("## 2. 서울 구별 응급실 분포\n")
lines.append("| 자치구 | 응급실 수 |")
lines.append("|---|---|")
for gu, cnt in results["gu_count"].items():
    lines.append(f"| {gu} | {cnt} |")
lines.append("")
lines.append("> **노원구**: 3개 응급의료기관 (경희대학교병원, 을지서울병원, 한국원자력의학원서울원자력병원)\n")

# ── 3. 실시간 가용 병상
lines.append("## 3. 실시간 응급실 가용 병상 현황 (수집 시점 기준)\n")
lines.append(f"- 병상 있음 (hvec > 0): **{results['hvec_pos']}개 병원**")
lines.append(f"- 병상 0: **{results['hvec_zero']}개 병원**")
lines.append(f"- 데이터 없음: **{results['hvec_nan']}개 병원**")
lines.append(f"- 최대 가용 병상: **{results['hvec_max']}개**")
lines.append(f"- 중앙값: **{results['hvec_median']}개**\n")
lines.append("> ⚠️ 실시간 데이터로, 실행 시점에 따라 값이 달라집니다.\n")

# ── 4. 장비/처치 가용 여부
lines.append("## 4. 장비 및 처치 가용 여부 (서울 응급실 실시간)\n")
lines.append(f"총 {len(seoul_real)}개 병원 기준\n")
lines.append("| 항목 | 가능(Y) | 일시불가(N1) | 불가(N) |")
lines.append("|---|---|---|---|")
for _, row in results["ayn_df"].iterrows():
    lines.append(f"| {row['항목']} | {row['가능(Y)']} | {row['일시불가(N1)']} | {row['불가(N)']} |")
lines.append("")
lines.append("> `N1` = 일시적 불가 (장비 점검·포화 등), `N` = 해당 장비 없음\n")

# ── 5. 중증질환 수용가능 여부 (핵심!)
lines.append("## 5. 중증질환별 수용가능 여부 — 정보 접근성 핵심 데이터\n")
lines.append(f"서울 **{results['total_76']}개 병원** 기준\n")
lines.append("| 중증질환 | 수용가능(Y) | N1 | 수용불가(N) | 정보미공개 | 정보미공개율 |")
lines.append("|---|---|---|---|---|---|")
for _, row in results["mk_df"].iterrows():
    bar = "█" * int(row["정보미공개율(%)"] / 10)
    lines.append(
        f"| {row['중증질환']} | {row['수용가능(Y)']} | {row['N1']} | {row['수용불가(N)']} "
        f"| {row['정보미공개']} | {row['정보미공개율(%)']}% {bar} |"
    )
lines.append("")

# 요약 인사이트
highest = results["mk_df"].iloc[0]
lowest  = results["mk_df"].iloc[-1]
lines.append("### 핵심 인사이트\n")
lines.append(
    f"- 정보미공개율 **최고**: {highest['중증질환']} — "
    f"{highest['정보미공개']}개 병원({highest['정보미공개율(%)']}%)이 정보를 공개하지 않음"
)
lines.append(
    f"- 정보미공개율 **최저**: {lowest['중증질환']} — "
    f"그래도 {lowest['정보미공개']}개 병원({lowest['정보미공개율(%)']}%)이 미공개"
)
lines.append(
    f"- **절반 이상**의 병원이 중증질환 수용 여부를 비공개하는 항목이 "
    f"{(results['mk_df']['정보미공개율(%)'] >= 50).sum()}개 / {len(mk_cols)}개"
)
lines.append("")

# ── 6. 구별 등급 분포 표
lines.append("## 6. 서울 구별 × 기관 등급 상세\n")
gu_g = results["gu_grade"].reset_index()
header_cols = ["자치구"] + [c for c in gu_g.columns if c != "gu"]
lines.append("| " + " | ".join(header_cols) + " |")
lines.append("|" + "---|" * len(header_cols))
for _, row in gu_g.iterrows():
    vals = [str(row["gu"])] + [str(row[c]) for c in gu_g.columns if c != "gu"]
    lines.append("| " + " | ".join(vals) + " |")
lines.append("")

# ── 7. 파일 구조
lines.append("## 7. 수집 파일 구조\n")
lines.append("```")
lines.append("data/raw/")
lines.append("├── er_institutions.csv    # 전국 534개 기관 목록 (기관명/주소/좌표/등급)")
lines.append("├── er_realtime_full.csv   # 실시간 가용병상 + 장비 가용 여부 (전국 418개)")
lines.append("└── er_seoul_detail.csv    # 서울 76개 병원 중증질환 Y/N/정보미공개")
lines.append("```\n")

lines.append("---")
lines.append("> 분석 스크립트: `fetch_api.py` / EDA: `_eda_temp.py`")

md = "\n".join(lines)
with open("eda_report.md", "w", encoding="utf-8") as f:
    f.write(md)

print("EDA 리포트 저장 완료: eda_report.md")
print(f"총 {len(lines)}줄")
