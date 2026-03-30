import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# ── 페이지 설정 ───────────────────────────────────────────────
st.set_page_config(
    page_title="⚡ 반도체 소재 탐구",
    page_icon="⚡",
    layout="wide",
)

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #0a0e1a; }
    [data-testid="stSidebar"] { background-color: #10152a; }
    .info-box {
        background: linear-gradient(135deg, #1a1f35, #222840);
        border-left: 4px solid #00d4ff;
        border-radius: 8px;
        padding: 0.9rem 1.2rem;
        margin: 0.5rem 0 1.2rem 0;
        color: #c8d8f0;
        font-size: 0.92rem;
        line-height: 1.6;
    }
    .section-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #00d4ff;
        margin-top: 2rem;
        margin-bottom: 0.2rem;
    }
    .card {
        background: linear-gradient(135deg, #1a1f35, #222840);
        border: 1px solid #2e3560;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        text-align: center;
        margin-bottom: 0.4rem;
    }
</style>
""", unsafe_allow_html=True)

# ── 데이터 정의 ───────────────────────────────────────────────
MATERIALS = {
    "Si\n(실리콘)":       {"밴드갭(eV)": 1.12, "전자이동도": 1400, "열전도율": 150,  "절연파괴전압": 0.3,  "최대동작온도": 150,  "색": "#4C9BE8", "용도": "스마트폰·PC·태양광 등 가장 많이 쓰이는 반도체"},
    "GaAs\n(갈륨비소)":   {"밴드갭(eV)": 1.42, "전자이동도": 8500, "열전도율": 46,   "절연파괴전압": 0.4,  "최대동작온도": 200,  "색": "#E84C9B", "용도": "5G 기지국·위성통신·레이저 다이오드"},
    "SiC\n(실리콘카바이드)":{"밴드갭(eV)": 3.26, "전자이동도": 900,  "열전도율": 490,  "절연파괴전압": 2.8,  "최대동작온도": 600,  "색": "#E8A04C", "용도": "전기차 인버터·고속 철도·산업용 전력"},
    "GaN\n(질화갈륨)":    {"밴드갭(eV)": 3.39, "전자이동도": 2000, "열전도율": 130,  "절연파괴전압": 3.3,  "최대동작온도": 500,  "색": "#4CE87A", "용도": "65W 고속충전기·5G RF칩·LED 조명"},
    "Diamond\n(다이아몬드)":{"밴드갭(eV)": 5.47, "전자이동도": 2200, "열전도율": 2200, "절연파괴전압": 10.0, "최대동작온도": 1000, "색": "#A64CE8", "용도": "극한 환경용 미래 반도체 소재 (연구 단계)"},
}

df = pd.DataFrame(MATERIALS).T.reset_index().rename(columns={"index": "소재"})
df["소재_단순"] = df["소재"].str.split("\n").str[0]  # 범례용 단순 이름

# ── 사이드바 ──────────────────────────────────────────────────
st.sidebar.title("⚙️ 설정")
all_names  = list(MATERIALS.keys())
selected   = st.sidebar.multiselect(
    "비교할 소재 선택",
    options=all_names,
    default=all_names,
)
if not selected:
    st.warning("소재를 1개 이상 선택하세요.")
    st.stop()

df_sel   = df[df["소재"].isin(selected)].copy()
colors   = df_sel["색"].tolist()
names    = df_sel["소재_단순"].tolist()

# ── 헤더 ─────────────────────────────────────────────────────
st.title("⚡ 반도체 소재 물성 비교 대시보드")
st.caption("고등학생을 위한 반도체 핵심 소재 탐구 | 데이터 출처: 반도체 공학 표준값")

# ── 소재 카드 ─────────────────────────────────────────────────
st.markdown('<div class="section-title">🔍 소재별 용도 한눈에 보기</div>', unsafe_allow_html=True)
card_cols = st.columns(len(df_sel))
for col, (_, row) in zip(card_cols, df_sel.iterrows()):
    with col:
        st.markdown(f"""
        <div class="card">
            <div style="font-size:1.1rem;font-weight:700;color:{row['색']};">{row['소재_단순']}</div>
            <div style="font-size:0.75rem;color:#aaa;margin-top:0.4rem;">{row['용도']}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ── 차트 1: 밴드갭 막대 ───────────────────────────────────────
st.markdown('<div class="section-title">🔋 밴드갭 (Band Gap) 비교</div>', unsafe_allow_html=True)
st.markdown("""
<div class="info-box">
💡 <b>밴드갭이란?</b> 전자가 이동하려면 넘어야 하는 에너지 장벽이에요.<br>
밴드갭이 <b>클수록</b> → 높은 전압·고온에서도 버틸 수 있어요 (전기차, 고속충전기에 유리!).<br>
밴드갭이 <b>작을수록</b> → 낮은 에너지로도 작동해 일반 전자기기에 적합해요.
</div>
""", unsafe_allow_html=True)

fig1 = go.Figure()
fig1.add_trace(go.Bar(
    x=names,
    y=df_sel["밴드갭(eV)"].tolist(),
    marker_color=colors,
    text=[f"{v:.2f} eV" for v in df_sel["밴드갭(eV)"]],
    textposition="outside",
    textfont=dict(size=13, color="white"),
    hovertemplate="<b>%{x}</b><br>밴드갭: %{y:.2f} eV<extra></extra>",
))
fig1.add_hline(y=1.12, line_dash="dot", line_color="#4C9BE8",
               annotation_text="Si 기준선 (1.12 eV)", annotation_font_color="#4C9BE8")
fig1.update_layout(
    template="plotly_dark", height=400,
    yaxis_title="밴드갭 (eV)",
    showlegend=False,
    plot_bgcolor="#0a0e1a", paper_bgcolor="#0a0e1a",
    margin=dict(l=50, r=20, t=30, b=50),
    yaxis=dict(range=[0, max(df_sel["밴드갭(eV)"]) * 1.25]),
)
st.plotly_chart(fig1, use_container_width=True)

# ── 차트 2: 레이더 차트 (종합 성능) ──────────────────────────
st.markdown('<div class="section-title">🕸️ 소재별 종합 성능 비교 (레이더 차트)</div>', unsafe_allow_html=True)
st.markdown("""
<div class="info-box">
💡 5가지 물성을 <b>0~100점으로 정규화</b>해서 한눈에 비교해요.<br>
넓을수록 전반적으로 우수한 소재예요. 어떤 소재가 어떤 분야에 특화됐는지 보이나요?
</div>
""", unsafe_allow_html=True)

radar_props = ["밴드갭(eV)", "전자이동도", "열전도율", "절연파괴전압", "최대동작온도"]
radar_labels = ["밴드갭", "전자\n이동도", "열전도율", "절연\n파괴전압", "최대\n동작온도"]

# 0~100 정규화
norm_df = df_sel[radar_props].copy()
for col in radar_props:
    col_min, col_max = df[col].min(), df[col].max()
    norm_df[col] = (norm_df[col] - col_min) / (col_max - col_min) * 100

fig2 = go.Figure()
for i, (_, row) in enumerate(df_sel.iterrows()):
    vals = norm_df.iloc[i].tolist()
    vals += [vals[0]]  # 닫기
    fig2.add_trace(go.Scatterpolar(
        r=vals,
        theta=radar_labels + [radar_labels[0]],
        name=names[i],
        fill="toself",
        fillcolor=colors[i] + "33",
        line=dict(color=colors[i], width=2),
        hovertemplate="<b>" + names[i] + "</b><br>%{theta}: %{r:.1f}점<extra></extra>",
    ))
fig2.update_layout(
    template="plotly_dark", height=480,
    polar=dict(
        radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=10)),
        angularaxis=dict(tickfont=dict(size=12)),
        bgcolor="#10152a",
    ),
    legend=dict(orientation="h", y=-0.12, font=dict(size=12)),
    plot_bgcolor="#0a0e1a", paper_bgcolor="#0a0e1a",
    margin=dict(l=60, r=60, t=30, b=80),
)
st.plotly_chart(fig2, use_container_width=True)

