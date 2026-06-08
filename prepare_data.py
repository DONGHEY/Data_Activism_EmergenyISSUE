"""
CSV 파일을 웹용 JSON으로 변환하는 데이터 준비 스크립트
출력: data/er_map.json, data/er_seoul_stats.json, data/district_stats.json
"""
import pandas as pd
import json
import os

DATA_DIR = "data/raw"
OUT_DIR = "data"

KIOSK_LABELS = {
    "MKioskTy1":  "뇌졸중",
    "MKioskTy2":  "심근경색",
    "MKioskTy3":  "외상",
    "MKioskTy4":  "화상",
    "MKioskTy5":  "고압산소",
    "MKioskTy6":  "정신과",
    "MKioskTy7":  "소아",
    "MKioskTy8":  "산과",
    "MKioskTy9":  "신생아",
    "MKioskTy10": "투석",
    "MKioskTy11": "코로나19(호흡기)",
    "MKioskTy25": "기타중증",
}

def extract_district(addr):
    if pd.isna(addr):
        return "기타"
    for part in str(addr).split():
        if part.endswith("구"):
            return part
    return "기타"

def main():
    inst   = pd.read_csv(f"{DATA_DIR}/er_institutions.csv",  encoding="utf-8-sig")
    detail = pd.read_csv(f"{DATA_DIR}/er_seoul_detail.csv",  encoding="utf-8-sig")

    # 서울 기관 등급 딕셔너리
    seoul_inst = inst[inst["dutyAddr"].str.contains("서울", na=False)]
    grade_lookup = dict(zip(seoul_inst["hpid"], seoul_inst["dutyEmclsName"]))

    # ── er_map.json ──────────────────────────────────────────────────────────
    map_records = []
    for _, row in detail.iterrows():
        lat = row.get("wgs84Lat")
        lon = row.get("wgs84Lon")
        if pd.isna(lat) or pd.isna(lon):
            continue
        beds_raw = row.get("hvec")
        map_records.append({
            "id":    row["hpid"],
            "name":  row["dutyName"],
            "addr":  row["dutyAddr"],
            "lat":   round(float(lat), 6),
            "lon":   round(float(lon), 6),
            "grade": grade_lookup.get(row["hpid"], ""),
            "beds":  int(beds_raw) if pd.notna(beds_raw) else None,
        })

    with open(f"{OUT_DIR}/er_map.json", "w", encoding="utf-8") as f:
        json.dump(map_records, f, ensure_ascii=False, indent=2)
    print(f"er_map.json: {len(map_records)}개 병원")

    # ── er_seoul_stats.json ───────────────────────────────────────────────────
    conditions, yes_list, no_list, unknown_list = [], [], [], []
    for col, label in KIOSK_LABELS.items():
        if col not in detail.columns:
            continue
        s = detail[col]
        conditions.append(label)
        yes_list.append(int((s == "Y").sum()))
        no_list.append(int((s == "N").sum()))
        unknown_list.append(int(s.isna().sum()))

    with open(f"{OUT_DIR}/er_seoul_stats.json", "w", encoding="utf-8") as f:
        json.dump({"conditions": conditions, "yes": yes_list,
                   "no": no_list, "unknown": unknown_list},
                  f, ensure_ascii=False, indent=2)
    print(f"er_seoul_stats.json: {len(conditions)}개 중증질환")

    # ── district_stats.json ───────────────────────────────────────────────────
    detail["district"] = detail["dutyAddr"].apply(extract_district)
    dist = detail.groupby("district").size().sort_values(ascending=False)
    with open(f"{OUT_DIR}/district_stats.json", "w", encoding="utf-8") as f:
        json.dump({"labels": dist.index.tolist(), "counts": dist.values.tolist()},
                  f, ensure_ascii=False, indent=2)
    print(f"district_stats.json: {len(dist)}개 자치구")

if __name__ == "__main__":
    main()
