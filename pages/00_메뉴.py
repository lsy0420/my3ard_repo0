import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

# ── 페이지 설정 ──────────────────────────────────────────────
st.set_page_config(
    page_title="🤖 AI 기업 주식 대시보드",
    page_icon="🤖",
    layout="wide",
)

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #0e1117; }
    /* st.metric 카드 스타일 override */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e2130, #2a2d3e);
        border: 1px solid #2e3250;
        border-radius: 12px;
        padding: 1rem 1.2rem !important;
        text-align: center;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem !important;
        color: #aaaaaa !important;
        justify-content: center;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.4rem !important;
        color: #ffffff !important;
        justify-content: center;
    }
    [data-testid="stMetricDelta"] {
        font-size: 1rem !important;
        justify-content: center;
    }
    .section-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #00d4ff;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ── 종목 정의 ─────────────────────────────────────────────────
US_TICKERS = {
    "NVIDIA":    "NVDA",
    "Microsoft": "MSFT",
    "Alphabet":  "GOOGL",
    "Meta":      "META",
    "Amazon":    "AMZN",
    "Tesla":     "TSLA",
    "AMD":       "AMD",
    "Palantir":  "PLTR",
    "C3.ai":     "AI",
}

KR_TICKERS = {
    "삼성전자":   "005930.KS",
    "SK하이닉스": "000660.KS",
    "LG전자":     "066570.KS",
}

ALL_TICKERS = {**US_TICKERS, **KR_TICKERS}

COLORS = (
    px.colors.qualitative.Vivid
    + px.colors.qualitative.Pastel
    + px.colors.qualitative.Safe
)

# ── 사이드바 ──────────────────────────────────────────────────
st.sidebar.title("⚙️ 설정")

st.sidebar.markdown("**🇺🇸 미국 AI 기업**")
us_selected = st.sidebar.multiselect(
    "미국 종목 선택",
    options=list(US_TICKERS.keys()),
    default=["NVIDIA", "Microsoft", "Alphabet", "Meta", "AMD"],
)

st.sidebar.markdown("**🇰🇷 한국 기업**")
kr_selected = st.sidebar.multiselect(
    "한국 종목 선택",
    options=list(KR_TICKERS.keys()),
    default=["삼성전자", "SK하이닉스", "LG전자"],
)

selected_names = us_selected + kr_selected

if not selected_names:
    st.warning("왼쪽 사이드바에서 종목을 1개 이상 선택하세요.")
    st.stop()

show_krw = st.sidebar.checkbox("한국 주식을 원화(₩)로 표시", value=True)

end_date   = datetime.today()
start_date = end_date - timedelta(days=365 * 20)

# ── 데이터 로드 ───────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_prices(names, start, end):
    ticker_map = {n: ALL_TICKERS[n] for n in names}
    symbols    = list(ticker_map.values())
    raw = yf.download(
        symbols, start=start, end=end,
        auto_adjust=True, progress=False
    )
    if isinstance(raw.columns, pd.MultiIndex):
        close = raw["Close"].copy()
    else:
        close = raw[["Close"]].copy()
        close.columns = symbols
    inv_map = {v: k for k, v in ticker_map.items()}
    close.rename(columns=inv_map, inplace=True)
    return close.dropna(how="all")

with st.spinner("📡 데이터 불러오는 중..."):
    df = load_prices(
        selected_names,
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d"),
    )

company_names = [n for n in selected_names if n in df.columns]

def display_price(name, value):
    if name in KR_TICKERS and show_krw:
        return f"₩{value:,.0f}"
    return f"${value:,.2f}"

# ── 헤더 ─────────────────────────────────────────────────────
st.title("🤖 AI 주요 기업 주식 대시보드")
st.caption(
    f"데이터 기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}"
    "  |  출처: Yahoo Finance"
)

# ── KPI 카드 ─────────────────────────────────────────────────
st.markdown('<div class="section-title">📌 20년 누적 수익률</div>', unsafe_allow_html=True)

# 한 행에 최대 4개씩 나눠서 표시
CARDS_PER_ROW = 4
kpi_data = []
for name in company_names:
    series = df[name].dropna()
    if len(series) < 2:
        continue
    total_ret = (series.iloc[-1] / series.iloc[0] - 1) * 100
    cur_price = series.iloc[-1]
    flag      = "🇰🇷" if name in KR_TICKERS else "🇺🇸"
    kpi_data.append((flag, name, cur_price, total_ret))

