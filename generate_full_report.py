"""
응급실 뺑뺑이 프로젝트 — 통합 EDA 리포트 생성
eda_report (섹션 1-4, 6-7) + capability_analysis (섹션 5) 를 하나로 합침
"""
import pandas as pd
import numpy as np
from datetime import datetime

# ── 데이터 로드 ──────────────────────────────────────────────────────────────
inst   = pd.read_csv("data/raw/er_institutions.csv", encoding="utf-8-sig")
real   = pd.read_csv("data/raw/er_realtime_full.csv", encoding="utf-8-sig")
detail = pd.read_csv("data/raw/er_seoul_detail.csv", encoding="utf-8-sig")

seoul_inst  = inst[inst["dutyAddr"].str.contains("서울", na=False)].copy()
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

# ── 섹션 1-4, 6 계산 (_eda_temp.py 동일) ────────────────────────────────────
gu_count = seoul_inst.groupby("gu").size().sort_values(ascending=False)
gu_grade = seoul_inst.groupby(["gu", "dutyEmclsName"]).size().unstack(fill_value=0)
grade_seoul = seoul_inst["dutyEmclsName"].value_counts()
grade_total = inst["dutyEmclsName"].value_counts()

hvec        = pd.to_numeric(seoul_real["hvec"], errors="coerce")
hvec_zero   = (hvec == 0).sum()
hvec_pos    = (hvec > 0).sum()
hvec_nan    = hvec.isna().sum()

ayn_cols = [c for c in real.columns if c.endswith("ayn")]
ayn_rows = []
for col in ayn_cols:
    y  = (seoul_real[col] == "Y").sum()
    n1 = (seoul_real[col] == "N1").sum()
    n  = (seoul_real[col] == "N").sum()
    ayn_rows.append({"항목": AYN_LABELS.get(col, col), "가능(Y)": y, "일시불가(N1)": n1, "불가(N)": n})
ayn_df = pd.DataFrame(ayn_rows)

# ── 섹션 5: 능력 기반 미공개 분석 ────────────────────────────────────────────
merged = detail.merge(real[["hpid"] + ayn_cols], on="hpid", how="left")
merged = merged.merge(inst[["hpid", "dutyEmclsName"]], on="hpid", how="left")

CAPABILITY_MAP = {
    "MKioskTy1":  {"label": "뇌졸중",          "rules": [("hvctayn","Y"),("hvmriayn","Y")],                        "logic": "OR"},
    "MKioskTy2":  {"label": "심근경색",         "rules": [("hvangioayn","Y")],                                     "logic": "OR"},
    "MKioskTy3":  {"label": "외상",             "rules": [("hvventiayn","Y"),("hpopyn",">0")],                     "logic": "AND"},
    "MKioskTy4":  {"label": "화상",             "rules": [("hpopyn",">0")],                                        "logic": "OR"},
    "MKioskTy5":  {"label": "고압산소",         "rules": [("hvoxyayn","Y")],                                       "logic": "OR"},
    "MKioskTy6":  {"label": "정신과",           "rules": [],                                                       "logic": "OR"},
    "MKioskTy7":  {"label": "소아",             "rules": [("hvventisoayn","Y"),("hvincuayn","Y")],                  "logic": "OR"},
    "MKioskTy8":  {"label": "산과",             "rules": [("hpopyn",">0")],                                        "logic": "OR"},
    "MKioskTy9":  {"label": "신생아",           "rules": [("hvincuayn","Y"),("hpnicuyn",">0")],                    "logic": "OR"},
    "MKioskTy10": {"label": "투석",             "rules": [("hvcrrtayn","Y")],                                      "logic": "OR"},
    "MKioskTy11": {"label": "코로나19(호흡기)", "rules": [("hvventiayn","Y")],                                     "logic": "OR"},
    "MKioskTy25": {"label": "기타중증",         "rules": [("hvecmoayn","Y"),("hvventiayn","Y"),("hpicuyn",">0")],  "logic": "OR"},
}

def has_capability(row, rules, logic):
    if not rules:
        return None
    results = []
    for col, cond in rules:
        val = row.get(col)
        if pd.isna(val):
            results.append(False)
        elif cond == "Y":
            results.append(str(val).strip() == "Y")
        elif cond == ">0":
            try:
                results.append(float(val) > 0)
            except (ValueError, TypeError):
                results.append(False)
    return any(results) if logic == "OR" else all(results)

def is_blank(val):
    return pd.isna(val) or str(val).strip() == ""

cap_rows   = []
detail_rows = []

