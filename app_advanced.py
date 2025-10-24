import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# OpenWeather API 키 (보안 처리)
# 환경 변수 또는 Streamlit secrets에서 가져오기
try:
    API_KEY = st.secrets["OPENWEATHER_API_KEY"]
except:
    API_KEY = os.getenv("OPENWEATHER_API_KEY", "your_api_key_here")

# API 키 유효성 검사
if API_KEY == "your_api_key_here" or not API_KEY:
    st.error("⚠️ OpenWeather API 키가 설정되지 않았습니다!")
    st.markdown("""
    ### API 키 설정 방법:
    1. [OpenWeatherMap](https://openweathermap.org/api)에서 무료 API 키를 발급받으세요
    2. 다음 중 하나의 방법으로 API 키를 설정하세요:
    
    **방법 1**: `.env` 파일에 추가
    ```
    OPENWEATHER_API_KEY=your_actual_api_key
    ```
    
    **방법 2**: `.streamlit/secrets.toml` 파일에 추가
    ```
    OPENWEATHER_API_KEY = "your_actual_api_key"
    ```
    """)
    st.stop()
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"

def get_weather_data(city_name):
    """현재 날씨 데이터를 가져오는 함수"""
    try:
        # API 요청 매개변수
        params = {
            'q': city_name,
            'appid': API_KEY,
            'units': 'metric',  # 섭씨온도
            'lang': 'kr'        # 한국어
        }
        
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"날씨 데이터를 가져오는데 실패했습니다: {e}")
        return None

def get_forecast_data(city_name):
    """5일 예보 데이터를 가져오는 함수"""
    try:
        params = {
            'q': city_name,
            'appid': API_KEY,
            'units': 'metric',
            'lang': 'kr'
        }
        
        response = requests.get(FORECAST_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"예보 데이터를 가져오는데 실패했습니다: {e}")
        return None

def get_weather_icon_emoji(icon_code):
    """날씨 아이콘 코드에 따른 이모지 반환"""
    icon_map = {
        '01d': '☀️',  # clear sky day
        '01n': '🌙',  # clear sky night
        '02d': '⛅',  # few clouds day
        '02n': '☁️',  # few clouds night
        '03d': '☁️',  # scattered clouds
        '03n': '☁️',
        '04d': '☁️',  # broken clouds
        '04n': '☁️',
        '09d': '🌧️',  # shower rain
        '09n': '🌧️',
        '10d': '🌦️',  # rain day
        '10n': '🌧️',  # rain night
        '11d': '⛈️',  # thunderstorm
        '11n': '⛈️',
        '13d': '❄️',  # snow
        '13n': '❄️',
        '50d': '🌫️',  # mist
        '50n': '🌫️'
    }
    return icon_map.get(icon_code, '🌤️')

def display_current_weather(weather_data):
    """현재 날씨 정보를 표시하는 함수"""
    if not weather_data:
        return
    
    # 기본 정보 추출
    city = weather_data['name']
    country = weather_data['sys']['country']
    temp = weather_data['main']['temp']
    feels_like = weather_data['main']['feels_like']
    humidity = weather_data['main']['humidity']
    pressure = weather_data['main']['pressure']
    description = weather_data['weather'][0]['description']
    icon = weather_data['weather'][0]['icon']
    wind_speed = weather_data['wind']['speed']
    visibility = weather_data.get('visibility', 0) / 1000  # km로 변환
    
    # 날씨 아이콘 URL과 이모지
    icon_url = f"http://openweathermap.org/img/wn/{icon}@2x.png"
    weather_emoji = get_weather_icon_emoji(icon)
    
    # 현재 시간
    current_time = datetime.now().strftime("%Y년 %m월 %d일 %H:%M")
    
    # 메인 정보 컨테이너
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"## {weather_emoji} {city}, {country}")
            st.markdown(f"### 🌡️ {temp}°C")
            st.caption(f"업데이트: {current_time}")
            
            # 온도 게이지 차트
            fig_temp = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = temp,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "현재 온도"},
                delta = {'reference': feels_like, 'suffix': "°C (체감)"},
                gauge = {
                    'axis': {'range': [-20, 50]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [-20, 0], 'color': "lightblue"},
                        {'range': [0, 20], 'color': "lightgreen"},
                        {'range': [20, 35], 'color': "yellow"},
                        {'range': [35, 50], 'color': "red"}],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': feels_like}}))
            fig_temp.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_temp, use_container_width=True)
        
        with col2:
            st.image(icon_url, width=120)
            st.markdown(f"**{description}**")
            st.markdown(f"**체감온도:** {feels_like}°C")
    
    # 상세 정보 메트릭
    st.markdown("### 📊 상세 정보")
    col3, col4, col5, col6 = st.columns(4)
    
    with col3:
        st.metric(
            label="💧 습도",
            value=f"{humidity}%",
            delta=f"{'높음' if humidity > 70 else '보통' if humidity > 40 else '낮음'}"
        )
    
    with col4:
        st.metric(
            label="🌪️ 풍속",
            value=f"{wind_speed} m/s",
            delta=f"{'강함' if wind_speed > 10 else '보통' if wind_speed > 5 else '약함'}"
        )
    
    with col5:
        st.metric(
            label="📊 기압",
            value=f"{pressure} hPa",
            delta=f"{'높음' if pressure > 1013 else '보통' if pressure > 1000 else '낮음'}"
        )
    
    with col6:
        st.metric(
            label="👁️ 가시거리",
            value=f"{visibility:.1f} km",
            delta=f"{'좋음' if visibility > 10 else '보통' if visibility > 5 else '나쁨'}"
        )