for row_start in range(0, len(kpi_data), CARDS_PER_ROW):
    row_items = kpi_data[row_start:row_start + CARDS_PER_ROW]
    cols = st.columns(CARDS_PER_ROW)
    for col, (flag, name, cur_price, total_ret) in zip(cols, row_items):
        with col:
            st.metric(
                label=f"{flag} {name}",
                value=display_price(name, cur_price),
                delta=f"{total_ret:+,.1f}%",
            )

st.markdown("---")

# ── 차트 1: 절대 주가 추이 (이중 Y축) ───────────────────────
st.markdown('<div class="section-title">📈 주가 추이 (절대값)</div>', unsafe_allow_html=True)
st.caption("한국(KRW, 우측 축)과 미국(USD, 좌측 축)은 단위가 달라 이중 축으로 표시합니다.")

fig1 = go.Figure()
for i, name in enumerate(company_names):
    series = df[name].dropna()
    is_kr  = name in KR_TICKERS
    fig1.add_trace(go.Scatter(
        x=series.index,
        y=series.values,
        name=name,
        yaxis="y2" if is_kr else "y",
        line=dict(width=2, color=COLORS[i % len(COLORS)]),
        hovertemplate=(
            f"<b>{'🇰🇷' if is_kr else '🇺🇸'} {name}</b><br>"
            f"날짜: %{{x|%Y-%m-%d}}<br>"
            + ("₩%{y:,.0f}" if is_kr else "$%{y:,.2f}")
            + "<extra></extra>"
        ),
    ))
fig1.update_layout(
    template="plotly_dark", height=480,
    hovermode="x unified",
    yaxis =dict(title="주가 (USD 🇺🇸)", side="left",  showgrid=True),
    yaxis2=dict(title="주가 (KRW 🇰🇷)", side="right", overlaying="y", showgrid=False),
    legend=dict(orientation="h", y=-0.22),
    margin=dict(l=60, r=60, t=20, b=90),
)
st.plotly_chart(fig1, use_container_width=True)

# ── 차트 2: 정규화 주가 비교 ─────────────────────────────────
st.markdown('<div class="section-title">📊 정규화 주가 비교 (시작점 = 100)</div>', unsafe_allow_html=True)
st.caption("시작 시점을 100으로 통일해 한국·미국 기업의 성장률을 동일 선상에서 비교합니다.")

fig2 = go.Figure()
for i, name in enumerate(company_names):
    series = df[name].dropna()
    norm   = series / series.iloc[0] * 100
    flag   = "🇰🇷" if name in KR_TICKERS else "🇺🇸"
    fig2.add_trace(go.Scatter(
        x=norm.index, y=norm.values,
        name=f"{flag} {name}",
        line=dict(width=2, color=COLORS[i % len(COLORS)]),
        hovertemplate=f"<b>{flag} {name}</b><br>%{{x|%Y-%m-%d}}<br>지수: %{{y:,.1f}}<extra></extra>",
    ))
fig2.add_hline(y=100, line_dash="dash", line_color="#555", annotation_text="기준(100)")
fig2.update_layout(
    template="plotly_dark", height=450,
    xaxis_title="날짜", yaxis_title="지수 (시작=100)",
    hovermode="x unified",
    legend=dict(orientation="h", y=-0.22),
    margin=dict(l=60, r=20, t=20, b=90),
)
st.plotly_chart(fig2, use_container_width=True)

# ── 차트 3: 연간 수익률 막대 ─────────────────────────────────
st.markdown('<div class="section-title">📅 연간 수익률 (%)</div>', unsafe_allow_html=True)

annual = {}
for name in company_names:
    series = df[name].dropna()
    yearly = series.resample("YE").last()
    ret    = yearly.pct_change().dropna() * 100
    annual[name] = ret

all_years = sorted({yr for ret in annual.values() for yr in ret.index.year})

