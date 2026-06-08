# 능력 지표 기반 미공개 분석

> 분석일시: 2026-06-01 18:38  
> 방법론: 장비·시설 보유 증거가 있는 병원 중 MKiosk 공백인 경우만 '설명 불가능한 미공개'로 정의

---

## 1. 데이터 구조 요약

- `er_seoul_detail.csv`: 서울 **76개** 병원 (MKiosk 중증질환 수용 여부)
- `er_realtime_full.csv`: 전국 418개 중 서울 **53개** 병원 (장비 가용 여부)
- 교집합: **53개** — 이 병원들만 능력 기반 분석 가능
- realtime 없는 23개: 능력 판단 불가 → 분석 제외

## 2. 기존 vs 새 방식 비교

> 기존: 76개 전체 분모 / 새 방식: 해당 능력 지표가 있는 병원 분모

| 중증질환 | 기존 미공개 | 기존 미공개율 | 능력있는 병원 | 능력있는데 공백 | **설명불가 미공개율** |
|---|---|---|---|---|---|
| 뇌졸중 | 41 | 53.9% | 52 | 17 | **32.7%** ▼ |
| 심근경색 | 44 | 57.9% | 37 | 5 | **13.5%** ▼ |
| 외상 | 44 | 57.9% | 49 | 19 | **38.8%** ▼ |
| 화상 | 38 | 50.0% | 50 | 14 | **28.0%** ▼ |
| 고압산소 | 55 | 72.4% | 5 | 3 | **60.0%** ▼ |
| 정신과 | 52 | nan% | 지표없음 | 지표없음 | **nan%** ▲ |
| 소아 | 35 | 46.1% | 30 | 3 | **10.0%** ▼ |
| 산과 | 41 | 53.9% | 50 | 17 | **34.0%** ▼ |
| 신생아 | 37 | 48.7% | 33 | 3 | **9.1%** ▼ |
| 투석 | 58 | 76.3% | 42 | 25 | **59.5%** ▼ |
| 코로나19(호흡기) | 38 | 50.0% | 52 | 14 | **26.9%** ▼ |
| 기타중증 | 51 | 67.1% | 52 | 27 | **51.9%** ▼ |

## 3. 설명 불가능한 미공개 — 병원별 상세

> 장비/시설 보유 증거가 있음에도 수용 여부를 공개하지 않는 병원

### 고압산소 (3개 병원)

| 병원명 | 등급 | 능력 근거 |
|---|---|---|
| 삼육서울병원 | 지역응급의료센터 | hvoxyayn=Y |
| 서울특별시서울의료원 | 권역응급의료센터 | hvoxyayn=Y |
| 의료법인한전의료재단한일병원 | 지역응급의료센터 | hvoxyayn=Y |

### 기타중증 (27개 병원)

