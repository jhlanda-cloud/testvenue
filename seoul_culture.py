# -*- coding: utf-8 -*-
"""
서울시 문화공간 정보 분석 대시보드
데이터: 서울시 문화공간 정보.csv (cp949)
사용: pandas, streamlit, plotly
"""

import re
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="서울시 문화공간 분석", page_icon="🏛️", layout="wide")

CSV_FILE = "서울시 문화공간 정보.csv"


@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="cp949")
    df.columns = [c.strip() for c in df.columns]

    # 좌표 숫자화
    df["위도"] = pd.to_numeric(df["위도"], errors="coerce")
    df["경도"] = pd.to_numeric(df["경도"], errors="coerce")

    # 개관 연도 추출 (다양한 포맷에서 4자리 연도만)
    def extract_year(v):
        if not isinstance(v, str):
            return None
        m = re.search(r"(19|20)\d{2}", v)
        return int(m.group()) if m else None

    df["개관연도"] = df["개관일자"].apply(extract_year)
    return df


df = load_data(CSV_FILE)

# ----------------------------------------------------------------------
# 사이드바 필터
# ----------------------------------------------------------------------
st.sidebar.header("🔎 필터")

gu_list = sorted(df["자치구"].dropna().unique().tolist())
sel_gu = st.sidebar.multiselect("자치구", gu_list, default=gu_list)

type_list = sorted(df["주제분류"].dropna().unique().tolist())
sel_type = st.sidebar.multiselect("주제분류", type_list, default=type_list)

fee_opts = df["무료구분"].dropna().unique().tolist()
sel_fee = st.sidebar.multiselect("무료구분", fee_opts, default=fee_opts)

fdf = df[
    df["자치구"].isin(sel_gu)
    & df["주제분류"].isin(sel_type)
    & df["무료구분"].isin(sel_fee)
].copy()

# ----------------------------------------------------------------------
# 헤더 & 지표
# ----------------------------------------------------------------------
st.title("🏛️ 서울시 문화공간 정보 분석")
st.caption("출처: 서울시 문화공간 정보 · 1,067개 시설")

c1, c2, c3, c4 = st.columns(4)
c1.metric("총 문화공간", f"{len(fdf):,} 개")
c2.metric("자치구 수", f"{fdf['자치구'].nunique()} 개")
free_ratio = (fdf["무료구분"] == "무료").mean() * 100 if len(fdf) else 0
c3.metric("무료 시설 비율", f"{free_ratio:.1f} %")
c4.metric("시설 유형 수", f"{fdf['주제분류'].nunique()} 종")

st.divider()

if fdf.empty:
    st.warning("선택한 조건에 해당하는 문화공간이 없습니다.")
    st.stop()

# ----------------------------------------------------------------------
# 그래프 1행: 유형별 / 무료구분
# ----------------------------------------------------------------------
col1, col2 = st.columns((2, 1))

with col1:
    st.subheader("📊 주제분류별 문화공간 수")
    tc = fdf["주제분류"].value_counts()
    tdf = pd.DataFrame({"주제분류": tc.index, "시설 수": tc.values})
    fig = px.bar(
        tdf, x="시설 수", y="주제분류", orientation="h", text="시설 수",
        color="시설 수", color_continuous_scale="Viridis",
    )
    fig.update_layout(
        coloraxis_showscale=False, xaxis_title="", yaxis_title="",
        yaxis={"categoryorder": "total ascending"},
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🎟️ 무료 / 유료")
    fc = fdf["무료구분"].value_counts()
    fig = px.pie(
        names=fc.index, values=fc.values, hole=0.45,
        color=fc.index,
        color_discrete_map={"무료": "#2E86C1", "유료": "#E67E22"},
    )
    fig.update_traces(textinfo="label+percent")
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------------------
# 그래프 2행: 자치구별 TOP / 개관 연도 추이
# ----------------------------------------------------------------------
col3, col4 = st.columns(2)

with col3:
    st.subheader("🗺️ 자치구별 문화공간 TOP 15")
    gc = fdf["자치구"].value_counts().head(15)
    gdf = pd.DataFrame({"자치구": gc.index, "시설 수": gc.values})
    fig = px.bar(
        gdf, x="자치구", y="시설 수", text="시설 수",
        color="시설 수", color_continuous_scale="Blues",
    )
    fig.update_layout(coloraxis_showscale=False, xaxis_title="", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

with col4:
    st.subheader("📈 개관 연도별 추이")
    yc = (
        fdf.dropna(subset=["개관연도"])
        .loc[lambda d: d["개관연도"] >= 1950, "개관연도"]
        .astype(int)
        .value_counts()
        .sort_index()
    )
    if len(yc):
        ydf = pd.DataFrame({"연도": yc.index, "개관 수": yc.values})
        fig = px.line(ydf, x="연도", y="개관 수", markers=True)
        fig.update_layout(xaxis_title="", yaxis_title="개관 수")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("개관연도 정보가 없습니다.")

# ----------------------------------------------------------------------
# 그래프 3행: 자치구 × 주제분류 히트맵
# ----------------------------------------------------------------------
st.subheader("🔥 자치구 × 주제분류 분포 (히트맵)")
top_gu = fdf["자치구"].value_counts().head(12).index.tolist()
pivot = (
    fdf[fdf["자치구"].isin(top_gu)]
    .pivot_table(index="자치구", columns="주제분류", values="문화시설명",
                 aggfunc="count", fill_value=0)
    .reindex(top_gu)
)
fig = px.imshow(
    pivot, text_auto=True, aspect="auto", color_continuous_scale="YlOrRd",
    labels=dict(x="주제분류", y="자치구", color="시설 수"),
)
st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------------------
# 지도
# ----------------------------------------------------------------------
st.subheader("📍 문화공간 위치 지도")
map_df = fdf.dropna(subset=["위도", "경도"])
map_df = map_df[(map_df["위도"].between(37.3, 37.75)) & (map_df["경도"].between(126.7, 127.3))]
fig = px.scatter_mapbox(
    map_df, lat="위도", lon="경도", color="주제분류",
    hover_name="문화시설명", hover_data={"자치구": True, "위도": False, "경도": False},
    zoom=10, height=550,
)
fig.update_layout(mapbox_style="open-street-map", margin=dict(l=0, r=0, t=0, b=0))
st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------------------
# 상세 목록
# ----------------------------------------------------------------------
st.subheader("📋 문화공간 상세 목록")
show_cols = ["문화시설명", "주제분류", "자치구", "주소", "무료구분", "관람시간", "홈페이지"]
st.dataframe(fdf[show_cols], use_container_width=True, hide_index=True)

csv_out = fdf[show_cols].to_csv(index=False).encode("utf-8-sig")
st.download_button("⬇️ 필터 결과 CSV 다운로드", data=csv_out,
                   file_name="서울문화공간_필터결과.csv", mime="text/csv")
