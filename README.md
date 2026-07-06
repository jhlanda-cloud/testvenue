# 서울시 문화공간 정보 분석 대시보드

서울시 문화공간 1,067개 시설 데이터를 pandas로 전처리하고 Streamlit + Plotly로 시각화한 대시보드입니다.

## 주요 기능
- 주제분류 / 무료·유료 / 자치구별 문화공간 분포
- 자치구 × 주제분류 히트맵
- 개관 연도별 추이
- 위·경도 기반 지도 시각화
- 자치구 / 주제분류 / 무료구분 필터 및 CSV 다운로드

## 배포에 필요한 파일
| 파일 | 설명 |
|---|---|
| `seoul_culture.py` | 메인 앱 (Streamlit) |
| `requirements.txt` | 의존성 (streamlit, pandas, plotly) |
| `서울시 문화공간 정보.csv` | 데이터 (cp949 인코딩) |
| `.streamlit/config.toml` | 테마 설정 |
| `.gitignore` | 배포 제외 파일 |

## 로컬 실행
```bash
pip install -r requirements.txt
streamlit run seoul_culture.py
```

## Streamlit Community Cloud 배포
1. 위 파일들을 GitHub 저장소에 push
   ```bash
   git init
   git add seoul_culture.py requirements.txt "서울시 문화공간 정보.csv" .streamlit/config.toml README.md .gitignore
   git commit -m "서울시 문화공간 분석 대시보드"
   git branch -M main
   git remote add origin https://github.com/<사용자명>/<저장소명>.git
   git push -u origin main
   ```
2. https://share.streamlit.io 접속 → **New app**
3. 저장소 / 브랜치(`main`) / **Main file path: `seoul_culture.py`** 지정
4. **Deploy** 클릭

> 데이터 파일(`서울시 문화공간 정보.csv`)이 반드시 저장소에 함께 올라가야 합니다.