| 병원명 | 등급 | 능력 근거 |
|---|---|---|
| 경찰병원 | 지역응급의료기관 | hvecmoayn=N1, hvventiayn=Y, hpicuyn=16.0 |
| 구로성심병원 | 지역응급의료기관 | hvecmoayn=N1, hvventiayn=Y, hpicuyn=nan |
| 국립중앙의료원 | 지역응급의료센터 | hvecmoayn=Y, hvventiayn=Y, hpicuyn=11.0 |
| 기쁨병원 | 지역응급의료기관 | hvecmoayn=N1, hvventiayn=Y, hpicuyn=nan |
| 노원을지대학교병원 | 지역응급의료센터 | hvecmoayn=Y, hvventiayn=Y, hpicuyn=nan |
| 녹색병원 | 지역응급의료기관 | hvecmoayn=N1, hvventiayn=Y, hpicuyn=15.0 |
| 대림성모병원 | 지역응급의료기관 | hvecmoayn=N1, hvventiayn=Y, hpicuyn=nan |
| 명지성모병원 | 지역응급의료기관 | hvecmoayn=N1, hvventiayn=Y, hpicuyn=12.0 |
| 부민병원 | 지역응급의료기관 | hvecmoayn=Y, hvventiayn=Y, hpicuyn=13.0 |
| 서울산보람병원 | 지역응급의료기관 | hvecmoayn=N1, hvventiayn=Y, hpicuyn=nan |
| 서울성심병원 | 지역응급의료기관 | hvecmoayn=N1, hvventiayn=Y, hpicuyn=8.0 |
| 서울적십자병원 | 지역응급의료기관 | hvecmoayn=N1, hvventiayn=Y, hpicuyn=12.0 |
| 서울특별시동부병원 | 지역응급의료기관 | hvecmoayn=N1, hvventiayn=Y, hpicuyn=9.0 |
| 서울특별시서남병원 | 지역응급의료기관 | hvecmoayn=Y, hvventiayn=Y, hpicuyn=15.0 |
| 서울특별시서울의료원 | 권역응급의료센터 | hvecmoayn=Y, hvventiayn=Y, hpicuyn=nan |
| 성애의료재단성애병원 | 지역응급의료센터 | hvecmoayn=N1, hvventiayn=Y, hpicuyn=12.0 |
| 세란병원 | 지역응급의료기관 | hvecmoayn=N1, hvventiayn=Y, hpicuyn=nan |
| 의료법인동신의료재단동신병원 | 지역응급의료기관 | hvecmoayn=N, hvventiayn=Y, hpicuyn=11.0 |
| 의료법인서울효천의료재단에이치플러스양지병원 | 지역응급의료센터 | hvecmoayn=Y, hvventiayn=Y, hpicuyn=20.0 |
| 의료법인청구성심병원 | 지역응급의료기관 | hvecmoayn=N1, hvventiayn=Y, hpicuyn=7.0 |
| 의료법인풍산의료재단동부제일병원 | 지역응급의료기관 | hvecmoayn=N1, hvventiayn=Y, hpicuyn=nan |
| 의료법인한전의료재단한일병원 | 지역응급의료센터 | hvecmoayn=N1, hvventiayn=Y, hpicuyn=25.0 |
| 이화여자대학교의과대학부속서울병원 | 지역응급의료센터 | hvecmoayn=Y, hvventiayn=Y, hpicuyn=nan |
| 한국원자력의학원원자력병원 | 지역응급의료기관 | hvecmoayn=N1, hvventiayn=Y, hpicuyn=10.0 |
| 혜민병원 | 지역응급의료기관 | hvecmoayn=N1, hvventiayn=Y, hpicuyn=15.0 |
| 홍익병원 | 지역응급의료기관 | hvecmoayn=N1, hvventiayn=Y, hpicuyn=7.0 |
| 희명병원 | 지역응급의료기관 | hvecmoayn=Y, hvventiayn=Y, hpicuyn=27.0 |

### 뇌졸중 (17개 병원)

| 병원명 | 등급 | 능력 근거 |
|---|---|---|
| 경찰병원 | 지역응급의료기관 | hvctayn=Y, hvmriayn=Y |
| 구로성심병원 | 지역응급의료기관 | hvctayn=Y, hvmriayn=Y |
| 기쁨병원 | 지역응급의료기관 | hvctayn=Y, hvmriayn=Y |
| 녹색병원 | 지역응급의료기관 | hvctayn=Y, hvmriayn=Y |
| 대림성모병원 | 지역응급의료기관 | hvctayn=Y, hvmriayn=Y |
| 부민병원 | 지역응급의료기관 | hvctayn=Y, hvmriayn=Y |
| 서울산보람병원 | 지역응급의료기관 | hvctayn=Y, hvmriayn=Y |
| 서울성심병원 | 지역응급의료기관 | hvctayn=Y, hvmriayn=Y |
| 서울적십자병원 | 지역응급의료기관 | hvctayn=Y, hvmriayn=Y |
| 서울특별시동부병원 | 지역응급의료기관 | hvctayn=Y, hvmriayn=Y |
| 서울특별시서남병원 | 지역응급의료기관 | hvctayn=Y, hvmriayn=Y |
| 세란병원 | 지역응급의료기관 | hvctayn=Y, hvmriayn=Y |
| 의료법인동신의료재단동신병원 | 지역응급의료기관 | hvctayn=Y, hvmriayn=Y |
| 의료법인청구성심병원 | 지역응급의료기관 | hvctayn=Y, hvmriayn=Y |
| 의료법인풍산의료재단동부제일병원 | 지역응급의료기관 | hvctayn=Y, hvmriayn=N |
| 한국원자력의학원원자력병원 | 지역응급의료기관 | hvctayn=Y, hvmriayn=Y |
| 혜민병원 | 지역응급의료기관 | hvctayn=Y, hvmriayn=Y |