for mk_col, cfg in CAPABILITY_MAP.items():
    if mk_col not in merged.columns:
        continue
    label, rules, logic = cfg["label"], cfg["rules"], cfg["logic"]

    # 기존 방식 (76개 전체)
    total_76 = len(merged)
    blank_76 = merged[mk_col].apply(is_blank).sum()
    rate_76  = round(blank_76 / total_76 * 100, 1)

    # 새 방식 (능력 있는 병원만)
    rt_mask   = merged["hpid"].isin(seoul_real["hpid"])
    merged_rt = merged[rt_mask].copy()

    if not rules:
        cap_rows.append({
            "중증질환": label, "기존_미공개(76)": blank_76, "기존율(%)": rate_76,
            "능력있는병원": "지표없음", "능력+공백": "지표없음", "설명불가율(%)": "—",
        })
        continue

    merged_rt["_cap"] = merged_rt.apply(lambda r: has_capability(r, rules, logic), axis=1)
    capable       = merged_rt[merged_rt["_cap"] == True]
    capable_blank = capable[capable[mk_col].apply(is_blank)]
    cap_n, cap_b  = len(capable), len(capable_blank)
    cap_rate      = round(cap_b / cap_n * 100, 1) if cap_n > 0 else 0.0

    cap_rows.append({
        "중증질환": label, "기존_미공개(76)": blank_76, "기존율(%)": rate_76,
        "능력있는병원": cap_n, "능력+공백": cap_b, "설명불가율(%)": cap_rate,
    })
    for _, r in capable_blank.iterrows():
        detail_rows.append({
            "중증질환": label,
            "병원명": r.get("dutyName", r["hpid"]),
            "등급": r.get("dutyEmclsName", ""),
            "근거": ", ".join(f"{c}={r.get(c,'?')}" for c, _ in rules),
        })

cap_df    = pd.DataFrame(cap_rows)
detail_df = pd.DataFrame(detail_rows) if detail_rows else pd.DataFrame()

# ── Markdown 작성 ─────────────────────────────────────────────────────────────
L = []

L.append("# 응급실 뺑뺑이 프로젝트 — 공공데이터 EDA")
L.append(f"\n> 수집·분석일시: {datetime.now().strftime('%Y-%m-%d %H:%M')}  ")
L.append("> 출처: 공공데이터포털 국립응급의료원_전국 응급의료기관 정보 조회 서비스  ")
L.append("> 분석 대상: 서울특별시 응급의료기관\n")
L.append("---\n")

# 1. 데이터 개요
L.append("## 1. 데이터 개요\n")
L.append(f"- 전국 응급의료기관: **{len(inst)}곳**")
L.append(f"- 서울 응급의료기관: **{len(seoul_inst)}곳**")
L.append(f"- 실시간 가용병상 수집: **{len(real)}곳** (전국 기준, 서울 {len(seoul_real)}곳)\n")
L.append("### 전국 vs 서울 기관 등급 분포\n")
L.append("| 등급 | 전국 | 서울 |")
L.append("|---|---|---|")
for grade in grade_total.index:
    L.append(f"| {grade} | {grade_total.get(grade,0)} | {grade_seoul.get(grade,0)} |")
L.append("")

# 2. 구별 분포
L.append("## 2. 서울 구별 응급실 분포\n")
L.append("| 자치구 | 응급실 수 |")
L.append("|---|---|")
for gu, cnt in gu_count.items():
    L.append(f"| {gu} | {cnt} |")
L.append("")

# 3. 가용 병상
L.append("## 3. 실시간 응급실 가용 병상 현황 (수집 시점 기준)\n")
L.append(f"- 병상 있음 (hvec > 0): **{hvec_pos}개 병원**")
L.append(f"- 병상 0: **{hvec_zero}개 병원**")
L.append(f"- 데이터 없음: **{hvec_nan}개 병원**")
L.append(f"- 최대 가용 병상: **{int(hvec.max()) if not hvec.isna().all() else 0}개**")
L.append(f"- 중앙값: **{float(hvec.median()) if not hvec.isna().all() else 0}개**\n")
L.append("> ⚠️ 실시간 데이터로, 실행 시점에 따라 값이 달라집니다.\n")

# 4. 장비 가용 여부
L.append("## 4. 장비 및 처치 가용 여부 (서울 응급실 실시간)\n")
L.append(f"총 {len(seoul_real)}개 병원 기준\n")
L.append("| 항목 | 가능(Y) | 일시불가(N1) | 불가(N) |")
L.append("|---|---|---|---|")
for _, row in ayn_df.iterrows():
    L.append(f"| {row['항목']} | {row['가능(Y)']} | {row['일시불가(N1)']} | {row['불가(N)']} |")
L.append("")
L.append("> `N1` = 일시적 불가 (장비 점검·포화 등), `N` = 해당 장비 없음\n")

