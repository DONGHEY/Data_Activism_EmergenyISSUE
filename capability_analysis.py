"""
능력 지표 기반 미공개 분석
- 기존: 76개 전체에서 MKiosk 공백 = 미공개
- 새 방식: 능력 증거가 있는 병원 중 MKiosk 공백인 경우만 '설명 불가능한 미공개'
"""
import pandas as pd
from datetime import datetime

inst   = pd.read_csv("data/raw/er_institutions.csv", encoding="utf-8-sig")
real   = pd.read_csv("data/raw/er_realtime_full.csv", encoding="utf-8-sig")
detail = pd.read_csv("data/raw/er_seoul_detail.csv", encoding="utf-8-sig")

# 서울 기관 필터
seoul_hpids = set(inst[inst["dutyAddr"].str.contains("서울", na=False)]["hpid"])
real_seoul  = real[real["hpid"].isin(seoul_hpids)].copy()

# detail + realtime 병합 (교집합 53개)
ayn_cols = [c for c in real.columns if c.endswith("ayn")]
merged = detail.merge(
    real_seoul[["hpid"] + ayn_cols],
    on="hpid", how="left"
)
# 등급 정보 붙이기 (병원명은 detail에 이미 있음)
merged = merged.merge(inst[["hpid", "dutyEmclsName"]], on="hpid", how="left")

# ── 능력 지표 → MKiosk 매핑 ──────────────────────────────────────────────────
# 각 중증질환에 대해: "어떤 컬럼이 어떤 값이면 능력이 있다고 본다"
CAPABILITY_MAP = {
    "MKioskTy1":  {  # 뇌졸중
        "label": "뇌졸중",
        "rules": [("hvctayn", "Y"), ("hvmriayn", "Y")],   # CT 또는 MRI 보유
        "logic": "OR",
    },
    "MKioskTy2":  {  # 심근경색
        "label": "심근경색",
        "rules": [("hvangioayn", "Y")],                    # 혈관조영술
        "logic": "OR",
    },
    "MKioskTy3":  {  # 외상
        "label": "외상",
        "rules": [("hvventiayn", "Y"), ("hpopyn", ">0")],  # 인공호흡기 AND 수술실
        "logic": "AND",
    },
    "MKioskTy4":  {  # 화상
        "label": "화상",
        "rules": [("hpopyn", ">0")],                       # 수술실
        "logic": "OR",
    },
    "MKioskTy5":  {  # 고압산소
        "label": "고압산소",
        "rules": [("hvoxyayn", "Y")],                      # 고압산소 장비
        "logic": "OR",
    },
    "MKioskTy6":  {  # 정신과
        "label": "정신과",
        "rules": [],                                        # 장비 지표 없음
        "logic": "OR",
    },
    "MKioskTy7":  {  # 소아
        "label": "소아",
        "rules": [("hvventisoayn", "Y"), ("hvincuayn", "Y")],  # 소아 인공호흡기 또는 인큐베이터
        "logic": "OR",
    },
    "MKioskTy8":  {  # 산과
        "label": "산과",
        "rules": [("hpopyn", ">0")],                       # 수술실
        "logic": "OR",
    },
    "MKioskTy9":  {  # 신생아
        "label": "신생아",
        "rules": [("hvincuayn", "Y"), ("hpnicuyn", ">0")], # 인큐베이터 또는 신생아 ICU
        "logic": "OR",
    },
    "MKioskTy10": {  # 투석
        "label": "투석",
        "rules": [("hvcrrtayn", "Y")],                     # CRRT
        "logic": "OR",
    },
    "MKioskTy11": {  # 코로나19(호흡기)
        "label": "코로나19(호흡기)",
        "rules": [("hvventiayn", "Y")],                    # 인공호흡기
        "logic": "OR",
    },
    "MKioskTy25": {  # 기타중증
        "label": "기타중증",
        "rules": [("hvecmoayn", "Y"), ("hvventiayn", "Y"), ("hpicuyn", ">0")],
        "logic": "OR",
    },
}

def has_capability(row, rules, logic):
    """능력 증거 여부 판단"""
    if not rules:
        return None  # 판단 불가

    results = []
    for col, condition in rules:
        val = row.get(col)
        if pd.isna(val):
            results.append(False)
        elif condition == "Y":
            results.append(str(val).strip() == "Y")
        elif condition == ">0":
            try:
                results.append(float(val) > 0)
            except (ValueError, TypeError):
                results.append(False)

    if logic == "OR":
        return any(results)
    else:  # AND
        return all(results)

def is_blank(val):
    return pd.isna(val) or str(val).strip() == ""

# ── 분석 실행 ────────────────────────────────────────────────────────────────
rows = []
detail_rows = []  # 병원별 상세 (능력 있는데 공백인 케이스)