### 산과 (17개 병원)

| 병원명 | 등급 | 능력 근거 |
|---|---|---|
| 경찰병원 | 지역응급의료기관 | hpopyn=7.0 |
| 녹색병원 | 지역응급의료기관 | hpopyn=3.0 |
| 대림성모병원 | 지역응급의료기관 | hpopyn=4.0 |
| 명지성모병원 | 지역응급의료기관 | hpopyn=3.0 |
| 부민병원 | 지역응급의료기관 | hpopyn=5.0 |
| 서울산보람병원 | 지역응급의료기관 | hpopyn=3.0 |
| 서울성심병원 | 지역응급의료기관 | hpopyn=6.0 |
| 서울적십자병원 | 지역응급의료기관 | hpopyn=6.0 |
| 서울특별시동부병원 | 지역응급의료기관 | hpopyn=3.0 |
| 서울특별시서남병원 | 지역응급의료기관 | hpopyn=5.0 |
| 성애의료재단성애병원 | 지역응급의료센터 | hpopyn=5.0 |
| 세란병원 | 지역응급의료기관 | hpopyn=5.0 |
| 씨엠병원 | 지역응급의료기관 | hpopyn=4.0 |
| 의료법인동신의료재단동신병원 | 지역응급의료기관 | hpopyn=4.0 |
| 의료법인청구성심병원 | 지역응급의료기관 | hpopyn=3.0 |
| 의료법인풍산의료재단동부제일병원 | 지역응급의료기관 | hpopyn=2.0 |
| 혜민병원 | 지역응급의료기관 | hpopyn=5.0 |

### 소아 (3개 병원)

| 병원명 | 등급 | 능력 근거 |
|---|---|---|
| 국립중앙의료원 | 지역응급의료센터 | hvventisoayn=N, hvincuayn=Y |
| 부민병원 | 지역응급의료기관 | hvventisoayn=N1, hvincuayn=Y |
| 서울특별시동부병원 | 지역응급의료기관 | hvventisoayn=N1, hvincuayn=Y |

### 신생아 (3개 병원)

| 병원명 | 등급 | 능력 근거 |
|---|---|---|
| 국립중앙의료원 | 지역응급의료센터 | hvincuayn=Y, hpnicuyn=nan |
| 부민병원 | 지역응급의료기관 | hvincuayn=Y, hpnicuyn=nan |
| 서울특별시동부병원 | 지역응급의료기관 | hvincuayn=Y, hpnicuyn=nan |

### 심근경색 (5개 병원)

| 병원명 | 등급 | 능력 근거 |
|---|---|---|
| 국립중앙의료원 | 지역응급의료센터 | hvangioayn=Y |
| 기쁨병원 | 지역응급의료기관 | hvangioayn=Y |
| 부민병원 | 지역응급의료기관 | hvangioayn=Y |
| 성애의료재단성애병원 | 지역응급의료센터 | hvangioayn=Y |
| 한국원자력의학원원자력병원 | 지역응급의료기관 | hvangioayn=Y |

### 외상 (19개 병원)

