# 🌤️ 실시간 날씨 웹앱

OpenWeather API를 사용하여 만든 실시간 날씨 정보 웹 애플리케이션입니다.

## ✨ 주요 기능

- 🌍 전 세계 도시의 실시간 날씨 정보
- 📊 온도, 습도, 기압, 풍속 등 상세 정보
- 📅 5일간의 날씨 예보 (3시간 간격)
- 📈 인터랙티브 차트와 그래프
- 🎨 직관적이고 아름다운 UI/UX
- 📱 반응형 디자인 (모바일 친화적)

## 🚀 빠른 시작

### 1. 필요한 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 기본 버전 실행

```bash
streamlit run app.py
```

### 3. 고급 버전 실행 (더 많은 기능 포함)

```bash
streamlit run app_advanced.py
```

## 📁 프로젝트 구조

```
weather/
├── app.py              # 기본 버전 앱
├── app_advanced.py     # 고급 버전 앱 (더 많은 기능)
├── requirements.txt    # 필요한 패키지 목록
├── .env               # 환경 변수 (API 키)
└── README.md          # 프로젝트 설명서
```

## 🔧 설정

### API 키 설정 (중요!)

보안을 위해 API 키는 환경 변수 또는 Streamlit secrets로 관리됩니다.

#### 방법 1: 환경 변수 사용 (.env 파일)

1. `.env.example` 파일을 복사하여 `.env` 파일을 생성합니다:
```bash
cp .env.example .env
```

2. `.env` 파일에 실제 API 키를 입력합니다:
```env
OPENWEATHER_API_KEY=your_actual_api_key_here
```

#### 방법 2: Streamlit Secrets 사용

1. `.streamlit/secrets.toml` 파일을 생성합니다:
```toml
OPENWEATHER_API_KEY = "your_actual_api_key_here"
```

#### OpenWeather API 키 발급 받기

1. [OpenWeatherMap](https://openweathermap.org/api) 사이트에 가입
2. API Keys 섹션에서 무료 API 키 발급
3. 위의 방법 중 하나로 API 키 설정

⚠️ **중요**: `.env` 파일과 `secrets.toml` 파일은 `.gitignore`에 포함되어 Git에 업로드되지 않습니다.

## 📊 사용 가능한 기능

### 기본 버전 (app.py)
- 현재 날씨 정보
- 5일 예보
- 기본 차트

### 고급 버전 (app_advanced.py)
- 온도 게이지 차트
- 다중 탭 차트 (온도, 습도, 바람)
- 향상된 UI/UX
- 이모지 날씨 아이콘
- 더 자세한 메트릭 정보

## 🌍 지원되는 도시

전 세계 모든 도시를 지원합니다. 영문 도시명으로 검색해주세요.

### 인기 도시 예시:
- Seoul (서울)
- Tokyo (도쿄)
- New York (뉴욕)
- London (런던)
- Paris (파리)
- Beijing (베이징)

## 📱 사용 방법

1. 웹 애플리케이션을 실행합니다
2. 사이드바에서 도시명을 입력하거나 인기 도시 버튼을 클릭합니다
3. 실시간 날씨 정보와 5일 예보를 확인합니다
4. 다양한 차트와 그래프로 데이터를 시각화합니다

## � Streamlit Cloud 배포

### 1. GitHub에 업로드
1. GitHub에 새 리포지토리 생성
2. 코드 업로드 (`.env` 파일은 자동으로 제외됨)

### 2. Streamlit Cloud에서 배포
1. [Streamlit Cloud](https://share.streamlit.io/)에 로그인
2. "New app" 클릭
3. GitHub 리포지토리 연결
4. `app.py` 또는 `app_advanced.py` 선택
5. **Secrets** 섹션에서 API 키 설정:
   ```
   OPENWEATHER_API_KEY = "your_actual_api_key_here"
   ```
6. Deploy 클릭

### 3. 배포 완료!
- 자동으로 생성된 URL에서 앱에 접속 가능
- 코드 변경 시 자동으로 재배포

### 🔧 배포 트러블슈팅

**Python 버전 호환성 문제 해결:**
- Streamlit Cloud는 Python 3.13을 사용합니다
- `requirements.txt`에서 패키지 버전을 최신으로 유지하세요
- 오류 발생 시 "Reboot app" 버튼으로 재시작해보세요

**의존성 오류 해결:**
```bash
# 로컬에서 테스트
pip install -r requirements.txt
streamlit run app.py
```

## ️ 기술 스택

- **Frontend**: Streamlit
- **Data Visualization**: Plotly
- **Data Processing**: Pandas
- **API**: OpenWeatherMap API
- **Language**: Python 3.8+ (Python 3.13 호환)

## ⚙️ 시스템 요구사항

- **Python**: 3.8 이상 (Python 3.13 완전 호환)
- **운영체제**: Windows, macOS, Linux
- **메모리**: 최소 512MB RAM
- **네트워크**: 인터넷 연결 (API 호출용)

## 📈 향후 개선 계획

- [ ] 시간별 상세 예보
- [ ] 날씨 알림 기능
- [ ] 즐겨찾는 도시 저장
- [ ] 날씨 히스토리 데이터
- [ ] 다국어 지원
- [ ] 모바일 앱 버전

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

## 🙋‍♂️ 문의사항

프로젝트 관련 문의사항이나 버그 리포트는 이슈를 등록해주세요.

---

⭐ 이 프로젝트가 유용하다면 별표를 눌러주세요!