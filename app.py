import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import time
import os

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

# IP 기반 위치 서비스 URL
IP_LOCATION_URL = "http://ip-api.com/json/"

# 한국의 행정구역 데이터 (도/특별시/광역시 → 시/군/구 → 동/읍/면)
KOREAN_ADMINISTRATIVE_DIVISIONS = {
    "서울특별시": {
        "강남구": {
            "districts": ["역삼동", "개포동", "청담동", "삼성동", "대치동", "신사동", "논현동", "압구정동", "세곡동", "자곡동"],
            "english": "Gangnam-gu, Seoul"
        },
        "강동구": {
            "districts": ["강일동", "상일동", "명일동", "고덕동", "암사동", "천호동", "성내동", "둔촌동"],
            "english": "Gangdong-gu, Seoul"
        },
        "강북구": {
            "districts": ["삼양동", "미아동", "번동", "수유동", "우이동"],
            "english": "Gangbuk-gu, Seoul"
        },
        "강서구": {
            "districts": ["염창동", "등촌동", "화곡동", "가양동", "마곡동", "개화동", "공항동", "방화동"],
            "english": "Gangseo-gu, Seoul"
        },
        "관악구": {
            "districts": ["보라매동", "청림동", "청룡동", "은천동", "성현동", "중앙동", "인헌동", "남현동"],
            "english": "Gwanak-gu, Seoul"
        },
        "광진구": {
            "districts": ["중곡동", "능동", "구의동", "광장동", "자양동", "화양동"],
            "english": "Gwangjin-gu, Seoul"
        },
        "구로구": {
            "districts": ["신도림동", "구로동", "가리봉동", "고척동", "개봉동", "오류동", "항동"],
            "english": "Guro-gu, Seoul"
        },
        "금천구": {
            "districts": ["가산동", "독산동", "시흥동"],
            "english": "Geumcheon-gu, Seoul"
        },
        "노원구": {
            "districts": ["월계동", "공릉동", "하계동", "중계동", "상계동"],
            "english": "Nowon-gu, Seoul"
        },
        "도봉구": {
            "districts": ["쌍문동", "방학동", "창동", "도봉동"],
            "english": "Dobong-gu, Seoul"
        },
        "동대문구": {
            "districts": ["용두동", "제기동", "전농동", "답십리동", "장안동", "청량리동", "회기동", "휘경동"],
            "english": "Dongdaemun-gu, Seoul"
        },
        "동작구": {
            "districts": ["노량진동", "상도동", "상도1동", "본동", "흑석동", "동작동", "사당동", "대방동"],
            "english": "Dongjak-gu, Seoul"
        },
        "마포구": {
            "districts": ["공덕동", "아현동", "용강동", "대흥동", "신수동", "서강동", "서교동", "합정동", "망원동", "연남동", "성산동", "상암동"],
            "english": "Mapo-gu, Seoul"
        },
        "서대문구": {
            "districts": ["충정로동", "미근동", "천연동", "신촌동", "연희동", "홍제동", "홍은동", "남가좌동", "북가좌동"],
            "english": "Seodaemun-gu, Seoul"
        },
        "서초구": {
            "districts": ["서초동", "잠원동", "반포동", "방배동", "양재동", "내곡동"],
            "english": "Seocho-gu, Seoul"
        },
        "성동구": {
            "districts": ["왕십리동", "마장동", "사근동", "행당동", "응봉동", "금남동", "옥수동", "성수동"],
            "english": "Seongdong-gu, Seoul"
        },
        "성북구": {
            "districts": ["성북동", "삼선동", "동선동", "돈암동", "안암동", "보문동", "정릉동", "길음동", "종암동", "하월곡동", "상월곡동"],
            "english": "Seongbuk-gu, Seoul"
        },
        "송파구": {
            "districts": ["풍납동", "거여동", "마천동", "방이동", "오금동", "송파동", "석촌동", "삼전동", "가락동", "문정동", "장지동"],
            "english": "Songpa-gu, Seoul"
        },
        "양천구": {
            "districts": ["목동", "신월동", "신정동"],
            "english": "Yangcheon-gu, Seoul"
        },
        "영등포구": {
            "districts": ["영등포동", "여의도동", "당산동", "도림동", "문래동", "양평동", "신길동", "대림동"],
            "english": "Yeongdeungpo-gu, Seoul"
        },
        "용산구": {
            "districts": ["후암동", "용산동", "남영동", "청파동", "원효로동", "효창동", "용문동", "한강로동", "이촌동", "이태원동", "한남동", "서빙고동"],
            "english": "Yongsan-gu, Seoul"
        },
        "은평구": {
            "districts": ["은평동", "녹번동", "불광동", "갈현동", "구산동", "대조동", "응암동", "역촌동", "신사동", "증산동", "진관동"],
            "english": "Eunpyeong-gu, Seoul"
        },
        "종로구": {
            "districts": ["청운효자동", "사직동", "삼청동", "부암동", "평창동", "무악동", "교남동", "가회동", "종로1가동", "종로2가동", "종로3가동", "종로4가동", "종로5가동", "종로6가동", "이화동", "혜화동", "명륜3가동", "창신동", "숭인동"],
            "english": "Jongno-gu, Seoul"
        },
        "중구": {
            "districts": ["소공동", "회현동", "명동", "필동", "장충동", "광희동", "을지로동", "신당동", "다산동", "약수동", "청구동", "신당5동", "동화동", "황학동", "중림동"],
            "english": "Jung-gu, Seoul"
        },
        "중랑구": {
            "districts": ["면목동", "상봉동", "중화동", "묵동", "망우동", "신내동"],
            "english": "Jungnang-gu, Seoul"
        }
    },
    "부산광역시": {
        "중구": {
            "districts": ["중앙동", "동광동", "대청동", "보수동", "부평동", "광복동", "남포동", "영주동"],
            "english": "Jung-gu, Busan"
        },
        "서구": {
            "districts": ["동대신동", "서대신동", "부민동", "아미동", "초장동", "충무동", "남부민동", "암남동"],
            "english": "Seo-gu, Busan"
        },
        "동구": {
            "districts": ["초량동", "수정동", "좌천동", "범일동"],
            "english": "Dong-gu, Busan"
        },
        "영도구": {
            "districts": ["남항동", "영선동", "신선동", "봉래동", "청학동", "동삼동"],
            "english": "Yeongdo-gu, Busan"
        },
        "부산진구": {
            "districts": ["부전동", "연지동", "초읍동", "양정동", "전포동", "부암동", "당감동", "가야동", "개금동", "범천동"],
            "english": "Busanjin-gu, Busan"
        },
        "동래구": {
            "districts": ["수민동", "복천동", "명륜동", "온천동", "사직동", "안락동", "명장동"],
            "english": "Dongnae-gu, Busan"
        },
        "남구": {
            "districts": ["대연동", "용호동", "용당동", "감만동", "우암동", "문현동"],
            "english": "Nam-gu, Busan"
        },
        "북구": {
            "districts": ["구포동", "금곡동", "화명동", "덕천동", "만덕동"],
            "english": "Buk-gu, Busan"
        },
        "해운대구": {
            "districts": ["우동", "중동", "좌동", "송정동", "반여동", "반송동", "재송동"],
            "english": "Haeundae-gu, Busan"
        },
        "사하구": {
            "districts": ["괴정동", "당리동", "하단동", "장림동", "신평동", "다대동"],
            "english": "Saha-gu, Busan"
        },
        "금정구": {
            "districts": ["부곡동", "장전동", "구서동", "금성동", "회동동", "남산동", "선두구동"],
            "english": "Geumjeong-gu, Busan"
        },
        "강서구": {
            "districts": ["대저동", "가락동", "천가동", "지사동", "강동동", "식만동", "불암동"],
            "english": "Gangseo-gu, Busan"
        },
        "연제구": {
            "districts": ["거제동", "연산동"],
            "english": "Yeonje-gu, Busan"
        },
        "수영구": {
            "districts": ["남천동", "수영동", "망미동", "광안동"],
            "english": "Suyeong-gu, Busan"
        },
        "사상구": {
            "districts": ["삼락동", "모라동", "덕포동", "괘법동", "감전동", "주례동", "학장동", "엄궁동"],
            "english": "Sasang-gu, Busan"
        },
        "기장군": {
            "districts": ["기장읍", "장안읍", "정관읍", "일광면", "철마면"],
            "english": "Gijang-gun, Busan"
        }
    },
    "경기도": {
        "수원시": {
            "districts": ["장안구", "영통구", "팔달구", "연무구"],
            "english": "Suwon-si, Gyeonggi-do"
        },
        "성남시": {
            "districts": ["수정구", "중원구", "분당구"],
            "english": "Seongnam-si, Gyeonggi-do"
        },
        "고양시": {
            "districts": ["덕양구", "일산동구", "일산서구"],
            "english": "Goyang-si, Gyeonggi-do"
        },
        "용인시": {
            "districts": ["처인구", "기흥구", "수지구"],
            "english": "Yongin-si, Gyeonggi-do"
        },
        "부천시": {
            "districts": ["원미구", "소사구", "오정구"],
            "english": "Bucheon-si, Gyeonggi-do"
        },
        "안산시": {
            "districts": ["상록구", "단원구"],
            "english": "Ansan-si, Gyeonggi-do"
        },
        "안양시": {
            "districts": ["만안구", "동안구"],
            "english": "Anyang-si, Gyeonggi-do"
        },
        "남양주시": {
            "districts": ["와부읍", "조안면", "오남읍", "양수리", "진접읍", "진건읍", "별내면", "퇴계원면", "화도읍", "수동면", "호평동", "평내동", "금곡동", "일패동", "이패동", "삼패동", "다산1동", "다산2동", "지금동", "도농동", "별내동"],
            "english": "Namyangju-si, Gyeonggi-do"
        },
        "화성시": {
            "districts": ["노진면", "매송면", "비봉면", "마도면", "송산면", "서신면", "남양읍", "우정읍", "향남읍", "양감면", "정남면", "장안면", "팔탄면", "봉담읍", "동탄면", "병점1동", "병점2동", "반송동", "기배동", "진안동", "동탄1동", "동탄2동", "동탄3동", "동탄4동", "동탄5동", "동탄6동", "동탄7동", "동탄8동"],
            "english": "Hwaseong-si, Gyeonggi-do"
        },
        "평택시": {
            "districts": ["중앙동", "서정동", "평택동", "송탄동", "지산동", "비전동", "세교동", "통복동", "청북읍", "포승읍", "고덕면", "오성면", "현덕면", "서탄면", "진위면", "안중읍", "팽성읍"],
            "english": "Pyeongtaek-si, Gyeonggi-do"
        },
        "의정부시": {
            "districts": ["의정부1동", "의정부2동", "호원1동", "호원2동", "장암동", "신곡1동", "신곡2동", "송산1동", "송산2동", "송산3동", "자금동", "가능동", "흥선동", "녹양동", "민락동", "금오동", "효자동", "고산동"],
            "english": "Uijeongbu-si, Gyeonggi-do"
        },
        "시흥시": {
            "districts": ["대야동", "신천동", "신현동", "은행동", "정왕1동", "정왕2동", "정왕3동", "정왕4동", "과림동", "월곶동", "장현동", "연성동", "능곡동"],
            "english": "Siheung-si, Gyeonggi-do"
        },
        "파주시": {
            "districts": ["파주읍", "문산읍", "법원읍", "조리읍", "탄현면", "파평면", "적성면", "장단면", "군내면", "광탄면", "금촌1동", "금촌2동", "금촌3동", "교하동", "운정1동", "운정2동", "운정3동"],
            "english": "Paju-si, Gyeonggi-do"
        },
        "광명시": {
            "districts": ["광명1동", "광명2동", "광명3동", "광명4동", "광명5동", "광명6동", "광명7동", "철산1동", "철산2동", "철산3동", "철산4동", "하안1동", "하안2동", "하안3동", "하안4동", "소하1동", "소하2동", "학온동"],
            "english": "Gwangmyeong-si, Gyeonggi-do"
        },
        "김포시": {
            "districts": ["김포1동", "김포2동", "사우동", "풍무동", "장기동", "마산동", "운양동", "구래동", "고촌읍", "양촌읍", "대곶면", "월곶면", "하성면", "통진읍"],
            "english": "Gimpo-si, Gyeonggi-do"
        },
        "군포시": {
            "districts": ["군포1동", "군포2동", "당동", "오금동", "산본1동", "산본2동", "금정동", "재궁동", "부곡동", "대야미동", "궁내동"],
            "english": "Gunpo-si, Gyeonggi-do"
        },
        "하남시": {
            "districts": ["신장1동", "신장2동", "천현동", "덕풍1동", "덕풍2동", "덕풍3동", "상산곡동", "하산곡동", "감북동", "감일동", "초이동", "창우동", "풍산동", "선동", "미사1동", "미사2동"],
            "english": "Hanam-si, Gyeonggi-do"
        },
        "오산시": {
            "districts": ["오산동", "원동", "세교동", "초평동", "은계동", "양산동", "내삼미동", "외삼미동", "금암동", "누읍동", "가수동", "서동", "궐동", "갈곶동"],
            "english": "Osan-si, Gyeonggi-do"
        },
        "이천시": {
            "districts": ["중리동", "증포동", "관고동", "갈산동", "창전동", "부발읍", "신둔면", "백사면", "호법면", "설성면", "마장면", "율면"],
            "english": "Icheon-si, Gyeonggi-do"
        },
        "안성시": {
            "districts": ["중앙동", "석정동", "당왕동", "월곡동", "공도읍", "보개면", "금광면", "서운면", "미양면", "대덕면", "양성면", "원곡면", "일죽면", "죽산면", "삼죽면"],
            "english": "Anseong-si, Gyeonggi-do"
        },
        "의왕시": {
            "districts": ["내손동", "포일동", "고천동", "오전동", "왕곡동", "청계동", "부곡동"],
            "english": "Uiwang-si, Gyeonggi-do"
        },
        "구리시": {
            "districts": ["인창동", "교문동", "수택동", "아천동", "갈매동"],
            "english": "Guri-si, Gyeonggi-do"
        },
        "양주시": {
            "districts": ["양주동", "회천동", "덕정동", "고읍동", "백석읍", "은현면", "남면", "광적면", "장흥면"],
            "english": "Yangju-si, Gyeonggi-do"
        },
        "동두천시": {
            "districts": ["생연동", "중앙동", "불현동", "송내동", "보산동", "상패동", "하패동", "탑동동"],
            "english": "Dongducheon-si, Gyeonggi-do"
        },
        "과천시": {
            "districts": ["중앙동", "갈현동", "별양동", "과천동", "원문동", "막계동", "문원동", "관문동"],
            "english": "Gwacheon-si, Gyeonggi-do"
        },
        "여주시": {
            "districts": ["여흥동", "오학동", "중앙동", "상동", "하동", "능서면", "흥천면", "가남읍", "점동면", "여주읍", "대신면", "북내면", "산북면"],
            "english": "Yeoju-si, Gyeonggi-do"
        },
        "연천군": {
            "districts": ["연천읍", "전곡읍", "청산면", "백학면", "미산면", "왕징면", "군남면", "신서면", "중면"],
            "english": "Yeoncheon-gun, Gyeonggi-do"
        },
        "가평군": {
            "districts": ["가평읍", "청평면", "상면", "하면", "북면", "조종면", "설악면"],
            "english": "Gapyeong-gun, Gyeonggi-do"
        },
        "양평군": {
            "districts": ["양평읍", "강상면", "강하면", "양서면", "서종면", "단월면", "청운면", "용문면", "지제면", "옥천면", "중미산면", "개군면"],
            "english": "Yangpyeong-gun, Gyeonggi-do"
        },
        "포천시": {
            "districts": ["포천동", "소흘읍", "가산면", "창수면", "영중면", "이동면", "화현면", "군내면", "내촌면", "신북면", "영북면", "관인면", "일동면", "중면", "추가면"],
            "english": "Pocheon-si, Gyeonggi-do"
        }
    },
    "인천광역시": {
        "중구": {
            "districts": ["신흥동", "도원동", "유동", "송학동", "운서동", "을왕동"],
            "english": "Jung-gu, Incheon"
        },
        "동구": {
            "districts": ["만석동", "화평동", "송현동", "금곡동"],
            "english": "Dong-gu, Incheon"
        },
        "미추홀구": {
            "districts": ["숭의동", "용현동", "학익동", "도화동", "주안동"],
            "english": "Michuhol-gu, Incheon"
        },
        "연수구": {
            "districts": ["옥련동", "선학동", "연수동", "청학동", "동춘동", "송도동"],
            "english": "Yeonsu-gu, Incheon"
        },
        "남동구": {
            "districts": ["구월동", "간석동", "만수동", "서창동", "장수동", "논현동", "고잔동"],
            "english": "Namdong-gu, Incheon"
        },
        "부평구": {
            "districts": ["부평동", "산곡동", "청천동", "갈산동", "삼산동", "일신동"],
            "english": "Bupyeong-gu, Incheon"
        },
        "계양구": {
            "districts": ["계산동", "계양동", "작전동", "서운동", "효성동", "박촌동"],
            "english": "Gyeyang-gu, Incheon"
        },
        "서구": {
            "districts": ["가좌동", "석남동", "청라동", "경서동", "검단동"],
            "english": "Seo-gu, Incheon"
        }
    },
    "강원특별자치도": {
        "춘천시": {
            "districts": ["요선동", "조운동", "온의동", "근화동", "효자동", "석사동", "퇴계동", "우두동", "동면", "동내면", "남면", "서면", "남산면", "사북면", "신북읍", "북산면"],
            "english": "Chuncheon-si, Gangwon-do"
        },
        "원주시": {
            "districts": ["중앙동", "원동", "개운동", "명륜동", "단계동", "태장동", "반곡동", "봉산동", "우산동", "행구동", "소초면", "호저면", "지정면", "문막읍", "새별읍"],
            "english": "Wonju-si, Gangwon-do"
        },
        "강릉시": {
            "districts": ["홍제동", "중앙동", "성남동", "경포동", "교동", "옥천동", "초당동", "운정동", "구정면", "성산면", "왕산면", "옥계면", "주문진읍", "연곡면"],
            "english": "Gangneung-si, Gangwon-do"
        },
        "동해시": {
            "districts": ["천곡동", "송정동", "부곡동", "삼화동", "망상동", "북평동", "묵호동"],
            "english": "Donghae-si, Gangwon-do"
        },
        "속초시": {
            "districts": ["노학동", "조양동", "금호동", "대포동", "청호동", "영랑동", "도문동"],
            "english": "Sokcho-si, Gangwon-do"
        }
    },
    "충청북도": {
        "청주시": {
            "districts": ["상당구", "서원구", "흥덕구", "청원구"],
            "english": "Cheongju-si, Chungcheongbuk-do"
        },
        "충주시": {
            "districts": ["성내동", "중앙동", "칠금동", "연수동", "목행동", "직동", "단월동", "호암동", "교현동", "용탄동", "주덕읍", "산척면", "수안보면", "앙성면", "노은면", "동량면", "중원대로", "신니면", "가금면", "엄정면", "살미면", "대소원면"],
            "english": "Chungju-si, Chungcheongbuk-do"
        },
        "제천시": {
            "districts": ["명동", "청전동", "중앙동", "영천동", "화산동", "신월동", "장락동", "고명동", "의림동", "모산동", "교동", "자작동", "송학면", "덕산면", "한수면", "청풍면", "수산면", "백운면", "봉양읍", "금성면"],
            "english": "Jecheon-si, Chungcheongbuk-do"
        }
    },
    "충청남도": {
        "천안시": {
            "districts": ["동남구", "서북구"],
            "english": "Cheonan-si, Chungcheongnam-do"
        },
        "공주시": {
            "districts": ["웅진동", "중학동", "신관동", "금성동", "옥룡동", "반포면", "의당면", "정안면", "우성면", "탄천면", "계룡면", "유구읍", "이인면", "사곡면"],
            "english": "Gongju-si, Chungcheongnam-do"
        },
        "보령시": {
            "districts": ["동대동", "서린동", "명천동", "대천동", "신흑동", "웅천읍", "주포면", "청라면", "오천면", "남포면", "주교면", "미산면", "성주면", "천북면"],
            "english": "Boryeong-si, Chungcheongnam-do"
        }
    },
    "전라북도": {
        "전주시": {
            "districts": ["완산구", "덕진구"],
            "english": "Jeonju-si, Jeollabuk-do"
        },
        "군산시": {
            "districts": ["중앙동", "조촌동", "경암동", "개정동", "수송동", "나운동", "소룡동", "개복동", "미성동", "옥산면", "회현면", "대야면", "개정면", "성산면", "나포면", "옥도면", "임피면", "서수면"],
            "english": "Gunsan-si, Jeollabuk-do"
        },
        "익산시": {
            "districts": ["중앙동", "모현동", "인화동", "부송동", "남중동", "어양동", "송학동", "신동", "영등동", "마동", "팔봉동", "함라면", "성당면", "낭산면", "여산면", "금마면", "왕궁면", "용안면", "춘포면", "웅포면", "망성면", "황등면", "용동면", "오산면"],
            "english": "Iksan-si, Jeollabuk-do"
        }
    },
    "전라남도": {
        "목포시": {
            "districts": ["용해동", "산정동", "용당동", "대안동", "연산동", "연동", "하당동", "석현동", "옥암동", "이로동", "부흥동", "죽교동", "상동", "유달동", "온금동", "서산동"],
            "english": "Mokpo-si, Jeollanam-do"
        },
        "여수시": {
            "districts": ["중앙동", "광림동", "서강동", "대교동", "문수동", "남산동", "시전동", "한려동", "여서동", "여천동", "주삼동", "미평동", "둔덕동", "소라면", "율촌면", "화양면", "남면", "화정면", "돌산읍"],
            "english": "Yeosu-si, Jeollanam-do"
        },
        "순천시": {
            "districts": ["중앙동", "향동", "매곡동", "왕조동", "조곡동", "풍덕동", "연향동", "덕연동", "인월동", "도사동", "해룡면", "황전면", "송광면", "주암면", "낙안면", "보성강변", "외서면", "상사면", "별량면", "승주읍"],
            "english": "Suncheon-si, Jeollanam-do"
        }
    },
    "경상북도": {
        "포항시": {
            "districts": ["남구", "북구"],
            "english": "Pohang-si, Gyeongsangbuk-do"
        },
        "경주시": {
            "districts": ["월성동", "동천동", "황남동", "용강동", "보문동", "성건동", "중부동", "계림동", "황오동", "배동", "탑동", "불국동", "진현동", "용황동", "건천읍", "감포읍", "양북면", "양남면", "내남면", "서면", "산내면", "외동읍", "안강읍", "현곡면", "산대남면"],
            "english": "Gyeongju-si, Gyeongsangbuk-do"
        },
        "안동시": {
            "districts": ["중구동", "명륜동", "용상동", "평화동", "서구동", "송현동", "강남동", "옥동", "태화동", "정하동", "법흥동", "임하면", "도산면", "서후면", "일직면", "남선면", "남후면", "길안면", "북후면", "예안면", "풍천면", "녹전면", "와룡면", "임동면", "풍산읍", "풍북면"],
            "english": "Andong-si, Gyeongsangbuk-do"
        },
        "구미시": {
            "districts": ["송정동", "원평동", "지산동", "인동동", "도량동", "선산읍", "고아읍", "옥성면", "도개면", "무을면", "해평면", "산동면", "상모사곡면", "장천면"],
            "english": "Gumi-si, Gyeongsangbuk-do"
        }
    },
    "경상남도": {
        "창원시": {
            "districts": ["의창구", "성산구", "마산합포구", "마산회원구", "진해구"],
            "english": "Changwon-si, Gyeongsangnam-do"
        },
        "진주시": {
            "districts": ["중앙동", "상대동", "하대동", "상봉동", "하봉동", "초장동", "평거동", "신안동", "이현동", "충무공동", "성북동", "칠암동", "강남동", "옥봉동"],
            "english": "Jinju-si, Gyeongsangnam-do"
        },
        "통영시": {
            "districts": ["중앙동", "서호동", "미수동", "봉평동", "명정동", "무전동", "도천동", "인평동", "광도면", "욕지면", "한산면", "사량면", "고성면"],
            "english": "Tongyeong-si, Gyeongsangnam-do"
        },
        "사천시": {
            "districts": ["동서동", "벌용동", "선구동", "정동면", "곤양면", "곤명면", "서포면", "사남면", "용현면"],
            "english": "Sacheon-si, Gyeongsangnam-do"
        }
    },
    "제주특별자치도": {
        "제주시": {
            "districts": ["일도동", "이도동", "삼도동", "용담동", "건입동", "화북동", "삼양동", "봉개동", "아라동", "오라동", "연동", "노형동", "외도동", "이호동", "도두동", "애월읍", "구좌읍", "조천읍", "한림읍", "한경면", "추자면", "우도면"],
            "english": "Jeju-si, Jeju-do"
        },
        "서귀포시": {
            "districts": ["동홍동", "서홍동", "대륜동", "중앙동", "천지동", "효돈동", "영천동", "토평동", "서강동", "중문동", "예래동", "하원동", "강정동", "법환동", "색달동", "위미동", "남원읍", "성산읍", "안덕면", "대정읍", "한남읍", "표선면"],
            "english": "Seogwipo-si, Jeju-do"
        }
    }
}