# ── 차트 3: 버블 차트 ────────────────────────────────────────
st.markdown('<div class="section-title">🔵 전자이동도 vs 절연파괴전압 (버블 크기 = 열전도율)</div>', unsafe_allow_html=True)
st.markdown("""
<div class="info-box">
💡 <b>전자이동도</b>: 전자가 얼마나 빠르게 움직이는지 → 클수록 빠른 소자에 유리해요.<br>
💡 <b>절연파괴전압</b>: 얼마나 높은 전압까지 버티는지 → 클수록 고전력 기기에 유리해요.<br>
💡 <b>버블 크기</b>: 열전도율 → 클수록 열을 잘 식혀줘요 (발열 문제 해결에 중요!).
</div>
""", unsafe_allow_html=True)

fig3 = go.Figure()
for i, (_, row) in enumerate(df_sel.iterrows()):
    fig3.add_trace(go.Scatter(
        x=[row["전자이동도"]],
        y=[row["절연파괴전압"]],
        mode="markers+text",
        name=names[i],
        text=[names[i]],
        textposition="top center",
        textfont=dict(size=12, color="white"),
        marker=dict(
            size=max(20, min(row["열전도율"] / 12, 90)),
            color=row["색"],
            opacity=0.85,
            line=dict(width=1.5, color="white"),
        ),
        hovertemplate=(
            f"<b>{names[i]}</b><br>"
            f"전자이동도: {row['전자이동도']:,} cm²/Vs<br>"
            f"절연파괴전압: {row['절연파괴전압']} MV/cm<br>"
            f"열전도율: {row['열전도율']} W/mK<extra></extra>"
        ),
    ))
