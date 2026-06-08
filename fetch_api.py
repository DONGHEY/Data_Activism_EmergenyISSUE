"""
공공데이터포털 - 국립응급의료원_전국 응급의료기관 정보 조회 서비스
API 응답(XML) → pandas DataFrame → CSV 저장

[인증키 설정 방법]
  공공데이터포털 마이페이지 > 개발계정 > 인증키(Decoding) 복사
  아래 API_KEY 변수에 붙여넣기

[실행 방법]
  터미널에서: python fetch_api.py
  결과: data/raw/ 폴더에 CSV 3개 생성
"""

import requests
import xml.etree.ElementTree as ET
import pandas as pd
import os

# ====================================================
# 인증키를 여기에 붙여넣으세요 (따옴표 안에)
API_KEY = "b5b8fe3f79aac7f79dd4c423c84572cc849b7c92c7afbfbd8c3993a488f3d97b"
# ====================================================

BASE_URL = "http://apis.data.go.kr/B552657/ErmctInfoInqireService"
SAVE_DIR = "data/raw"


def fetch_all_pages(endpoint, extra_params):
    """
    한 페이지에 100개씩 요청하면서 전체 데이터를 다 가져옴.
    공공데이터 API는 한 번에 최대 100개까지만 줌 → 여러 페이지 요청 필요.
    """
    all_items = []
    page = 1

    while True:
        params = {
            "ServiceKey": API_KEY,
            "numOfRows": 100,
            "pageNo": page,
            **extra_params,   # 시도코드(STAGE1) 등 추가 파라미터
        }
        url = f"{BASE_URL}/{endpoint}"

        print(f"  요청 중: page {page} ...", end=" ")
        response = requests.get(url, params=params, timeout=15)

        # XML이 아닌 에러 응답이 오면 바로 중단
        if not response.content.startswith(b"<"):
            print("에러: XML이 아닌 응답이 왔습니다.")
            print("응답 내용:", response.text[:300])
            print("→ 인증키가 올바른지 확인해주세요.")
            break

        root = ET.fromstring(response.content)

        # API 서버 오류 코드 확인
        result_code = root.findtext(".//resultCode", default="")
        if result_code != "00":
            result_msg = root.findtext(".//resultMsg", default="알 수 없는 오류")
            print(f"API 오류: [{result_code}] {result_msg}")
            break

        # 이번 페이지 데이터 추출
        items = root.findall(".//item")
        page_data = [
            {child.tag: (child.text.strip() if child.text else None) for child in item}
            for item in items
        ]
        all_items.extend(page_data)
        print(f"{len(page_data)}건 수집 (누적 {len(all_items)}건)")


        # 전체 건수 확인해서 더 가져올 게 없으면 종료
        total_count = int(root.findtext(".//totalCount", default="0"))
        if len(all_items) >= total_count:
            break

        page += 1

    return all_items


def save_csv(data, filename):
    """DataFrame으로 변환 후 CSV 저장. encoding='utf-8-sig'로 Excel 한글 깨짐 방지."""
    if not data:
        print(f"  저장할 데이터 없음: {filename}")
        return

    os.makedirs(SAVE_DIR, exist_ok=True)
    filepath = os.path.join(SAVE_DIR, filename)

    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False, encoding="utf-8-sig")
    print(f"  저장 완료: {filepath} ({len(df)}행 × {len(df.columns)}열)")
    return df


# MKioskTy 코드 → 중증질환 한국어 이름 매핑
MKIOSK_LABELS = {
    "MKioskTy1":  "뇌졸중",       "MKioskTy2":  "심근경색",
    "MKioskTy3":  "외상",          "MKioskTy4":  "화상",
    "MKioskTy5":  "고압산소",      "MKioskTy6":  "정신과",
    "MKioskTy7":  "소아",          "MKioskTy8":  "산과",
    "MKioskTy9":  "신생아",        "MKioskTy10": "투석",
    "MKioskTy11": "코로나19(호흡기)", "MKioskTy25": "기타",
}

# 중증질환 코드 → 한국어 이름 매핑
HVS_LABELS = {
    "hvs01": "뇌졸중(재관류)",   "hvs02": "심근경색(재관류)",
    "hvs03": "복부손상수술",      "hvs04": "사지접합수술",
    "hvs05": "응급투석",          "hvs06": "조산산모",
    "hvs07": "신생아집중치료",    "hvs08": "중증화상",
    "hvs19": "코로나19",          "hvs22": "외상",
    "hvs26": "정신질환자",        "hvs27": "분만",
    "hvs28": "뇌출혈수술",        "hvs29": "뇌경색재관류",
    "hvs30": "심정지",            "hvs31": "일반외상",
    "hvs32": "흉부손상수술",      "hvs33": "뇌수술",
    "hvs34": "복강경수술",        "hvs35": "심장수술",
    "hvs37": "응급내시경",        "hvs38": "응급혈관술",
    "hvs50": "응급투석(야간)",    "hvs51": "응급수술(야간)",
}