fig3 = go.Figure()
for i, name in enumerate(company_names):
    ret     = annual[name]
    by_year = {r.year: v for r, v in ret.items()}
    y_vals  = [by_year.get(yr) for yr in all_years]
    flag    = "🇰🇷" if name in KR_TICKERS else "🇺🇸"
    fig3.add_trace(go.Bar(
        name=f"{flag} {name}",
        x=[str(y) for y in all_years],
        y=y_vals,
        marker_color=COLORS[i % len(COLORS)],
        hovertemplate=f"<b>{flag} {name}</b><br>연도: %{{x}}<br>수익률: %{{y:,.1f}}%<extra></extra>",
    ))
fig3.add_hline(y=0, line_color="#777", line_width=1)
fig3.update_layout(
    template="plotly_dark", height=460,
    barmode="group",
    xaxis_title="연도", yaxis_title="수익률 (%)",
    legend=dict(orientation="h", y=-0.28),
    margin=dict(l=60, r=20, t=20, b=110),
)
st.plotly_chart(fig3, use_container_width=True)

# ── 차트 4: 변동성 vs CAGR 산점도 ────────────────────────────
st.markdown('<div class="section-title">🔵 변동성 vs 연평균 수익률 (버블 크기 = 누적 수익률)</div>', unsafe_allow_html=True)
st.caption("버블이 클수록 20년 누적 수익률이 높습니다.")

scatter_data = []
for i, name in enumerate(company_names):
    series    = df[name].dropna()
    daily_ret = series.pct_change().dropna()
    vol       = daily_ret.std() * np.sqrt(252) * 100
    years_cnt = (series.index[-1] - series.index[0]).days / 365
    cagr      = ((series.iloc[-1] / series.iloc[0]) ** (1 / max(years_cnt, 1)) - 1) * 100
    total_ret = (series.iloc[-1] / series.iloc[0] - 1) * 100
    flag      = "🇰🇷" if name in KR_TICKERS else "🇺🇸"
    scatter_data.append(dict(
        name=name, vol=vol, cagr=cagr,
        total_ret=total_ret, flag=flag,
        color=COLORS[i % len(COLORS)],
    ))

fig4 = go.Figure()
for d in scatter_data:
    bubble_size = max(15, min(abs(d["total_ret"]) / 20, 90))
    fig4.add_trace(go.Scatter(
        x=[d["vol"]], y=[d["cagr"]],
        mode="markers+text",
        name=d["name"],
        text=[f"{d['flag']} {d['name']}"],
        textposition="top center",
        marker=dict(
            size=bubble_size,
            color=d["color"],
            opacity=0.85,
            line=dict(width=1, color="white"),
        ),
        hovertemplate=(
            f"<b>{d['flag']} {d['name']}</b><br>"
            f"연간 변동성: {d['vol']:.1f}%<br>"
            f"CAGR: {d['cagr']:.1f}%<br>"
            f"20년 누적: {d['total_ret']:.0f}%<extra></extra>"
        ),
    ))
fig4.update_layout(
    template="plotly_dark", height=520,
    xaxis_title="연간 변동성 (%)",
    yaxis_title="연평균 수익률 / CAGR (%)",
    showlegend=False,
    margin=dict(l=60, r=20, t=20, b=60),
)
st.plotly_chart(fig4, use_container_width=True)

# ── 차트 5: 월별 수익률 막대 (최근 1년) ─────────────────────
st.markdown('<div class="section-title">🗓️ 최근 1년 월별 수익률</div>', unsafe_allow_html=True)

selected_heat = st.selectbox("종목 선택", company_names)
heat_series   = df[selected_heat].dropna().last("365D")
monthly       = heat_series.resample("ME").last().pct_change().dropna() * 100
months        = [d.strftime("%Y-%m") for d in monthly.index]
values        = monthly.values.tolist()

fig5 = go.Figure(go.Bar(
    x=months, y=values,
    marker_color=["#00c853" if v >= 0 else "#d50000" for v in values],
    hovertemplate="<b>%{x}</b><br>수익률: %{y:.2f}%<extra></extra>",
))
fig5.add_hline(y=0, line_color="#555", line_width=1)
fig5.update_layout(
    template="plotly_dark", height=360,
    xaxis_title="월", yaxis_title="수익률 (%)",
    margin=dict(l=60, r=20, t=20, b=60),
)
st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")
st.caption("⚠️ 본 대시보드는 교육·참고 목적이며 투자 권유가 아닙니다.")

st.markdown("---")
st.caption("⚠️ 본 대시보드는 교육·참고 목적이며 투자 권유가 아닙니다.")