# 빠른 도시 검색을 위한 간단한 매핑
SIMPLE_CITY_MAPPING = {
    # 특별시/광역시
    "서울": "Seoul",
    "부산": "Busan",
    "인천": "Incheon", 
    "대구": "Daegu",
    "대전": "Daejeon",
    "광주": "Gwangju",
    "울산": "Ulsan",
    "세종": "Sejong",
    
    # 경기도 주요 도시
    "수원": "Suwon",
    "성남": "Seongnam",
    "고양": "Goyang",
    "용인": "Yongin",
    "부천": "Bucheon",
    "안산": "Ansan",
    "안양": "Anyang",
    "남양주": "Namyangju",
    "화성": "Hwaseong",
    "평택": "Pyeongtaek",
    "의정부": "Uijeongbu",
    "시흥": "Siheung",
    "파주": "Paju",
    "광명": "Gwangmyeong",
    "김포": "Gimpo",
    "군포": "Gunpo",
    "하남": "Hanam",
    "오산": "Osan",
    "이천": "Icheon",
    "안성": "Anseong",
    "의왕": "Uiwang",
    "구리": "Guri",
    "양주": "Yangju",
    "동두천": "Dongducheon",
    "과천": "Gwacheon",
    "여주": "Yeoju",
    "포천": "Pocheon",
    
    # 강원도
    "춘천": "Chuncheon",
    "원주": "Wonju",
    "강릉": "Gangneung",
    "동해": "Donghae",
    "속초": "Sokcho",
    
    # 충청도
    "청주": "Cheongju",
    "충주": "Chungju",
    "제천": "Jecheon",
    "천안": "Cheonan",
    "공주": "Gongju",
    "보령": "Boryeong",
    
    # 전라도
    "전주": "Jeonju",
    "군산": "Gunsan",
    "익산": "Iksan",
    "목포": "Mokpo",
    "여수": "Yeosu",
    "순천": "Suncheon",
    
    # 경상도
    "포항": "Pohang",
    "경주": "Gyeongju",
    "안동": "Andong",
    "구미": "Gumi",
    "창원": "Changwon",
    "진주": "Jinju",
    "통영": "Tongyeong",
    "사천": "Sacheon",
    
    # 제주도
    "제주": "Jeju",
    "서귀포": "Seogwipo"
}

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