# 5. 중증질환 미공개 — 능력 기반
L.append("## 5. 중증질환별 수용 여부 미공개 분석\n")
L.append("> **방법론**: 단순 공백 카운트(기존) vs 장비·시설 보유 증거가 있는 병원 중 공백인 경우(설명불가)  ")
L.append(f"> 능력 기반 분석 가능 병원: 53개 (realtime 교집합) / 능력 판단 불가: 23개\n")
L.append("| 중증질환 | 기존 미공개 | 기존율 | 능력있는 병원 | 능력+공백 | **설명불가율** |")
L.append("|---|---|---|---|---|---|")
for _, r in cap_df.iterrows():
    if r["설명불가율(%)"] == "—":
        L.append(f"| {r['중증질환']} | {r['기존_미공개(76)']} | {r['기존율(%)']}% | — | — | — *(장비지표 없음)* |")
    else:
        new = r["설명불가율(%)"]
        old = r["기존율(%)"]
        arrow = "▼" if new < old else "▲"
        L.append(f"| {r['중증질환']} | {r['기존_미공개(76)']} | {old}% | {r['능력있는병원']} | {r['능력+공백']} | **{new}%** {arrow} |")
L.append("")

L.append("### 5-1. 설명 불가능한 미공개 — 병원별 상세\n")
L.append("> 장비·시설 보유 증거가 있음에도 수용 여부를 공개하지 않는 병원\n")
if not detail_df.empty:
    for disease, group in detail_df.groupby("중증질환"):
        L.append(f"#### {disease} ({len(group)}개 병원)\n")
        L.append("| 병원명 | 등급 | 능력 근거 |")
        L.append("|---|---|---|")
        for _, r in group.iterrows():
            L.append(f"| {r['병원명']} | {r['등급']} | {r['근거']} |")
        L.append("")

L.append("### 5-2. 능력 지표 매핑 기준\n")
L.append("| 중증질환 | 능력 지표 |")
L.append("|---|---|")
for mk_col, cfg in CAPABILITY_MAP.items():
    if cfg["rules"]:
        rules_str = f" {cfg['logic']} ".join(r[0] for r in cfg["rules"])
        L.append(f"| {cfg['label']} | {rules_str} |")
    else:
        L.append(f"| {cfg['label']} | — (장비 지표 없음, 분석 제외) |")
L.append("")

# 6. 구별×등급
L.append("## 6. 서울 구별 × 기관 등급 상세\n")
gu_g = gu_grade.reset_index()
header_cols = ["자치구"] + [c for c in gu_g.columns if c != "gu"]
L.append("| " + " | ".join(header_cols) + " |")
L.append("|" + "---|" * len(header_cols))
for _, row in gu_g.iterrows():
    vals = [str(row["gu"])] + [str(row[c]) for c in gu_g.columns if c != "gu"]
    L.append("| " + " | ".join(vals) + " |")
L.append("")

# 7. 파일 구조
L.append("## 7. 수집 파일 구조\n")
L.append("```")
L.append("data/raw/")
L.append("├── er_institutions.csv    # 전국 534개 기관 목록 (기관명/주소/좌표/등급)")
L.append("├── er_realtime_full.csv   # 실시간 가용병상 + 장비 가용 여부 (전국 418개)")
L.append("└── er_seoul_detail.csv    # 서울 76개 병원 중증질환 Y/N/정보미공개")
L.append("```\n")

# 8. 뺑뺑이의 구조적 원인 분석
L.append("## 8. 뺑뺑이의 구조적 원인 분석\n")
L.append("> 데이터에서 도출한 인과 구조. 세 층위가 맞물려 뺑뺑이를 발생시킨다.\n")

L.append("### 1순위: 정보 비대칭 — 직접 원인\n")
L.append("뺑뺑이의 핵심 메커니즘은 **구급대원이 수용 가능 병원을 전화로 확인하는 시간**이 골든타임을 잠식하는 것이다.")
L.append("실시간 공개 데이터가 있으면 이 과정이 생략되지만, 현재는 능력이 있는 병원조차 공개하지 않는다.\n")

# 정보 비대칭 핵심 수치 동적 계산
info_rows = cap_df[cap_df["설명불가율(%)"] != "—"].copy()
info_rows["설명불가율(%)"] = pd.to_numeric(info_rows["설명불가율(%)"], errors="coerce")
top3 = info_rows.nlargest(3, "설명불가율(%)")

L.append("**설명불가 미공개율 상위 항목**\n")
L.append("| 중증질환 | 능력있는 병원 | 미공개 | 설명불가율 |")
L.append("|---|---|---|---|")
for _, r in top3.iterrows():
    L.append(f"| {r['중증질환']} | {r['능력있는병원']}개 | {r['능력+공백']}개 | **{r['설명불가율(%)']}%** |")
L.append("")

# 공공병원 미공개 케이스 집계
public_hospitals = ["서울특별시서울의료원", "국립중앙의료원"]
public_cases = detail_df[detail_df["병원명"].isin(public_hospitals)].groupby("병원명")["중증질환"].apply(list)

