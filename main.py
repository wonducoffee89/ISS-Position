import streamlit as st
import requests
import datetime
import pytz
import streamlit.components.v1 as components

# 페이지 설정
st.set_page_config(
    page_title="국제우주정거장 ISS 위치 탐색",
    page_icon="🛰️",
    layout="centered"
)

# 주요 표준시(Timezone) 매핑
TIMEZONE_OPTIONS = {
    "대한민국 / 일본 (KST/JST, UTC+9)": "Asia/Seoul",
    "협정 세계시 (UTC)": "UTC",
    "미국 동부 (EST/EDT, 뉴욕/워싱턴)": "America/New_York",
    "미국 서부 (PST/PDT, LA/시애틀)": "America/Los_Angeles",
    "영국 / 서유럽 (GMT/BST, 런던)": "Europe/London",
    "중앙유럽 (CET/CEST, 파리/베를린)": "Europe/Paris",
    "호주 동부 (AEST/AEDT, 시드니)": "Australia/Sydney",
}

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

# 사이드바 설정
st.sidebar.header("⚙️ 옵션 및 시간 설정")

# 1. 국가/지역 표준시 선택
selected_tz_label = st.sidebar.selectbox(
    "🌍 기준 표준시(Timezone) 선택",
    list(TIMEZONE_OPTIONS.keys()),
    index=0
)
tz_str = TIMEZONE_OPTIONS[selected_tz_label]
user_tz = pytz.timezone(tz_str)

# 2. 조회 모드 선택
mode = st.sidebar.radio("조회 모드 선택", ["실시간 이동 애니메이션 (Live)", "특정 시간 선택 및 타임머신 재생"])

# 3. 일시정지 / 재생 토글 버튼 (사이드바 배치)
if 'is_paused' not in st.session_state:
    st.session_state.is_paused = False

col_btn1, col_btn2 = st.sidebar.columns(2)
with col_btn1:
    if st.button("▶️ 재생 (Play)"):
        st.session_state.is_paused = False
with col_btn2:
    if st.button("⏸️ 정지 (Pause)"):
        st.session_state.is_paused = True

# Where the ISS at? API 호출 함수
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

