from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 800})
    page.goto("http://localhost:8080")
    page.wait_for_load_state("networkidle")
    time.sleep(3)

    # 지도 섹션으로 이동 후 추가 대기
    page.evaluate("document.getElementById('map-section').scrollIntoView()")
    time.sleep(2)

    # 마커 상세 확인
    markers = page.query_selector_all(".leaflet-marker-icon")
    circles = page.query_selector_all(".leaflet-interactive")
    all_map_elements = page.query_selector_all("[class*=leaflet]")

    print(f"leaflet-marker-icon: {len(markers)}")
    print(f"leaflet-interactive (circle markers): {len(circles)}")
    print(f"all leaflet elements: {len(all_map_elements)}")

    # 지도 SVG 내부 확인
    svg_paths = page.query_selector_all(".leaflet-overlay-pane svg path")
    print(f"SVG paths (vector markers): {len(svg_paths)}")

    circles_svg = page.query_selector_all(".leaflet-overlay-pane circle")
    print(f"SVG circles: {len(circles_svg)}")

    # 마커 컨테이너 내용 확인
    marker_pane = page.query_selector(".leaflet-marker-pane")
    if marker_pane:
        inner = page.evaluate("(el) => el.innerHTML", marker_pane)
        print(f"marker-pane HTML: {inner[:300]}")

    # 지도 컨테이너 확인
    map_container = page.query_selector(".leaflet-container")
    print(f"leaflet-container found: {map_container is not None}")

    # 지도 타일 레이어 확인
    tiles = page.query_selector_all(".leaflet-tile-loaded")
    print(f"loaded tiles: {len(tiles)}")

    # JS에서 Leaflet 레이어 정보 확인
    layer_info = page.evaluate("""
        () => {
            if (window._map) {
                const layers = [];
                window._map.eachLayer(l => layers.push(l.constructor.name));
                return layers;
            }
            // 전역 변수 탐색
            const keys = Object.keys(window).filter(k => {
                try { return window[k] && window[k]._leaflet_id; } catch(e) { return false; }
            });
            return keys;
        }
    """)
    print(f"Leaflet map layers/vars: {layer_info}")

    browser.close()
