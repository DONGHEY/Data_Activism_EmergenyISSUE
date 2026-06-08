from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 800})

    errors = []
    console_msgs = []
    page.on("console", lambda msg: errors.append(f"{msg.type}: {msg.text}") if msg.type == "error" else console_msgs.append(f"{msg.type}: {msg.text}"))

    page.goto("http://localhost:8080")
    page.wait_for_load_state("networkidle")
    time.sleep(3)

    # Hero 섹션
    page.screenshot(path="screenshot_hero.png", clip={"x":0,"y":0,"width":1280,"height":800})

    # 지도 섹션
    map_section = page.query_selector("#map-section")
    if map_section:
        page.evaluate("document.getElementById('map-section').scrollIntoView()")
    else:
        print("WARNING: #map-section not found, trying scroll by section order")
        page.evaluate("window.scrollBy(0, 800)")
    time.sleep(1.5)
    page.screenshot(path="screenshot_map.png", clip={"x":0,"y":0,"width":1280,"height":800})

    # 수용 분석 섹션
    capacity_section = page.query_selector("#capacity-section")
    if capacity_section:
        page.evaluate("document.getElementById('capacity-section').scrollIntoView()")
    else:
        print("WARNING: #capacity-section not found")
        page.evaluate("window.scrollBy(0, 1600)")
    time.sleep(1.5)
    page.screenshot(path="screenshot_capacity.png", clip={"x":0,"y":0,"width":1280,"height":800})

    # 설문 섹션
    survey_section = page.query_selector("#survey-section")
    if survey_section:
        page.evaluate("document.getElementById('survey-section').scrollIntoView()")
    else:
        print("WARNING: #survey-section not found")
        page.evaluate("window.scrollBy(0, 2400)")
    time.sleep(1.5)
    page.screenshot(path="screenshot_survey.png", clip={"x":0,"y":0,"width":1280,"height":800})

    # 전체 페이지 스크린샷
    page.evaluate("window.scrollTo(0, 0)")
    time.sleep(0.5)
    page.screenshot(path="screenshot_full.png", full_page=True)

    # 요소 존재 확인
    hero_title = page.query_selector(".hero-title")
    stat_cards = page.query_selector_all(".stat-card")
    map_div = page.query_selector("#map")
    leaflet_pane = page.query_selector(".leaflet-map-pane")
    capacity_chart = page.query_selector("#capacityChart")
    survey_charts = page.query_selector_all("#searchMethodChart, #needInfoChart, #wantFeatureChart")
    capability_table = page.query_selector("#capabilityTableBody")

    # 히어로 헤드라인 텍스트 확인
    hero_text = ""
    if hero_title:
        hero_text = page.evaluate("document.querySelector('.hero-title').textContent")

    # 통계 카드 값 확인
    stat_values = []
    for card in stat_cards:
        val = page.evaluate("(el) => el.textContent", card)
        stat_values.append(val.strip()[:50])

    # 다크 테마 확인
    bg_color = page.evaluate("window.getComputedStyle(document.body).backgroundColor")

    # Leaflet 타일 레이어 확인
    leaflet_tiles = page.query_selector_all(".leaflet-tile")
    leaflet_markers = page.query_selector_all(".leaflet-marker-icon")

    # Canvas 렌더링 확인 (width/height 속성으로 판단)
    capacity_chart_info = ""
    if capacity_chart:
        capacity_chart_info = page.evaluate("""
            () => {
                const c = document.getElementById('capacityChart');
                return c ? `width=${c.width}, height=${c.height}, clientWidth=${c.clientWidth}` : 'not found';
            }
        """)

    survey_chart_info = page.evaluate("""
        () => {
            const ids = ['searchMethodChart', 'needInfoChart', 'wantFeatureChart'];
            return ids.map(id => {
                const c = document.getElementById(id);
                return c ? `${id}: width=${c.width}, height=${c.height}` : `${id}: NOT FOUND`;
            });
        }
    """)

    # 섹션 ID 목록 수집
    section_ids = page.evaluate("""
        () => Array.from(document.querySelectorAll('section[id], div[id]')).map(el => el.id).filter(id => id)
    """)

    checks = {
        "hero_title": hero_title is not None,
        "stat_cards (3개)": len(stat_cards) == 3,
        "map_div (#map)": map_div is not None,
        "leaflet_pane": leaflet_pane is not None,
        "capacity_chart (#capacityChart)": capacity_chart is not None,
        "survey_charts (3개)": len(survey_charts) == 3,
        "capability_table": capability_table is not None,
    }

    print("=== 요소 확인 결과 ===")
    for k, v in checks.items():
        print(f"  {'V' if v else 'X'} {k}: {v}")

    print(f"\n=== Hero 헤드라인 텍스트 ===")
    print(f"  {hero_text[:100]}")

    print(f"\n=== 통계 카드 내용 ({len(stat_cards)}개) ===")
    for i, v in enumerate(stat_values):
        print(f"  Card {i+1}: {v}")

    print(f"\n=== 다크 테마 배경색 ===")
    print(f"  body background-color: {bg_color}")

    print(f"\n=== Leaflet 지도 상태 ===")
    print(f"  leaflet-tile 개수: {len(leaflet_tiles)}")
    print(f"  leaflet-marker-icon 개수: {len(leaflet_markers)}")

    print(f"\n=== Canvas 차트 정보 ===")
    print(f"  capacityChart: {capacity_chart_info}")
    for info in survey_chart_info:
        print(f"  {info}")

    print(f"\n=== 발견된 섹션 ID 목록 ===")
    print(f"  {section_ids}")

    print(f"\n=== 콘솔 에러 ({len(errors)}개) ===")
    for e in errors[:20]:
        print(f"  {e}")

    if not errors:
        print("  (에러 없음)")

    print(f"\n=== 기타 콘솔 메시지 ({len(console_msgs)}개) ===")
    for m in console_msgs[:10]:
        print(f"  {m}")

    browser.close()
    print("\n[완료] 스크린샷 4개 저장됨: screenshot_hero.png, screenshot_map.png, screenshot_capacity.png, screenshot_survey.png")