def display_forecast(forecast_data):
    """5일 예보를 표시하는 함수"""
    if not forecast_data:
        return
    
    st.markdown("## 📅 5일 예보")
    
    # 예보 데이터 처리
    forecast_list = []
    for item in forecast_data['list'][:40]:  # 5일 * 8회 (3시간 간격)
        date_time = datetime.fromtimestamp(item['dt'])
        forecast_list.append({
            'datetime': date_time,
            'date': date_time.strftime('%m/%d'),
            'time': date_time.strftime('%H:%M'),
            'temp': item['main']['temp'],
            'temp_min': item['main']['temp_min'],
            'temp_max': item['main']['temp_max'],
            'humidity': item['main']['humidity'],
            'description': item['weather'][0]['description'],
            'icon': item['weather'][0]['icon'],
            'wind_speed': item['wind']['speed']
        })
    
    # 데이터프레임 생성
    df = pd.DataFrame(forecast_list)
    
    # 탭으로 다양한 차트 표시
    tab1, tab2, tab3 = st.tabs(["🌡️ 온도", "💧 습도", "🌪️ 바람"])
    
    with tab1:
        # 온도 변화 그래프
        fig_temp = go.Figure()
        fig_temp.add_trace(go.Scatter(
            x=df['datetime'], y=df['temp'],
            mode='lines+markers',
            name='온도',
            line=dict(color='#ff6b6b', width=3),
            marker=dict(size=6)
        ))
        fig_temp.add_trace(go.Scatter(
            x=df['datetime'], y=df['temp_max'],
            mode='lines',
            name='최고기온',
            line=dict(color='#ff9999', width=2, dash='dash')
        ))
        fig_temp.add_trace(go.Scatter(
            x=df['datetime'], y=df['temp_min'],
            mode='lines',
            name='최저기온',
            line=dict(color='#6bb6ff', width=2, dash='dash')
        ))
        fig_temp.update_layout(
            title='온도 변화 (5일간)',
            xaxis_title='시간',
            yaxis_title='온도 (°C)',
            height=400,
            hovermode='x unified'
        )
        st.plotly_chart(fig_temp, use_container_width=True)
    
    with tab2:
        # 습도 변화 그래프
        fig_humidity = px.area(df, x='datetime', y='humidity',
                              title='습도 변화 (5일간)',
                              labels={'humidity': '습도 (%)', 'datetime': '시간'})
        fig_humidity.update_traces(fill='tonexty', fillcolor='rgba(107, 182, 255, 0.3)')
        fig_humidity.update_layout(height=400)
        st.plotly_chart(fig_humidity, use_container_width=True)
    
    with tab3:
        # 바람 속도 변화 그래프
        fig_wind = px.bar(df, x='datetime', y='wind_speed',
                         title='풍속 변화 (5일간)',
                         labels={'wind_speed': '풍속 (m/s)', 'datetime': '시간'})
        fig_wind.update_layout(height=400)
        st.plotly_chart(fig_wind, use_container_width=True)
    
    # 일별 예보 요약
    st.markdown("### 📋 일별 요약")
    daily_forecast = df.groupby('date').agg({
        'temp': ['min', 'max', 'mean'],
        'humidity': 'mean',
        'description': 'first',
        'icon': 'first'
    }).reset_index()
    
    daily_forecast.columns = ['date', 'min_temp', 'max_temp', 'avg_temp', 'avg_humidity', 'description', 'icon']
    
    # 일별 예보 카드 표시
    cols = st.columns(5)
    for idx, row in daily_forecast.head(5).iterrows():
        with cols[idx]:
            icon_url = f"http://openweathermap.org/img/wn/{row['icon']}@2x.png"
            weather_emoji = get_weather_icon_emoji(row['icon'])
            
            st.markdown(f"### {weather_emoji}")
            st.image(icon_url, width=60)
            st.markdown(f"**{row['date']}**")
            st.markdown(f"🔺 {row['max_temp']:.1f}°C")
            st.markdown(f"🔻 {row['min_temp']:.1f}°C")
            st.markdown(f"💧 {row['avg_humidity']:.0f}%")
            st.caption(f"{row['description']}")

