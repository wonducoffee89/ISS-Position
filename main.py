import streamlit as st
import requests
import datetime
import streamlit.components.v1 as components

# 페이지 설정
st.set_page_config(
    page_title="국제우주정거장 ISS 위치 탐색",
    page_icon="🛰️",
    layout="centered"
)

# 상단 태그 및 제목
st.markdown(
    """
    <div style="text-align: center;">
        <span style="background-color: #fff3cd; color: #856404; padding: 4px 12px; border-radius: 12px; font-size: 14px; font-weight: bold;">천문·물리</span>
        <span style="background-color: #d1ecf1; color: #0c5460; padding: 4px 12px; border-radius: 12px; font-size: 14px; font-weight: bold; margin-left: 5px;">전 지구(국내 상공 포함)</span>
        <h2 style="margin-top: 10px;">국제우주정거장 ISS 궤도 탐색</h2>
    </div>
    """,
    unsafe_allow_html=True
)

# 사이드바: 시간 선택 및 모드 설정
st.sidebar.header("⏱️ ISS 시간 및 위치 설정")
mode = st.sidebar.radio("조회 모드 선택", ["실시간 (Live)", "원하는 시간 선택"])

target_timestamp = None

if mode == "실시간 (Live)":
    # 현재 UTC 타임스탬프
    target_timestamp = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
    st.sidebar.info("현재 실시간 ISS 위치를 불러옵니다.")
else:
    st.sidebar.markdown("조회하고 싶은 날짜와 시간을 선택하세요.")
    d = st.sidebar.date_input("날짜 선택", datetime.date.today())
    t = st.sidebar.time_input("시간 선택", datetime.datetime.now().time())
    
    # 선택한 로컬 시간을 UTC 타임스탬프로 변환
    selected_dt = datetime.datetime.combine(d, t)
    target_timestamp = int(selected_dt.replace(tzinfo=datetime.timezone.utc).timestamp())
    st.sidebar.success(f"선택 시간: {selected_dt}")

# 설명 박스
st.markdown(
    """
    <div style="background-color: #fdfefe; border: 1px solid #f0e6d2; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
        <p style="font-weight: bold; margin-bottom: 8px;">📄 어떤 데이터인가요?</p>
        <p style="color: #333; line-height: 1.5; margin: 0;">
            축구장만 한 국제우주정거장(ISS)이 지금 지구 위 약 <b>420km</b>에서 시속 <b>27,000km</b>로 날고 있어요. 원하는 시간대의 ISS 위치와 이동 정보를 확인해 보세요!
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Where the ISS at? API 호출 함수 (timestamp 파라미터 지원)
def get_iss_data(timestamp=None):
    if timestamp:
        url = f"https://api.wheretheiss.at/v1/satellites/25544?timestamp={timestamp}"
    else:
        url = "https://api.wheretheiss.at/v1/satellites/25544"
        
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception:
        return None
    return None

data = get_iss_data(target_timestamp)

if data:
    lat = data.get("latitude")
    lon = data.get("longitude")
    alt = data.get("altitude") # km
    vel = data.get("velocity") # km/h
    
    # 실시간 메트릭 정보 표시
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("위도 (Latitude)", f"{lat:.2f}°")
    col2.metric("경도 (Longitude)", f"{lon:.2f}°")
    col3.metric("고도 (Altitude)", f"{alt:.2f} km")
    col4.metric("속도 (Velocity)", f"{vel:,.0f} km/h")

    st.markdown("---")

    # Leaflet.js를 활용한 ISS 일러스트 아이콘 지도 시각화
    st.subheader("🌍 ISS 위치 시각화 지도")
    
    leaflet_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <style>
            #map {{ width: 100%; height: 450px; border-radius: 10px; }}
        </style>
    </head>
    <body>
        <div id="map"></div>
        <script>
            var map = L.map('map').setView([{lat}, {lon}], 3);

            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                maxZoom: 19,
                attribution: '© OpenStreetMap'
            }}).addTo(map);

            // ISS 일러스트 아이콘 설정
            var issIcon = L.icon({{
                iconUrl: 'https://cdn-icons-png.flaticon.com/512/3212/3212585.png',
                iconSize: [50, 50],
                iconAnchor: [25, 25],
                popupAnchor: [0, -25]
            }});

            var marker = L.marker([{lat}, {lon}], {{icon: issIcon}}).addTo(map);
            marker.bindPopup("<b>ISS (국제우주정거장)</b><br>위도: {lat:.2f}°<br>경도: {lon:.2f}°<br>고도: {alt:.2f} km").openPopup();
        </script>
    </body>
    </html>
    """
    components.html(leaflet_html, height=470)

else:
    st.error("ISS 데이터를 불러오는 데 실패했습니다. 올바른 시간대인지 확인하거나 잠시 후 다시 시도해 주세요.")

# 하단 정보 및 링크 영역
st.markdown("---")
st.markdown(
    """
    <div style="background-color: #fdfefe; border: 1px solid #f0e6d2; padding: 15px; border-radius: 10px;">
        <p style="margin: 0 0 10px 0;">🔗 <b>원 데이터 출처:</b> <a href="https://wheretheiss.at/" target="_blank">Where the ISS at?</a></p>
        <p style="margin: 0;">
            🚄 <b>더 보기:</b> 
            <a href="https://spotthestation.nasa.gov/" target="_blank" style="margin-right: 10px; text-decoration: none; background: #fae1dd; padding: 4px 10px; border-radius: 15px; color: #333;">NASA Spot the Station</a>
            <a href="https://www.nasa.gov/specials/ISS-tracker/" target="_blank" style="text-decoration: none; background: #e8f4f8; padding: 4px 10px; border-radius: 15px; color: #333;">ISS 실시간 영상(NASA)</a>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