for mk_col, cfg in CAPABILITY_MAP.items():
    if mk_col not in merged.columns:
        continue

    label    = cfg["label"]
    rules    = cfg["rules"]
    logic    = cfg["logic"]
    no_indicator = len(rules) == 0

    # 전체 76개 기준 (기존 방식)
    total_76    = len(merged)
    blank_76    = merged[mk_col].apply(is_blank).sum()
    rate_76     = round(blank_76 / total_76 * 100, 1)

    # 새 방식: realtime 있는 53개 중 능력 판단
    has_rt = merged[ayn_cols[0]].notna() | merged[ayn_cols[0]].isna()
    rt_mask = merged["hpid"].isin(real_seoul["hpid"])
    merged_rt = merged[rt_mask].copy()

    if no_indicator:
        rows.append({
            "중증질환": label,
            "기존_미공개(76기준)": blank_76,
            "기존_미공개율": rate_76,
            "능력있는병원수": "지표없음",
            "능력있는데공백": "지표없음",
            "설명불가_미공개율": "지표없음",
            "비고": "장비 지표 없음 — 분석 제외",
        })
        continue

    # 능력 있는 병원 찾기
    merged_rt["_has_cap"] = merged_rt.apply(
        lambda r: has_capability(r, rules, logic), axis=1
    )
    capable = merged_rt[merged_rt["_has_cap"] == True]
    capable_blank = capable[capable[mk_col].apply(is_blank)]

    cap_n     = len(capable)
    cap_blank = len(capable_blank)
    cap_rate  = round(cap_blank / cap_n * 100, 1) if cap_n > 0 else 0.0

    rows.append({
        "중증질환": label,
        "기존_미공개(76기준)": blank_76,
        "기존_미공개율(%)": rate_76,
        "능력있는병원수": cap_n,
        "능력있는데공백": cap_blank,
        "설명불가_미공개율(%)": cap_rate,
        "비고": f"능력지표: {', '.join(r[0] for r in rules)}",
    })

    # 병원별 상세
    for _, r in capable_blank.iterrows():
        detail_rows.append({
            "중증질환": label,
            "병원명": r.get("dutyName", r["hpid"]),
            "등급": r.get("dutyEmclsName", ""),
            "능력지표근거": ", ".join(
                f"{col}={r.get(col,'?')}" for col, _ in rules
            ),
        })

result_df = pd.DataFrame(rows)
detail_df = pd.DataFrame(detail_rows) if detail_rows else pd.DataFrame()

# ── Markdown 리포트 ──────────────────────────────────────────────────────────
lines = []
lines.append("# 능력 지표 기반 미공개 분석")
lines.append(f"\n> 분석일시: {datetime.now().strftime('%Y-%m-%d %H:%M')}  ")
lines.append("> 방법론: 장비·시설 보유 증거가 있는 병원 중 MKiosk 공백인 경우만 '설명 불가능한 미공개'로 정의\n")
lines.append("---\n")

lines.append("## 1. 데이터 구조 요약\n")
lines.append(f"- `er_seoul_detail.csv`: 서울 **76개** 병원 (MKiosk 중증질환 수용 여부)")
lines.append(f"- `er_realtime_full.csv`: 전국 418개 중 서울 **53개** 병원 (장비 가용 여부)")
lines.append(f"- 교집합: **53개** — 이 병원들만 능력 기반 분석 가능")
lines.append(f"- realtime 없는 23개: 능력 판단 불가 → 분석 제외\n")

lines.append("## 2. 기존 vs 새 방식 비교\n")
lines.append("> 기존: 76개 전체 분모 / 새 방식: 해당 능력 지표가 있는 병원 분모\n")
lines.append("| 중증질환 | 기존 미공개 | 기존 미공개율 | 능력있는 병원 | 능력있는데 공백 | **설명불가 미공개율** |")
lines.append("|---|---|---|---|---|---|")

for _, r in result_df.iterrows():
    if r["설명불가_미공개율(%)"] == "지표없음":
        lines.append(
            f"| {r['중증질환']} | {r['기존_미공개(76기준)']} | {r['기존_미공개율(%)']}% "
            f"| — | — | — *(지표없음)* |"
        )
    else:
        old_rate = r["기존_미공개율(%)"]
        new_rate = r["설명불가_미공개율(%)"]
        arrow = "▼" if new_rate < old_rate else "▲"
        lines.append(
            f"| {r['중증질환']} | {r['기존_미공개(76기준)']} | {old_rate}% "
            f"| {r['능력있는병원수']} | {r['능력있는데공백']} | **{new_rate}%** {arrow} |"
        )

lines.append("")

lines.append("## 3. 설명 불가능한 미공개 — 병원별 상세\n")
lines.append("> 장비/시설 보유 증거가 있음에도 수용 여부를 공개하지 않는 병원\n")

if not detail_df.empty:
    by_disease = detail_df.groupby("중증질환")
    for disease, group in by_disease:
        lines.append(f"### {disease} ({len(group)}개 병원)\n")
        lines.append("| 병원명 | 등급 | 능력 근거 |")
        lines.append("|---|---|---|")
        for _, r in group.iterrows():
            lines.append(f"| {r['병원명']} | {r['등급']} | {r['능력지표근거']} |")
        lines.append("")

lines.append("## 4. 방법론 주석\n")
lines.append("| 중증질환 | 능력 지표 | 근거 |")
lines.append("|---|---|---|")
for mk_col, cfg in CAPABILITY_MAP.items():
    if cfg["rules"]:
        rules_str = " {} ".format(cfg["logic"]).join(r[0] for r in cfg["rules"])
        lines.append(f"| {cfg['label']} | {rules_str} | 해당 장비 보유 = 처치 가능 |")
    else:
        lines.append(f"| {cfg['label']} | — | 객관적 장비 지표 없음 (분석 제외) |")
lines.append("")

lines.append("---")
lines.append("> 분석 스크립트: `capability_analysis.py`")

md = "\n".join(lines)
with open("capability_report.md", "w", encoding="utf-8") as f:
    f.write(md)

print("저장 완료: capability_report.md")
print("\n[기존 vs 새 방식 요약]")
print(result_df[["중증질환", "기존_미공개율(%)", "설명불가_미공개율(%)"]].to_string(index=False))