| 병원명 | 등급 | 능력 근거 |
|---|---|---|
| 경찰병원 | 지역응급의료기관 | hvventiayn=Y, hpopyn=7.0 |
| 구로성심병원 | 지역응급의료기관 | hvventiayn=Y, hpopyn=3.0 |
| 국립중앙의료원 | 지역응급의료센터 | hvventiayn=Y, hpopyn=7.0 |
| 녹색병원 | 지역응급의료기관 | hvventiayn=Y, hpopyn=3.0 |
| 대림성모병원 | 지역응급의료기관 | hvventiayn=Y, hpopyn=4.0 |
| 부민병원 | 지역응급의료기관 | hvventiayn=Y, hpopyn=5.0 |
| 서울산보람병원 | 지역응급의료기관 | hvventiayn=Y, hpopyn=3.0 |
| 서울성심병원 | 지역응급의료기관 | hvventiayn=Y, hpopyn=6.0 |
| 서울적십자병원 | 지역응급의료기관 | hvventiayn=Y, hpopyn=6.0 |
| 서울특별시동부병원 | 지역응급의료기관 | hvventiayn=Y, hpopyn=3.0 |
| 서울특별시서남병원 | 지역응급의료기관 | hvventiayn=Y, hpopyn=5.0 |
| 성애의료재단성애병원 | 지역응급의료센터 | hvventiayn=Y, hpopyn=5.0 |
| 세란병원 | 지역응급의료기관 | hvventiayn=Y, hpopyn=5.0 |
| 의료법인동신의료재단동신병원 | 지역응급의료기관 | hvventiayn=Y, hpopyn=4.0 |
| 의료법인청구성심병원 | 지역응급의료기관 | hvventiayn=Y, hpopyn=3.0 |
| 의료법인풍산의료재단동부제일병원 | 지역응급의료기관 | hvventiayn=Y, hpopyn=2.0 |
| 한국원자력의학원원자력병원 | 지역응급의료기관 | hvventiayn=Y, hpopyn=10.0 |
| 혜민병원 | 지역응급의료기관 | hvventiayn=Y, hpopyn=5.0 |
| 희명병원 | 지역응급의료기관 | hvventiayn=Y, hpopyn=3.0 |

### 코로나19(호흡기) (14개 병원)

| 병원명 | 등급 | 능력 근거 |
|---|---|---|
| 경찰병원 | 지역응급의료기관 | hvventiayn=Y |
| 국립중앙의료원 | 지역응급의료센터 | hvventiayn=Y |
| 기쁨병원 | 지역응급의료기관 | hvventiayn=Y |
| 대림성모병원 | 지역응급의료기관 | hvventiayn=Y |
| 명지성모병원 | 지역응급의료기관 | hvventiayn=Y |
| 부민병원 | 지역응급의료기관 | hvventiayn=Y |
| 서울적십자병원 | 지역응급의료기관 | hvventiayn=Y |
| 서울특별시동부병원 | 지역응급의료기관 | hvventiayn=Y |
| 세란병원 | 지역응급의료기관 | hvventiayn=Y |
| 의료법인동신의료재단동신병원 | 지역응급의료기관 | hvventiayn=Y |
| 의료법인풍산의료재단동부제일병원 | 지역응급의료기관 | hvventiayn=Y |
| 혜민병원 | 지역응급의료기관 | hvventiayn=Y |
| 홍익병원 | 지역응급의료기관 | hvventiayn=Y |
| 희명병원 | 지역응급의료기관 | hvventiayn=Y |

### 투석 (25개 병원)