def main():
    print("=" * 55)
    print("응급의료기관 데이터 수집")
    print("=" * 55)

    # --------------------------------------------------
    # 1) 응급의료기관 목록 정보 (서울 필터)
    #    기관명, 주소, 좌표, 전화, 기관등급
    # --------------------------------------------------
    print("\n[1/2] 응급의료기관 목록 정보 (getEgytListInfoInqire)")
    data = fetch_all_pages("getEgytListInfoInqire", {"STAGE1": "Q0"})
    df1 = save_csv(data, "er_institutions.csv")

    # --------------------------------------------------
    # 2) 응급실 실시간 가용병상 + 중증질환 진료가능 여부
    #    - hvec: 응급실 가용 병상수
    #    - hvs01~hvs51: 중증질환별 Y / N / 정보미공개
    #    ※ 파라미터 없이 호출해야 전체 데이터가 나옴 (STAGE1 미지원)
    #    ※ 실시간 데이터라 실행할 때마다 값이 달라짐
    # --------------------------------------------------
    print("\n[2/2] 실시간 병상 + 중증질환 진료가능 여부 (getEmrrmRltmUsefulSckbdInfoInqire)")
    data = fetch_all_pages("getEmrrmRltmUsefulSckbdInfoInqire", {})
    save_csv(data, "er_realtime_full.csv")

    # --------------------------------------------------
    # 3) 서울 병원별 기본정보 (중증질환별 수용가능 여부)
    #    MKioskTy1~MKioskTy25: Y / N / NaN(정보미공개)
    #    → 정보 접근성 분석의 핵심 데이터
    # --------------------------------------------------
    print("\n[추가] 서울 병원별 중증질환 수용가능 여부 (getEgytBassInfoInqire)")
    if df1 is not None:
        seoul_hpids = df1[df1["dutyAddr"].str.contains("서울", na=False)]["hpid"].tolist()
        print(f"  서울 병원 {len(seoul_hpids)}곳에 대해 개별 조회 중...")
        detail_rows = []
        for i, hpid in enumerate(seoul_hpids, 1):
            r = requests.get(
                f"{BASE_URL}/getEgytBassInfoInqire",
                params={"ServiceKey": API_KEY, "HPID": hpid, "numOfRows": 1, "pageNo": 1},
                timeout=15,
            )
            if r.content.startswith(b"<"):
                root = ET.fromstring(r.content)
                item = root.find(".//item")
                if item is not None:
                    detail_rows.append({c.tag: (c.text.strip() if c.text else None) for c in item})
            if i % 10 == 0:
                print(f"    {i}/{len(seoul_hpids)} 완료...")
        df3 = save_csv(detail_rows, "er_seoul_detail.csv")
    else:
        df3 = None

    # --------------------------------------------------
    # 수집 결과 요약
    # --------------------------------------------------
    print("\n" + "=" * 55)
    print("수집 완료! 아래 파일들을 Excel로 열어서 확인해보세요:")
    print("  data/raw/er_institutions.csv   ← 기관 목록 (주소/좌표/등급)")
    print("  data/raw/er_realtime_full.csv  ← 실시간 병상 수 (전국)")
    print("  data/raw/er_seoul_detail.csv   ← 서울 병원별 중증질환 Y/N/정보미공개 (핵심!)")

    # 노원구 병원 확인
    if df1 is not None:
        nowon = df1[df1["dutyAddr"].str.contains("노원", na=False)]
        print(f"\n노원구 포함 기관 {len(nowon)}곳:")
        for _, row in nowon.iterrows():
            print(f"  - {row['dutyName']}")

    # 중증질환 정보미공개 현황 요약 (MKioskTy Y/N/NaN 분포)
    if df3 is not None:
        mk_cols = [c for c in df3.columns if c.startswith("MKioskTy")]
        total = len(df3)
        print(f"\n[서울 {total}개 병원 중증질환 수용가능 여부]")
        for col in mk_cols:
            y = (df3[col] == "Y").sum()
            n = (df3[col] == "N").sum()
            missing = df3[col].isna().sum()
            label = MKIOSK_LABELS.get(col, col)
            print(f"  {label:12s}: 가능 {y:2d}개 / 불가 {n:2d}개 / 정보미공개 {missing:2d}개")

    print("=" * 55)


if __name__ == "__main__":
    main()