def main():
    """메인 함수"""
    # 페이지 설정
    st.set_page_config(
        page_title="🌤️ 날씨 웹앱",
        page_icon="🌤️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 커스텀 CSS
    st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 0.25rem solid #1f77b4;
    }
    .weather-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 1rem;
        color: white;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 헤더
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='color: #1f77b4; font-size: 3rem; margin: 0;'>🌤️ 실시간 날씨 정보</h1>
        <p style='color: #666; font-size: 1.2rem;'>전 세계 도시의 현재 날씨와 5일 예보를 확인하세요</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 사이드바
    with st.sidebar:
        st.header("⚙️ 설정")
        
        # 도시 입력
        city_input = st.text_input(
            "🏙️ 도시 이름을 입력하세요:",
            value="Seoul",
            help="영문 도시명을 입력해주세요 (예: Seoul, Tokyo, New York)"
        )
        
        # 인기 도시 버튼
        st.markdown("#### 🌍 인기 도시")
        popular_cities = {
            "Seoul": "🇰🇷",
            "Tokyo": "🇯🇵", 
            "New York": "🇺🇸",
            "London": "🇬🇧",
            "Paris": "🇫🇷",
            "Beijing": "🇨🇳"
        }
        
        for city, flag in popular_cities.items():
            if st.button(f"{flag} {city}", key=f"city_{city}", use_container_width=True):
                city_input = city
                st.rerun()
        
        st.markdown("---")
        
        # 앱 정보
        st.markdown("""
        #### ℹ️ 앱 정보
        - **데이터 제공:** OpenWeatherMap
        - **업데이트:** 실시간
        - **예보 기간:** 5일 (3시간 간격)
        """)
        
        # 새로고침 버튼
        if st.button("🔄 새로고침", type="primary", use_container_width=True):
            st.rerun()
    
    # 메인 컨텐츠
    if city_input:
        # 로딩 표시
        with st.spinner(f"🔍 {city_input}의 날씨 정보를 가져오는 중..."):
            weather_data = get_weather_data(city_input)
            forecast_data = get_forecast_data(city_input)
        
        if weather_data and weather_data.get('cod') == 200:
            # 현재 날씨 표시
            display_current_weather(weather_data)
            
            st.markdown("---")
            
            # 5일 예보 표시
            if forecast_data:
                display_forecast(forecast_data)
            
            # 원본 데이터 (개발자용)
            with st.expander("🔧 원본 데이터 (개발자용)"):
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("현재 날씨")
                    st.json(weather_data)
                with col2:
                    if forecast_data:
                        st.subheader("예보 데이터")
                        st.json(forecast_data)
        
        else:
            st.error("❌ 해당 도시의 날씨 정보를 찾을 수 없습니다.")
            st.info("💡 다음을 확인해주세요:")
            st.markdown("""
            - 도시명이 올바른지 확인
            - 영문으로 입력했는지 확인
            - 인기 도시 버튼 사용
            """)
    
    else:
        # 기본 화면
        st.info("👆 사이드바에서 도시를 선택하거나 입력해주세요!")
        
        # 샘플 이미지나 정보 표시
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div style='text-align: center; padding: 3rem;'>
                <h3>🌤️ 전 세계 날씨를 확인하세요!</h3>
                <p>실시간 날씨 정보와 5일 예보를 제공합니다.</p>
            </div>
            """, unsafe_allow_html=True)
    
    # 푸터
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray; padding: 2rem 0;'>
        <p>🌤️ <strong>Weather App</strong> | Powered by OpenWeatherMap API | Made with ❤️ using Streamlit</p>
        <p><small>© 2024 Real-time Weather Information Service</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()