def get_current_location():
    """IP 기반으로 현재 위치를 가져오는 함수"""
    try:
        response = requests.get(IP_LOCATION_URL, timeout=5)
        response.raise_for_status()
        location_data = response.json()
        
        if location_data['status'] == 'success':
            return {
                'city': location_data.get('city', ''),
                'country': location_data.get('country', ''),
                'lat': location_data.get('lat', 0),
                'lon': location_data.get('lon', 0),
                'region': location_data.get('regionName', ''),
                'timezone': location_data.get('timezone', '')
            }
        return None
    except Exception as e:
        st.warning(f"위치 정보를 가져올 수 없습니다: {e}")
        return None

def get_weather_by_coordinates(lat, lon):
    """위도, 경도로 날씨 데이터를 가져오는 함수"""
    try:
        params = {
            'lat': lat,
            'lon': lon,
            'appid': API_KEY,
            'units': 'metric',
            'lang': 'kr'
        }
        
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"위치 기반 날씨 데이터를 가져오는데 실패했습니다: {e}")
        return None

def get_forecast_by_coordinates(lat, lon):
    """위도, 경도로 5일 예보 데이터를 가져오는 함수"""
    try:
        params = {
            'lat': lat,
            'lon': lon,
            'appid': API_KEY,
            'units': 'metric',
            'lang': 'kr'
        }
        
        response = requests.get(FORECAST_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"위치 기반 예보 데이터를 가져오는데 실패했습니다: {e}")
        return None

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
    visibility = weather_data.get('visibility', 0) / 1000 if 'visibility' in weather_data else 0
    
    # 일출/일몰 정보
    sunrise = datetime.fromtimestamp(weather_data['sys']['sunrise']).strftime('%H:%M')
    sunset = datetime.fromtimestamp(weather_data['sys']['sunset']).strftime('%H:%M')
    
    # 날씨 아이콘 URL
    icon_url = f"http://openweathermap.org/img/wn/{icon}@4x.png"
    
    # 메인 날씨 정보 표시
    st.markdown(f"""
    <div style='background-color: #ffffff; 
                padding: 2rem; 
                border-radius: 12px; 
                border: 1px solid #dee2e6;
                margin: 2rem 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                text-align: center;'>
        <h2 style='color: #212529; margin-bottom: 1rem; font-weight: 300;'>📍 {city}, {country}</h2>
        <h1 style='color: #495057; font-size: 4rem; margin: 1rem 0; font-weight: 200;'>{temp:.1f}°C</h1>
        <p style='color: #6c757d; font-size: 1.1rem; margin: 0.5rem 0;'>체감온도 {feels_like:.1f}°C</p>
        <p style='color: #495057; font-size: 1rem; margin: 0; text-transform: capitalize;'>{description}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 날씨 아이콘 및 상세 정보
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.markdown("### 🌤️ 날씨")
        st.image(icon_url, width=120)
        
    with col2:
        st.markdown("### ℹ️ 상세 정보")
        
        info_col1, info_col2 = st.columns(2)
        with info_col1:
            st.info(f"🌅 **일출:** {sunrise}")
            st.info(f"👁️ **가시거리:** {visibility:.1f}km")
        with info_col2:
            st.info(f"� **일몰:** {sunset}")
            st.info(f"�️ **체감온도:** {feels_like:.1f}°C")
            
    with col3:
        st.markdown("### � 현재 상태")
        st.write(f"**온도:** {temp:.1f}°C")
        st.write(f"**날씨:** {description}")
    
    # 메트릭 카드들 (Streamlit 기본 컴포넌트 사용)
    st.markdown("---")
    st.markdown("### 📊 상세 날씨 정보")
    
    # 온도에 따른 아이콘 결정
    if temp >= 30:
        temp_icon = "🔥"
    elif temp >= 20:
        temp_icon = "☀️"
    elif temp >= 10:
        temp_icon = "🌤️"
    else:
        temp_icon = "❄️"
    
    col4, col5, col6, col7 = st.columns(4)
    
    with col4:
        st.metric(
            label="💧 습도",
            value=f"{humidity}%",
            help="공기 중 수분 함량"
        )
        
    with col5:
        st.metric(
            label="🌪️ 풍속",
            value=f"{wind_speed} m/s",
            help="바람의 속도"
        )
        
    with col6:
        st.metric(
            label="📊 기압",
            value=f"{pressure} hPa",
            help="대기압 수치"
        )
        
    with col7:
        st.metric(
            label=f"{temp_icon} 현재 온도",
            value=f"{temp:.1f}°C",
            delta=f"체감 {feels_like:.1f}°C",
            help="현재 측정된 온도"
        )

def display_forecast(forecast_data):
    """5일 예보를 표시하는 함수"""
    if not forecast_data:
        return
    
    st.markdown("""
    <h3 style='color: #495057; text-align: center; margin: 2rem 0; font-weight: 400;'>
        📅 5일 예보
    </h3>
    """, unsafe_allow_html=True)
    
    # 예보 데이터 처리
    forecast_list = []
    for item in forecast_data['list'][:40]:  # 5일 * 8회 (3시간 간격)
        date_time = datetime.fromtimestamp(item['dt'])
        forecast_list.append({
            'datetime': date_time,
            'date': date_time.strftime('%m/%d'),
            'time': date_time.strftime('%H:%M'),
            'temp': item['main']['temp'],
            'description': item['weather'][0]['description'],
            'icon': item['weather'][0]['icon'],
            'humidity': item['main']['humidity'],
            'wind_speed': item['wind']['speed']
        })
    
    # 데이터프레임 생성
    df = pd.DataFrame(forecast_list)
    
    # 온도 그래프 (더 예쁘게)
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['datetime'], 
        y=df['temp'],
        mode='lines+markers',
        name='온도',
        line=dict(color='#e74c3c', width=3),
        marker=dict(size=8, color='#c0392b'),
        fill='tonexty',
        fillcolor='rgba(231, 76, 60, 0.1)'
    ))
    
    fig.update_layout(
        title={
            'text': '🌡️ 시간별 온도 변화',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24, 'color': '#2c3e50'}
        },
        xaxis_title='시간',
        yaxis_title='온도 (°C)',
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            gridcolor='rgba(128,128,128,0.2)',
            linecolor='rgba(128,128,128,0.5)'
        ),
        yaxis=dict(
            gridcolor='rgba(128,128,128,0.2)',
            linecolor='rgba(128,128,128,0.5)'
        ),
        font=dict(color='#2c3e50')
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 일별 예보 요약
    daily_forecast = df.groupby('date').agg({
        'temp': ['min', 'max'],
        'description': 'first',
        'icon': 'first',
        'humidity': 'mean',
        'wind_speed': 'mean'
    }).reset_index()
    
    daily_forecast.columns = ['date', 'min_temp', 'max_temp', 'description', 'icon', 'humidity', 'wind_speed']
    
    # 일별 예보 카드 표시 (Streamlit 컴포넌트 사용)
    st.markdown("---")
    
    # 컬럼으로 5일 예보 표시
    cols = st.columns(5)
    

    
    for idx, row in daily_forecast.head(5).iterrows():
        with cols[idx]:
            # 날짜 포맷팅
            current_year = datetime.now().year
            try:
                date_obj = datetime.strptime(f"{current_year}/{row['date']}", "%Y/%m/%d")
                weekday = ["월", "화", "수", "목", "금", "토", "일"][date_obj.weekday()]
            except:
                weekday = ""
            
            # 깔끔한 카드 생성
                
            st.markdown(f"""
            <div style='
                background-color: #ffffff;
                padding: 1.5rem;
                border-radius: 8px;
                border: 1px solid #dee2e6;
                text-align: center;
                margin: 0.5rem 0;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            '>
                <h5 style='margin: 0 0 1rem 0; color: #495057; font-weight: 500;'>{row['date']} ({weekday})</h5>
                <div style='margin: 1rem 0;'>
                    <img src="http://openweathermap.org/img/wn/{row['icon']}@2x.png" width="60" style="display: block; margin: 0 auto;">
                </div>
                <h4 style='color: #495057; margin: 0.5rem 0; font-weight: 500;'>{row['max_temp']:.0f}° / {row['min_temp']:.0f}°</h4>
                <p style='color: #6c757d; margin: 0.5rem 0; font-size: 0.9rem;'>{row['description']}</p>
                <div style='display: flex; justify-content: space-between; margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #dee2e6; font-size: 0.8rem; color: #6c757d;'>
                    <span>💧 {row['humidity']:.0f}%</span>
                    <span>💨 {row['wind_speed']:.1f}m/s</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

def main():
    """메인 함수"""
    # 페이지 설정
    st.set_page_config(
        page_title="날씨 웹앱 🌤️",
        page_icon="🌤️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 미니멀 CSS 스타일
    st.markdown("""
    <style>
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
            max-width: 1200px;
        }
        
        .stApp {
            background-color: #ffffff;
        }
        
        .stSelectbox > div > div > select {
            background-color: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #dee2e6;
            color: #495057;
        }
        
        .stRadio > div {
            background-color: #ffffff;
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid #dee2e6;
        }
        
        .stButton > button {
            background-color: #ffffff;
            color: #495057;
            border-radius: 8px;
            border: 1px solid #dee2e6;
            padding: 0.5rem 1rem;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        
        .stButton > button:hover {
            background-color: #f8f9fa;
            border-color: #adb5bd;
        }
        
        .sidebar .element-container {
            margin-bottom: 1rem;
        }
        
        .weather-card {
            background-color: #ffffff;
            padding: 2rem;
            border-radius: 12px;
            border: 1px solid #dee2e6;
            margin-bottom: 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .metric-card {
            background-color: #f8f9fa;
            padding: 1.5rem;
            border-radius: 8px;
            border: 1px solid #dee2e6;
            text-align: center;
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: #212529 !important;
        }
        
        .stMetric {
            background-color: #ffffff;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 1rem;
        }
        
        .stExpander {
            background-color: #ffffff;
            border: 1px solid #dee2e6;
            border-radius: 8px;
        }
        
        /* 사이드바 스타일 */
        .css-1d391kg {
            background-color: #f8f9fa;
        }
        
        .stSidebar > div {
            background-color: #f8f9fa;
        }
        
        /* 깔끔한 구분선 */
        hr {
            border: none;
            height: 1px;
            background-color: #dee2e6;
            margin: 2rem 0;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # 헤더
    st.markdown("""
    <div style='text-align: center; margin-bottom: 3rem; padding: 2rem 0; border-bottom: 1px solid #dee2e6;'>
        <h1 style='color: #212529; font-size: 2.5rem; font-weight: 300; margin-bottom: 0.5rem; letter-spacing: -1px;'>
            🌤️ Weather
        </h1>
        <p style='color: #6c757d; font-size: 1rem; margin: 0; font-weight: 400;'>
            실시간 날씨 정보와 예보 서비스
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 사이드바
    with st.sidebar:
        st.markdown("### ⚙️ 설정")
        st.markdown("---")
        st.markdown("### 🌍 위치 선택 방법")
        st.markdown("---")
        
        input_method = st.selectbox(
            "선택하세요:",
            ["📍 현재 위치", "🇰🇷 한국 도시", "🌍 해외 도시"],
            help="원하는 위치 선택 방법을 선택하세요"
        )
        
        city_input = "Seoul"  # 기본값
        
        if input_method == "📍 현재 위치":
            st.markdown("#### 📍 현재 위치 자동 감지")
            
            # 설명 박스 - 작은 크기와 연한 회색 배경
            st.markdown("""
            <div style='
                background-color: #f5f5f5; 
                padding: 0.8rem; 
                border-radius: 6px; 
                border: 1px solid #e0e0e0;
                margin: 0.5rem 0;
            '>
                <small style='color: #666666; font-size: 0.85rem;'>
                    💡 IP 주소를 기반으로 현재 위치를 자동으로 찾아드립니다
                </small>
            </div>
            """, unsafe_allow_html=True)
            
            # 위치 찾기 버튼
            if st.button("🔍 현재 위치 찾기", type="primary", use_container_width=True):
                with st.spinner("🌍 위치를 검색하고 있습니다..."):
                    location = get_current_location()
                    if location:
                        st.session_state['current_location'] = location
                        st.balloons()  # 성공 시 풍선 효과
                    else:
                        st.error("❌ 위치를 찾을 수 없습니다. 네트워크 연결을 확인해주세요.")
            
            # 위치 결과 표시
            if 'current_location' in st.session_state:
                location = st.session_state['current_location']
                
                # 예쁜 위치 정보 박스
                st.markdown("---")
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.markdown("### 📍")
                with col2:
                    st.markdown(f"**현재 위치**")
                    st.markdown(f"🏙️ **도시**: {location['city']}")
                    st.markdown(f"🗺️ **지역**: {location['region']}")
                    if 'country' in location:
                        st.markdown(f"🌍 **국가**: {location['country']}")
                
                city_input = location['city']
                
                # 새로 검색 버튼
                if st.button("🔄 다시 검색", key="re_search"):
                    del st.session_state['current_location']
                    st.rerun()
            else:
                st.markdown("---")
                st.markdown("📌 **위 버튼을 클릭하여 현재 위치를 찾아보세요**")
                city_input = "Seoul"
                
        elif input_method == "🇰🇷 한국 도시":
            st.markdown("#### 🇰🇷 대한민국 행정구역 선택")
            
            # 1단계: 시/도 선택
            st.markdown("**🏛️ 1단계: 시/도 선택**")
            selected_province = st.selectbox(
                "광역자치단체를 선택하세요",
                list(KOREAN_ADMINISTRATIVE_DIVISIONS.keys()),
                key="province_select"
            )
            
            st.markdown("")  # 빈 줄 추가
            
            # 2단계: 시/군/구 선택
            st.markdown("**🏙️ 2단계: 시/군/구 선택**")
            if selected_province:
                city_options = list(KOREAN_ADMINISTRATIVE_DIVISIONS[selected_province].keys())
                selected_city = st.selectbox(
                    "기초자치단체를 선택하세요", 
                    city_options,
                    key="city_select"
                )
            else:
                selected_city = None
                st.selectbox("먼저 시/도를 선택해주세요", ["선택 불가"], disabled=True, key="city_disabled")
            
            st.markdown("")  # 빈 줄 추가
            
            # 3단계: 동/읍/면 선택
            st.markdown("**📍 3단계: 동/읍/면 선택**")
            if selected_city:
                district_options = KOREAN_ADMINISTRATIVE_DIVISIONS[selected_province][selected_city]["districts"]
                selected_district = st.selectbox(
                    "상세 지역을 선택하세요", 
                    district_options,
                    key="district_select"
                )
                english_name = KOREAN_ADMINISTRATIVE_DIVISIONS[selected_province][selected_city]["english"]
                city_input = english_name.split(",")[0]
                
                # 선택 결과 표시
                st.markdown("---")
                full_address = f"{selected_province} {selected_city} {selected_district}"
                st.success(f"✅ 선택된 지역: {full_address}")
                st.info(f"🌍 영문명: {english_name}")
            else:
                st.selectbox("먼저 시/군/구를 선택해주세요", ["선택 불가"], disabled=True, key="district_disabled")
                city_input = "Seoul"
            
        else:
            st.markdown("#### 🌍 세계 도시 선택")
            
            city_input = st.text_input("해외 도시명 (영문)", value="Tokyo", 
                                     help="전세계 도시명을 영문으로 입력하세요")
            
            st.markdown("---")
            st.markdown("##### ⚡ 빠른 선택")
            
            # 북미 도시들
            st.markdown("**북미**")
            if st.button("New York", key="ny_usa", use_container_width=True):
                city_input = "New York"
            if st.button("Los Angeles", key="la_usa", use_container_width=True):
                city_input = "Los Angeles"
            if st.button("Chicago", key="chicago_usa", use_container_width=True):
                city_input = "Chicago"
            if st.button("Toronto", key="toronto_ca", use_container_width=True):
                city_input = "Toronto"
            if st.button("Vancouver", key="vancouver_ca", use_container_width=True):
                city_input = "Vancouver"
            
            # 유럽 도시들
            st.markdown("**� 유럽**")
            if st.button("London", key="london_gb", use_container_width=True):
                city_input = "London"
            if st.button("Paris", key="paris_fr", use_container_width=True):
                city_input = "Paris"
            if st.button("Berlin", key="berlin_de", use_container_width=True):
                city_input = "Berlin"
            if st.button("Rome", key="rome_it", use_container_width=True):
                city_input = "Rome"
            if st.button("Madrid", key="madrid_es", use_container_width=True):
                city_input = "Madrid"
            if st.button("Amsterdam", key="amsterdam_nl", use_container_width=True):
                city_input = "Amsterdam"
            
            # 아시아 도시들
            st.markdown("**� 아시아**")
            if st.button("Tokyo", key="tokyo_jp", use_container_width=True):
                city_input = "Tokyo"
            if st.button("Osaka", key="osaka_jp", use_container_width=True):
                city_input = "Osaka"
            if st.button("Bangkok", key="bangkok_th", use_container_width=True):
                city_input = "Bangkok"
            if st.button("Singapore", key="singapore_sg", use_container_width=True):
                city_input = "Singapore"
            if st.button("Hong Kong ��", key="hongkong_hk", use_container_width=True):
                city_input = "Hong Kong"
            if st.button("Mumbai ��", key="mumbai_in", use_container_width=True):
                city_input = "Mumbai"
            
            # 오세아니아 도시들
            st.markdown("**오세아니아**")
            if st.button("Sydney", key="sydney_au", use_container_width=True):
                city_input = "Sydney"
            if st.button("Melbourne", key="melbourne_au", use_container_width=True):
                city_input = "Melbourne"
            if st.button("Auckland", key="auckland_nz", use_container_width=True):
                city_input = "Auckland"
            
            # 기타 도시들
            st.markdown("**기타**")
            if st.button("Dubai", key="dubai_ae", use_container_width=True):
                city_input = "Dubai"
            if st.button("Cairo 🇪�", key="cairo_eg", use_container_width=True):
                city_input = "Cairo"
            if st.button("Moscow", key="moscow_ru", use_container_width=True):
                city_input = "Moscow"
            if st.button("São Paulo", key="saopaulo_br", use_container_width=True):
                city_input = "São Paulo"
        
        st.markdown("---")
        
        # 자동 새로고침 (5분마다)
        st.markdown("#### ⏰ 자동 새로고침")
        st.info("💡 이 페이지는 5분마다 자동으로 새로고침됩니다")
        
        # JavaScript를 이용한 자동 새로고침
        st.markdown("""
        <script>
        setTimeout(function(){
            window.location.reload(1);
        }, 300000); // 5분 = 300000 밀리초
        </script>
        """, unsafe_allow_html=True)
        
        # 수동 새로고침 버튼
        if st.button("🔄 지금 새로고침", use_container_width=True):
            st.rerun()
        
        st.markdown("---")
        st.caption("🌤️ OpenWeatherMap API")
    
    # 메인 컨텐츠
    if city_input or (input_method == "📍 현재 위치" and 'current_location' in st.session_state):
        
        # 위치 기반 또는 도시명 기반으로 데이터 가져오기
        if input_method == "📍 현재 위치" and 'current_location' in st.session_state:
            location = st.session_state['current_location']
            with st.spinner(f"{location['city']}의 날씨 정보를 가져오는 중..."):
                weather_data = get_weather_by_coordinates(location['lat'], location['lon'])
                forecast_data = get_forecast_by_coordinates(location['lat'], location['lon'])
        else:
            with st.spinner(f"{city_input}의 날씨 정보를 가져오는 중..."):
                weather_data = get_weather_data(city_input)
                forecast_data = get_forecast_data(city_input)
        
        if weather_data:
            # 현재 날씨 표시
            display_current_weather(weather_data)
            
            st.markdown("---")
            
            # 5일 예보 표시
            display_forecast(forecast_data)
            
            # 추가 정보
            with st.expander("📋 상세 정보"):
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("🌤️ 현재 날씨 데이터")
                    st.json(weather_data)
                
                if input_method == "📍 현재 위치" and 'current_location' in st.session_state:
                    with col2:
                        st.subheader("📍 위치 정보")
                        location = st.session_state['current_location']
                        st.json({
                            "도시": location['city'],
                            "지역": location['region'],
                            "국가": location['country'],
                            "위도": location['lat'],
                            "경도": location['lon'],
                            "시간대": location['timezone']
                        })
        
        else:
            st.error("❌ 날씨 정보를 찾을 수 없습니다. 다른 위치나 도시명을 시도해보세요.")
    
    else:
        # 기본 화면
        st.info("👆 사이드바에서 위치를 선택하거나 도시명을 입력해주세요.")
        
        st.info("사이드바에서 위치를 선택해주세요")
        st.markdown("### 🌤️ 사용 방법")
        st.markdown("""
        - **📍 현재 위치**: 자동으로 현재 위치의 날씨 확인
        - **🇰🇷 한국 도시**: 시/도 → 시/군/구 → 동/읍/면 선택
        - **🌍 해외 도시**: 전세계 주요 도시 선택 또는 직접 입력
        """)
    
    # 푸터
    st.markdown("---")
    st.markdown("<div style='text-align: center; color: #6c757d; font-size: 0.9rem;'>🌤️ Weather App | OpenWeatherMap API</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()