fig3.update_layout(
    template="plotly_dark", height=480,
    xaxis_title="전자이동도 (cm²/Vs)  →  클수록 빠른 소자",
    yaxis_title="절연파괴전압 (MV/cm)  →  클수록 고전력",
    showlegend=False,
    plot_bgcolor="#0a0e1a", paper_bgcolor="#0a0e1a",
    margin=dict(l=70, r=20, t=30, b=70),
)
st.plotly_chart(fig3, use_container_width=True)

# ── 차트 4: 최대 동작온도 ─────────────────────────────────────
st.markdown('<div class="section-title">🌡️ 최대 동작 온도 비교</div>', unsafe_allow_html=True)
st.markdown("""
<div class="info-box">
💡 반도체는 온도가 너무 높으면 망가져요.<br>
<b>최대 동작 온도가 높을수록</b> → 우주·엔진룸·발전소 같은 극한 환경에서 사용 가능해요!
</div>
""", unsafe_allow_html=True)

fig4 = go.Figure()
sorted_df = df_sel.sort_values("최대동작온도")
fig4.add_trace(go.Bar(
    x=sorted_df["최대동작온도"].tolist(),
    y=sorted_df["소재_단순"].tolist(),
    orientation="h",
    marker=dict(
        color=sorted_df["색"].tolist(),
        line=dict(width=0),
    ),
    text=[f"{int(v)}°C" for v in sorted_df["최대동작온도"]],
    textposition="outside",
    textfont=dict(size=13, color="white"),
    hovertemplate="<b>%{y}</b><br>최대 동작온도: %{x}°C<extra></extra>",
))
fig4.add_vline(x=150, line_dash="dot", line_color="#4C9BE8",
               annotation_text="Si 한계 (150°C)", annotation_font_color="#4C9BE8",
               annotation_position="top right")
fig4.update_layout(
    template="plotly_dark", height=380,
    xaxis_title="최대 동작 온도 (°C)",
    showlegend=False,
    plot_bgcolor="#0a0e1a", paper_bgcolor="#0a0e1a",
    margin=dict(l=20, r=80, t=30, b=50),
    xaxis=dict(range=[0, max(df_sel["최대동작온도"]) * 1.2]),
)
st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")
st.caption("📚 본 데이터는 교육용 표준 물성값이며, 실제 소자 특성은 제조 공정에 따라 달라질 수 있습니다.")