| 병원명 | 등급 | 능력 근거 |
|---|---|---|
| 가톨릭대학교여의도성모병원 | 지역응급의료센터 | hvcrrtayn=Y |
| 강동경희대학교병원 | 권역응급의료센터 | hvcrrtayn=Y |
| 건국대학교병원 | 지역응급의료센터 | hvcrrtayn=Y |
| 경찰병원 | 지역응급의료기관 | hvcrrtayn=Y |
| 경희대학교병원 | 지역응급의료센터 | hvcrrtayn=Y |
| 국립중앙의료원 | 지역응급의료센터 | hvcrrtayn=Y |
| 녹색병원 | 지역응급의료기관 | hvcrrtayn=Y |
| 부민병원 | 지역응급의료기관 | hvcrrtayn=Y |
| 삼육서울병원 | 지역응급의료센터 | hvcrrtayn=Y |
| 서울적십자병원 | 지역응급의료기관 | hvcrrtayn=Y |
| 서울특별시동부병원 | 지역응급의료기관 | hvcrrtayn=Y |
| 서울특별시보라매병원 | 지역응급의료센터 | hvcrrtayn=Y |
| 서울특별시서남병원 | 지역응급의료기관 | hvcrrtayn=Y |
| 성심의료재단강동성심병원 | 지역응급의료센터 | hvcrrtayn=Y |
| 성애의료재단성애병원 | 지역응급의료센터 | hvcrrtayn=Y |
| 순천향대학교부속서울병원 | 지역응급의료센터 | hvcrrtayn=Y |
| 연세대학교의과대학강남세브란스병원 | 지역응급의료센터 | hvcrrtayn=Y |
| 의료법인동신의료재단동신병원 | 지역응급의료기관 | hvcrrtayn=Y |
| 의료법인서울효천의료재단에이치플러스양지병원 | 지역응급의료센터 | hvcrrtayn=Y |
| 의료법인한전의료재단한일병원 | 지역응급의료센터 | hvcrrtayn=Y |
| 이화여자대학교의과대학부속목동병원 | 권역응급의료센터 | hvcrrtayn=Y |
| 한국보훈복지의료공단중앙보훈병원 | 지역응급의료센터 | hvcrrtayn=Y |
| 한국원자력의학원원자력병원 | 지역응급의료기관 | hvcrrtayn=Y |
| 혜민병원 | 지역응급의료기관 | hvcrrtayn=Y |
| 희명병원 | 지역응급의료기관 | hvcrrtayn=Y |

### 화상 (14개 병원)

| 병원명 | 등급 | 능력 근거 |
|---|---|---|
| 경찰병원 | 지역응급의료기관 | hpopyn=7.0 |
| 구로성심병원 | 지역응급의료기관 | hpopyn=3.0 |
| 대림성모병원 | 지역응급의료기관 | hpopyn=4.0 |
| 부민병원 | 지역응급의료기관 | hpopyn=5.0 |
| 서울성심병원 | 지역응급의료기관 | hpopyn=6.0 |
| 서울적십자병원 | 지역응급의료기관 | hpopyn=6.0 |
| 서울특별시동부병원 | 지역응급의료기관 | hpopyn=3.0 |
| 서울특별시서남병원 | 지역응급의료기관 | hpopyn=5.0 |
| 세란병원 | 지역응급의료기관 | hpopyn=5.0 |
| 씨엠병원 | 지역응급의료기관 | hpopyn=4.0 |
| 의료법인동신의료재단동신병원 | 지역응급의료기관 | hpopyn=4.0 |
| 의료법인청구성심병원 | 지역응급의료기관 | hpopyn=3.0 |
| 의료법인풍산의료재단동부제일병원 | 지역응급의료기관 | hpopyn=2.0 |
| 희명병원 | 지역응급의료기관 | hpopyn=3.0 |

## 4. 방법론 주석

| 중증질환 | 능력 지표 | 근거 |
|---|---|---|
| 뇌졸중 | hvctayn OR hvmriayn | 해당 장비 보유 = 처치 가능 |
| 심근경색 | hvangioayn | 해당 장비 보유 = 처치 가능 |
| 외상 | hvventiayn AND hpopyn | 해당 장비 보유 = 처치 가능 |
| 화상 | hpopyn | 해당 장비 보유 = 처치 가능 |
| 고압산소 | hvoxyayn | 해당 장비 보유 = 처치 가능 |
| 정신과 | — | 객관적 장비 지표 없음 (분석 제외) |
| 소아 | hvventisoayn OR hvincuayn | 해당 장비 보유 = 처치 가능 |
| 산과 | hpopyn | 해당 장비 보유 = 처치 가능 |
| 신생아 | hvincuayn OR hpnicuyn | 해당 장비 보유 = 처치 가능 |
| 투석 | hvcrrtayn | 해당 장비 보유 = 처치 가능 |
| 코로나19(호흡기) | hvventiayn | 해당 장비 보유 = 처치 가능 |
| 기타중증 | hvecmoayn OR hvventiayn OR hpicuyn | 해당 장비 보유 = 처치 가능 |

---
> 분석 스크립트: `capability_analysis.py`