# 설명 박스
st.markdown(
    """
    <div style="background-color: #fdfefe; border: 1px solid #f0e6d2; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
        <p style="font-weight: bold; margin-bottom: 8px;">📄 어떤 데이터인가요?</p>
        <p style="color: #333; line-height: 1.5; margin: 0;">
            축구장만 한 국제우주정거장(ISS)이 지금 지구 위 약 <b>420km</b>에서 시속 <b>27,000km</b>로 날고 있어요. 원하는 시간대의 이동 애니메이션과 일시정지 기능을 활용해 보세요!
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

if mode == "실시간 이동 애니메이션 (Live)":
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    now_ts = int(now_utc.timestamp())
    prev_ts = now_ts - 10  # 10초 전
    
    current_data = get_iss_data(now_ts)
    prev_data = get_iss_data(prev_ts)

    if current_data and prev_data:
        lat1, lon1 = prev_data.get("latitude"), prev_data.get("longitude")
        lat2, lon2 = current_data.get("latitude"), current_data.get("longitude")
        alt = current_data.get("altitude")
        vel = current_data.get("velocity")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("위도 (Latitude)", f"{lat2:.2f}°")
        col2.metric("경도 (Longitude)", f"{lon2:.2f}°")
        col3.metric("고도 (Altitude)", f"{alt:.2f} km")
        col4.metric("속도 (Velocity)", f"{vel:,.0f} km/h")

        st.markdown("---")
        status_text = "⏸️ 일시정지됨" if st.session_state.is_paused else "🟢 실시간 이동 중"
        st.subheader(f"🌍 ISS 실시간 이동 지도 ({status_text})")

        reload_code = "" if st.session_state.is_paused else """
        setTimeout(function() {
            window.location.reload();
        }, 10000);
        """

        leaflet_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <style>
                #map {{ width: 100%; height: 480px; border-radius: 10px; }}
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script>
                var map = L.map('map').setView([{lat2}, {lon2}], 3);

                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    maxZoom: 19,
                    attribution: '© OpenStreetMap'
                }}).addTo(map);

                var issIcon = L.icon({{
                    iconUrl: 'https://cdn-icons-png.flaticon.com/512/3212/3212585.png',
                    iconSize: [50, 50],
                    iconAnchor: [25, 25],
                    popupAnchor: [0, -25]
                }});

                var startLat = {lat1}, startLon = {lon1};
                var endLat = {lat2}, endLon = {lon2};

                var marker = L.marker([startLat, startLon], {{icon: issIcon}}).addTo(map);
                marker.bindPopup("<b>ISS (국제우주정거장)</b><br>이동 중...").openPopup();

                var isPaused = {'true' if st.session_state.is_paused else 'false'};

                if (!isPaused) {{
                    var startTime = null;
                    var duration = 10000;

                    function animateMarker(timestamp) {{
                        if (!startTime) startTime = timestamp;
                        var progress = (timestamp - startTime) / duration;
                        if (progress > 1) progress = 1;

                        var currentLat = startLat + (endLat - startLat) * progress;
                        var currentLon = startLon + (endLon - startLon) * progress;

                        marker.setLatLng([currentLat, currentLon]);
                        map.panTo([currentLat, currentLon], {{ animate: false }});

                        if (progress < 1) {{
                            requestAnimationFrame(animateMarker);
                        }}
                    }}
                    requestAnimationFrame(animateMarker);
                }}

                {reload_code}
            </script>
        </body>
        </html>
        """
        components.html(leaflet_html, height=500)
    else:
        st.error("ISS 데이터를 가져오는 데 실패했습니다.")

else:
    # 특정 시간 선택 및 타임머신 재생 모드
    st.sidebar.markdown(f"**선택된 표준시:** `{selected_tz_label}`")
    
    now_in_user_tz = datetime.datetime.now(user_tz)
    
    d = st.sidebar.date_input("시작 날짜 선택", now_in_user_tz.date())
    t = st.sidebar.time_input("시작 시간 선택", now_in_user_tz.time())

    selected_dt_naive = datetime.datetime.combine(d, t)
    selected_dt = user_tz.localize(selected_dt_naive)
    start_timestamp = int(selected_dt.astimezone(pytz.utc).timestamp())
    prev_timestamp = start_timestamp - 10

    st.sidebar.info(f"시작 시각 ({tz_str}):\n{selected_dt.strftime('%Y-%m-%d %H:%M:%S')}")

    current_data = get_iss_data(start_timestamp)
    prev_data = get_iss_data(prev_timestamp)

    if current_data and prev_data:
        lat1, lon1 = prev_data.get("latitude"), prev_data.get("longitude")
        lat2, lon2 = current_data.get("latitude"), current_data.get("longitude")
        alt = current_data.get("altitude")
        vel = current_data.get("velocity")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("위도 (Latitude)", f"{lat2:.2f}°")
        col2.metric("경도 (Longitude)", f"{lon2:.2f}°")
        col3.metric("고도 (Altitude)", f"{alt:.2f} km")
        col4.metric("속도 (Velocity)", f"{vel:,.0f} km/h")

        st.markdown("---")
        status_text = "⏸️ 일시정지됨" if st.session_state.is_paused else "⏩ 타임머신 재생 중 (시간 흐름 반영)"
        st.subheader(f"🌍 선택 시간대 ISS 궤도 애니메이션 ({status_text})")

        reload_code = "" if st.session_state.is_paused else """
        setTimeout(function() {
            window.location.reload();
        }, 10000);
        """

        leaflet_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <style>
                #map {{ width: 100%; height: 480px; border-radius: 10px; }}
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script>
                var map = L.map('map').setView([{lat2}, {lon2}], 3);

                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    maxZoom: 19,
                    attribution: '© OpenStreetMap'
                }}).addTo(map);

                var issIcon = L.icon({{
                    iconUrl: 'https://cdn-icons-png.flaticon.com/512/3212/3212585.png',
                    iconSize: [50, 50],
                    iconAnchor: [25, 25],
                    popupAnchor: [0, -25]
                }});

                var startLat = {lat1}, startLon = {lon1};
                var endLat = {lat2}, endLon = {lon2};

                var marker = L.marker([startLat, startLon], {{icon: issIcon}}).addTo(map);
                marker.bindPopup("<b>ISS (국제우주정거장)</b><br>과거 궤도 재생 중...").openPopup();

                var isPaused = {'true' if st.session_state.is_paused else 'false'};

                if (!isPaused) {{
                    var startTime = null;
                    var duration = 10000;

                    function animateMarker(timestamp) {{
                        if (!startTime) startTime = timestamp;
                        var progress = (timestamp - startTime) / duration;
                        if (progress > 1) progress = 1;

                        var currentLat = startLat + (endLat - startLat) * progress;
                        var currentLon = startLon + (endLon - startLon) * progress;

                        marker.setLatLng([currentLat, currentLon]);
                        map.panTo([currentLat, currentLon], {{ animate: false }});

                        if (progress < 1) {{
                            requestAnimationFrame(animateMarker);
                        }}
                    }}
                    requestAnimationFrame(animateMarker);
                }}

                {reload_code}
            </script>
        </body>
        </html>
        """
        components.html(leaflet_html, height=500)
    else:
        st.error("해당 시간대의 ISS 데이터를 불러오는 데 실패했습니다.")

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
