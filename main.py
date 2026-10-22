import time
import requests
import streamlit as st
import pandas as pd
import pydeck as pdk
from streamlit_autorefresh import st_autorefresh

# 페이지 설정
st.set_page_config(
    page_title="국제우주정거장 ISS 위치 탐색",
    page_icon="🛰️",
    layout="centered"
)

# 5초마다 페이지 자동 갱신 (5000밀리초)
count = st_autorefresh(interval=5000, limit=None, key="iss_refresh")

# 상단 태그 및 제목
st.markdown(
    """
    <div style="text-align: center;">
        <span style="background-color: #fff3cd; color: #856404; padding: 4px 12px; border-radius: 12px; font-size: 14px; font-weight: bold;">천문·물리</span>
        <span style="background-color: #d1ecf1; color: #0c5460; padding: 4px 12px; border-radius: 12px; font-size: 14px; font-weight: bold; margin-left: 5px;">전 지구(국내 상공 포함)</span>
        <h2 style="margin-top: 10px;">국제우주정거장 ISS</h2>
    </div>
    """,
    unsafe_allow_html=True
)

# 설명 박스 (이미지 내용 반영)
st.markdown(
    """
    <div style="background-color: #fdfefe; border: 1px solid #f0e6d2; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
        <p style="font-weight: bold; margin-bottom: 8px;">📄 어떤 데이터인가요?</p>
        <p style="color: #333; line-height: 1.5; margin: 0;">
            축구장만 한 국제우주정거장(ISS)이 지금 지구 위 약 <b>420km</b>에서 시속 <b>27,000km</b>로 날고 있어요. 약 90분에 지구를 한 바퀴! 그 위치를 초 단위로 알려주는 서비스입니다.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Where the ISS at? API 호출 함수
@st.cache_data(ttl=3)
def get_iss_data():
    url = "https://api.wheretheiss.at/v1/satellites/25544"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception:
        return None
    return None

data = get_iss_data()

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

    # pydeck을 활용한 실시간 위치 지도 시각화
    st.subheader("🌍 ISS 실시간 위치 지도")
    
    df = pd.DataFrame({
        'lat': [lat],
        'lon': [lon],
        'name': ['ISS (International Space Station)']
    })

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["lon", "lat"],
        get_color=[255, 75, 75, 200],
        get_radius=300000, # 가시성을 위한 마커 반경 설정
        pickable=True,
    )

    view_state = pdk.ViewState(
        latitude=lat,
        longitude=lon,
        zoom=2,
        pitch=0,
    )

    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "{name}\n위도: {lat}\n경도: {lon}"}
    )

    st.pydeck_chart(r)

else:
    st.error("ISS 데이터를 불러오는 데 실패했습니다. 잠시 후 다시 시도해 주세요.")

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
        <p style="color: #666; font-size: 12px; margin-top: 10px; margin-bottom: 0;">이 페이지는 5초마다 자동 갱신됩니다.</p>
    </div>
    """,
    unsafe_allow_html=True
)