L.append("**공개 의무 부재의 단면 — 공공병원 미공개 현황**\n")
L.append("| 병원명 | 등급 | 미공개 항목 |")
L.append("|---|---|---|")
for hosp, diseases in public_cases.items():
    grade = detail_df[detail_df["병원명"] == hosp]["등급"].iloc[0]
    L.append(f"| {hosp} | {grade} | {', '.join(diseases)} |")
L.append("")
L.append("> 공공병원도 미공개하는 것은 **공개를 강제하는 제도적 장치가 없음**을 시사한다.\n")

L.append("### 2순위: 공급 절대 부족 — 구조 원인\n")
L.append("정보가 완전히 공개되더라도 실제로 빈 자리가 없는 상황이 반복된다.\n")
L.append(f"- 서울 응급실 가용 병상 **중앙값 {float(hvec.median()):.0f}개**, 최대 {int(hvec.max())}개")
L.append(f"- 병상 0개인 병원: **{hvec_zero}개**")

ecmo_y  = (seoul_real["hvecmoayn"] == "Y").sum()
ecmo_n1 = (seoul_real["hvecmoayn"] == "N1").sum()
oxy_y   = (seoul_real["hvoxyayn"] == "Y").sum()
L.append(f"- ECMO 일시불가(N1): {ecmo_n1}개 병원 — 가능(Y) {ecmo_y}개 대비 포화 비율 높음")
L.append(f"- 고압산소 가능 병원: 서울 전체에서 **{oxy_y}개**뿐\n")
L.append("> 정보 투명성이 개선되더라도, 보낼 곳 자체가 부족한 구조 문제는 별도로 해결이 필요하다.\n")

L.append("### 3순위: 지리적 불균형 — 불평등 원인\n")
L.append("거주 지역에 따라 접근 가능한 응급의료 수준이 구조적으로 다르다.\n")

# 권역·지역센터 없는 구 계산
권역 = gu_grade.get("권역응급의료센터", pd.Series(dtype=int)).fillna(0)
지역 = gu_grade.get("지역응급의료센터", pd.Series(dtype=int)).fillna(0)
no_center = gu_grade[(권역 == 0) & (지역 == 0)].index.tolist()

신고기관 = gu_grade.get("응급실운영신고기관", pd.Series(dtype=int)).fillna(0)
total_by_gu = gu_grade.sum(axis=1)
only_신고 = gu_grade[(권역 == 0) & (지역 == 0) & (gu_grade.get("지역응급의료기관", pd.Series(dtype=int)).fillna(0) == 0)].index.tolist()

L.append("| 자치구 | 권역센터 | 지역센터 | 신고기관 비율 | 비고 |")
L.append("|---|---|---|---|---|")
vulnerable = ["강북구", "마포구", "도봉구", "성북구", "금천구"]
for gu in vulnerable:
    if gu in gu_grade.index:
        row = gu_grade.loc[gu]
        total = total_by_gu.loc[gu]
        singobi = row.get("응급실운영신고기관", 0)
        kwon = row.get("권역응급의료센터", 0)
        jiyeok = row.get("지역응급의료센터", 0)
        ratio = f"{singobi/total*100:.0f}%" if total > 0 else "—"
        note = "권역·지역센터 없음" if kwon == 0 and jiyeok == 0 else ""
        L.append(f"| {gu} | {kwon} | {jiyeok} | {ratio} | {note} |")
L.append("")
L.append("> 강북구는 응급실 3개 모두 최하위 등급(신고기관). 중증 환자는 구를 벗어나야 한다.\n")

L.append("---\n")
L.append("## 9. 액티비즘 우선순위\n")
L.append("| 순위 | 원인 | 핵심 주장 | 요구 가능한 변화 |")
L.append("|---|---|---|---|")
L.append("| **1** | 정보 비대칭 | 공개 의무가 없으니 공공병원도 안 한다 | MKiosk 공개 의무 법제화 |")
L.append("| **2** | 공급 부족 | 병상 중앙값 7개 — 정보가 있어도 보낼 곳이 없다 | 응급 병상 확충 예산 |")
L.append("| **3** | 지리 불균형 | 강북구는 구조적으로 불리하다 | 취약 지역 응급센터 지정 |")
L.append("")
L.append("> **1순위가 가장 즉각적인 변화를 요구할 수 있다.** 예산·인프라 없이 제도 하나로 해결 가능한 문제다.\n")

L.append("---")
L.append("> 분석 스크립트: `fetch_api.py` / EDA: `generate_full_report.py`")

md = "\n".join(L)
with open("full_eda_report.md", "w", encoding="utf-8") as f:
    f.write(md)

print("저장 완료: full_eda_report.md")
