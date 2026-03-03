import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# ═══════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO DA PÁGINA
# ═══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Análise Voos PDL · AzData Solutions",
    page_icon="∧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════
# BRAND COLORS — AzData Solutions
# ═══════════════════════════════════════════════════════════════════
AZ_AQUA      = "#22D4DF"   # Aqua Atlântico  — primária / accent
AZ_TEAL      = "#0E9AA7"   # Teal Oceano     — secundária / botões
AZ_BLUE      = "#0B4F6C"   # Azul Profundo   — fundos / cards
AZ_GREEN     = "#2ECC8F"   # Verde Vulcânico — sucesso / destaque
AZ_LAVA      = "#E85D35"   # Laranja Lava    — alertas / CTAs
AZ_MIDNIGHT  = "#050F14"   # Midnight Deep   — background principal
AZ_MID_CARD  = "#0A1A24"   # card bg ligeiramente mais claro
AZ_BORDER    = "#0E2D3F"   # bordas sutis

# Mapeamento de categorias → brand colors
CORES_TIPO = {
    "Inter-Ilhas":    AZ_AQUA,
    "Territoriais":   AZ_TEAL,
    "Internacionais": AZ_GREEN,
}
COR_2025 = "#1A4A5C"   # versão escura do teal para linha 2025
COR_2026 = AZ_AQUA     # aqua atlântico para linha 2026

# ═══════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO GLOBAL DE GRÁFICOS PLOTLY
# ═══════════════════════════════════════════════════════════════════
PLOT_TRANSPARENT = "rgba(0,0,0,0)"
GRID_COLOR       = "rgba(14,154,167,0.08)"
AXIS_LINE_COLOR  = "rgba(14,154,167,0.15)"
TICK_COLOR       = "#4A7A8A"
LABEL_COLOR      = "#5A8A9A"
TITLE_COLOR      = "#7ABFCC"
LEGEND_COLOR     = "#5A8A9A"

AXIS_BASE = dict(
    gridcolor=GRID_COLOR,
    linecolor=AXIS_LINE_COLOR,
    zerolinecolor=AXIS_LINE_COLOR,
    tickfont=dict(color=TICK_COLOR, size=11, family="DM Sans"),
    title_font=dict(color=LABEL_COLOR, size=11, family="DM Sans"),
)

LAYOUT_BASE = dict(
    template="plotly_white",
    plot_bgcolor=PLOT_TRANSPARENT,
    paper_bgcolor=PLOT_TRANSPARENT,
    font=dict(family="DM Sans", color=LABEL_COLOR),
    xaxis=AXIS_BASE,
    yaxis=AXIS_BASE,
    legend=dict(
        font=dict(color=LEGEND_COLOR, size=12, family="DM Sans"),
        bgcolor="rgba(0,0,0,0)",
        bordercolor="rgba(0,0,0,0)",
    ),
    title_font=dict(color=TITLE_COLOR, size=13, family="DM Sans"),
    hoverlabel=dict(
        bgcolor=AZ_BLUE,
        font=dict(color="#E0F4F7", size=12, family="DM Mono"),
        bordercolor=AZ_TEAL,
    ),
)

def apply_layout(fig, **overrides):
    """Aplica LAYOUT_BASE + overrides a qualquer gráfico."""
    layout = {**LAYOUT_BASE, **overrides}
    for ax in ("xaxis", "yaxis"):
        if ax in overrides:
            layout[ax] = {**AXIS_BASE, **overrides[ax]}
    fig.update_layout(**layout)
    return fig

# ═══════════════════════════════════════════════════════════════════
# CSS GLOBAL — AzData Brand Identity
# Fontes: Syne 800 (títulos) · DM Sans 400/500 (corpo) · DM Mono (labels/código)
# ═══════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@400;500&display=swap');

  html, body, [class*="css"] {{
      font-family: 'DM Sans', sans-serif;
      background-color: {AZ_MIDNIGHT};
      color: #7ABFCC;
  }}
  .stApp {{ background-color: {AZ_MIDNIGHT}; }}
  section[data-testid="stSidebar"] {{
      background-color: #030A0F !important;
      border-right: 1px solid {AZ_BORDER};
  }}
  .block-container {{ padding-top: 1.5rem; }}

  /* ── HERO ── */
  .hero {{
      background: linear-gradient(135deg, {AZ_BLUE} 0%, #071824 55%, {AZ_MIDNIGHT} 100%);
      border: 1px solid {AZ_BORDER};
      border-top: 2px solid {AZ_TEAL};
      border-radius: 12px;
      padding: 2.8rem 3rem 2.4rem;
      margin-bottom: 2rem;
      position: relative;
      overflow: hidden;
  }}
  .hero::before {{
      content: '';
      position: absolute; inset: 0;
      background:
        radial-gradient(ellipse at 80% 50%, rgba(34,212,223,0.05) 0%, transparent 60%),
        repeating-linear-gradient(90deg, transparent, transparent 60px, rgba(14,154,167,0.03) 60px, rgba(14,154,167,0.03) 61px),
        repeating-linear-gradient(0deg,  transparent, transparent 60px, rgba(14,154,167,0.03) 60px, rgba(14,154,167,0.03) 61px);
  }}
  .hero::after {{
      content: '∧';
      position: absolute; right: 3.5rem; top: 50%;
      transform: translateY(-50%);
      font-family: 'Syne', sans-serif;
      font-size: 10rem; font-weight: 800;
      color: rgba(34,212,223,0.04);
      pointer-events: none; line-height: 1;
  }}
  .hero-pill {{
      display: inline-flex; align-items: center; gap: 6px;
      background: rgba(34,212,223,0.08);
      border: 1px solid rgba(34,212,223,0.25);
      color: {AZ_AQUA};
      border-radius: 4px; padding: 3px 12px;
      font-family: 'DM Mono', monospace;
      font-size: 0.65rem; font-weight: 500;
      letter-spacing: 2px; text-transform: uppercase;
      margin-bottom: 1rem;
  }}
  .hero h1 {{
      font-family: 'Syne', sans-serif;
      color: #E0F4F7; font-size: 2.5rem; font-weight: 800;
      margin: 0 0 0.5rem; letter-spacing: -0.04em;
      line-height: 1.1;
  }}
  .hero h1 span {{ color: {AZ_AQUA}; }}
  .hero p {{
      color: #3A7A8A; font-size: 0.92rem;
      margin: 0; font-weight: 400; letter-spacing: 0.2px;
  }}
  .hero-brand {{
      position: absolute; bottom: 1.5rem; right: 2rem;
      font-family: 'DM Mono', monospace;
      font-size: 0.62rem; color: rgba(34,212,223,0.25);
      letter-spacing: 2px; text-transform: uppercase;
  }}

  /* ── SECTION TITLES ── */
  .sec-title {{
      font-family: 'DM Mono', monospace;
      font-size: 0.65rem; color: {AZ_TEAL};
      letter-spacing: 3px; text-transform: uppercase;
      margin: 2.5rem 0 1.2rem;
      padding-bottom: 0.7rem;
      border-bottom: 1px solid {AZ_BORDER};
      display: flex; align-items: center; gap: 0.7rem;
  }}
  .sec-title::before {{
      content: '';
      display: inline-block; width: 20px; height: 2px;
      background: linear-gradient(90deg, {AZ_AQUA}, {AZ_TEAL});
      border-radius: 2px; flex-shrink: 0;
  }}

  /* ── KPI CARDS ── */
  .kpi {{
      background: {AZ_MID_CARD};
      border: 1px solid {AZ_BORDER};
      border-radius: 10px;
      padding: 1.4rem 1.5rem;
      position: relative; overflow: hidden; height: 100%;
      transition: border-color 0.2s;
  }}
  .kpi::before {{
      content: '';
      position: absolute; top: 0; left: 0; right: 0;
      height: 2px; background: {AZ_BORDER};
  }}
  .kpi.aq::before {{ background: linear-gradient(90deg, {AZ_AQUA}, {AZ_TEAL}); }}
  .kpi.tl::before {{ background: {AZ_TEAL}; }}
  .kpi.gr::before {{ background: {AZ_GREEN}; }}
  .kpi.lv::before {{ background: {AZ_LAVA}; }}
  .kpi-lbl {{
      font-family: 'DM Mono', monospace;
      font-size: 0.6rem; font-weight: 500;
      letter-spacing: 2px; text-transform: uppercase;
      color: #2A5A6A; margin-bottom: 0.5rem;
  }}
  .kpi-val {{
      font-family: 'Syne', sans-serif;
      font-size: 2.5rem; font-weight: 800;
      color: #C0E8EE; line-height: 1;
      letter-spacing: -0.04em;
  }}
  .kpi-val.aq {{ color: {AZ_AQUA}; }}
  .kpi-val.tl {{ color: {AZ_TEAL}; }}
  .kpi-val.gr {{ color: {AZ_GREEN}; }}
  .kpi-val.lv {{ color: {AZ_LAVA}; }}
  .kpi-sub {{ font-size: 0.78rem; color: #2A5A6A; margin-top: 0.4rem; font-family: 'DM Sans', sans-serif; }}
  .dlt-up {{ color: {AZ_GREEN}; font-weight: 600; }}
  .dlt-dn {{ color: {AZ_LAVA}; font-weight: 600; }}

  /* ── INSIGHT BOXES ── */
  .ibox {{
      background: {AZ_MID_CARD};
      border: 1px solid {AZ_BORDER};
      border-left: 3px solid {AZ_TEAL};
      border-radius: 0 10px 10px 0;
      padding: 1.3rem 1.7rem; margin: 1.1rem 0;
  }}
  .ibox h4 {{
      font-family: 'DM Mono', monospace;
      color: {AZ_AQUA}; margin: 0 0 0.55rem;
      font-size: 0.68rem; letter-spacing: 2px; text-transform: uppercase;
  }}
  .ibox p {{ margin: 0; font-size: 0.87rem; line-height: 1.7; color: #3A6A7A; }}
  .ibox p b {{ color: #7ABFCC; }}

  /* ── FOOTER ── */
  .fnote {{
      background: #030A0F;
      border: 1px solid {AZ_BORDER};
      border-top: 1px solid rgba(34,212,223,0.12);
      border-radius: 8px; padding: 1.1rem 1.5rem;
      font-family: 'DM Mono', monospace;
      font-size: 0.65rem; color: #1A4A5A;
      margin-top: 1.5rem; letter-spacing: 0.3px;
      display: flex; justify-content: space-between; align-items: center;
      flex-wrap: wrap; gap: 0.5rem;
  }}
  .fnote b {{ color: #2A6A7A; }}
  .fnote-brand {{
      color: {AZ_TEAL}; font-weight: 500; letter-spacing: 1px;
  }}

  /* ── SIDEBAR ── */
  .stSidebar [data-testid="stMarkdownContainer"] p,
  .stSidebar label, .stSidebar .stSelectbox div {{
      color: #2A5A6A !important;
      font-family: 'DM Sans', sans-serif !important;
  }}
  .stSidebar h3 {{ color: {AZ_TEAL} !important; font-family: 'Syne', sans-serif !important; }}
  .stSidebar .stCaption {{ color: #1A3A4A !important; }}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# CONSTANTES DE DADOS
# ═══════════════════════════════════════════════════════════════════

BASE_PATH = os.path.dirname(__file__)

MESES_PT  = {6:"Jun", 7:"Jul", 8:"Ago", 9:"Set"}
MES_ORD   = {"Jun":6, "Jul":7, "Ago":8, "Set":9}
TIPO_MAP  = {"InterIlhas":"Inter-Ilhas", "Territoriais":"Territoriais", "Internacionais":"Internacionais"}

# ═══════════════════════════════════════════════════════════════════
# CARREGAMENTO DE DADOS
# ═══════════════════════════════════════════════════════════════════
@st.cache_data
def load_data():
    df_v = pd.read_csv(os.path.join(BASE_PATH, "numero_voos.csv"))
    df_a = pd.read_csv(os.path.join(BASE_PATH, "detalhe_voos_2026.csv"))
    df_v["MesNome"]   = df_v["Mes"].map(MESES_PT)
    df_v["TipoLabel"] = df_v["TipoVoo"].map(TIPO_MAP)
    df_a["date"]      = pd.to_datetime(df_a["date"])
    df_a["Mes"]       = df_a["date"].dt.month
    df_a["MesNome"]   = df_a["Mes"].map(MESES_PT)
    df_a["TipoLabel"] = df_a["TipoVoo"].map(TIPO_MAP)
    df_a["dist_km"]   = (
        df_a["direct_distance_km"]
        .str.replace(" km", "", regex=False)
        .str.replace(",", "")
        .astype(float)
    )
    return df_v, df_a

df_voos, df_arr = load_data()

# ═══════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### ∧ Filtros de Análise")
    mes_sel  = st.multiselect("Mês", ["Jun","Jul","Ago","Set"], default=["Jun","Jul","Ago","Set"])
    tipo_sel = st.multiselect("Categoria", list(TIPO_MAP.values()), default=list(TIPO_MAP.values()))
    comp_sel = st.multiselect("Companhia (2026)", sorted(df_arr["airline"].unique().tolist()), default=sorted(df_arr["airline"].unique().tolist()))
    
    st.markdown("---")
    st.markdown("**Aeroporto de Ponta Delgada (PDL)**  \nVerão 2025 vs 2026")
    st.caption("AzData Solutions · azdata.pt")

# ═══════════════════════════════════════════════════════════════════
# FILTROS
# ═══════════════════════════════════════════════════════════════════
def fv(df):
    d = df.copy()
    if mes_sel:  # se lista não está vazia
        d = d[d["MesNome"].isin(mes_sel)]
    if tipo_sel:
        d = d[d["TipoLabel"].isin(tipo_sel)]
    return d

def fa(df):
    d = df.copy()
    if mes_sel:
        d = d[d["MesNome"].isin(mes_sel)]
    if tipo_sel:
        d = d[d["TipoLabel"].isin(tipo_sel)]
    if comp_sel:
        d = d[d["airline"].isin(comp_sel)]
    return d

dfv = fv(df_voos)
dfa = fa(df_arr)

# ═══════════════════════════════════════════════════════════════════
# KPIs
# ═══════════════════════════════════════════════════════════════════
t25 = dfv[dfv["Ano"]==2025]["NumerodeVoos"].sum()
t26 = dfv[dfv["Ano"]==2026]["NumerodeVoos"].sum()
dt  = ((t26-t25)/t25*100) if t25 else 0
i25 = dfv[(dfv["Ano"]==2025)&(dfv["TipoVoo"]=="Internacionais")]["NumerodeVoos"].sum()
i26 = dfv[(dfv["Ano"]==2026)&(dfv["TipoVoo"]=="Internacionais")]["NumerodeVoos"].sum()
di  = ((i26-i25)/i25*100) if i25 else 0
seats_tot = dfa["seats_per_flight"].sum()
avg_s     = dfa["seats_per_flight"].mean() if len(dfa) else 0
n_air     = dfa["airline"].nunique()
n_rts     = dfa["iata"].nunique()

# ═══════════════════════════════════════════════════════════════════
# HERO
# ═══════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
  <div class="hero-pill">∧ AzData Solutions · PDL · Açores</div>
  <h1>Análise de Voos —<br><span>Verão 2025 &amp; 2026</span></h1>
  <p>Estudo comparativo da evolução do tráfego aéreo · Junho a Setembro · Aeroporto de Ponta Delgada</p>
  <div class="hero-brand">azdata.pt · data engineering · analytics</div>
</div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# SEC 1 — KPIs
# ═══════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-title">01 · indicadores‑chave de desempenho</div>', unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
dc, da = ("dlt-up","▲") if dt>=0 else ("dlt-dn","▼")
ic, ia = ("dlt-up","▲") if di>=0 else ("dlt-dn","▼")
with k1:
    st.markdown(f'<div class="kpi aq"><div class="kpi-lbl">Total Voos 2026</div><div class="kpi-val aq">{t26:,}</div><div class="kpi-sub"><span class="{dc}">{da} {abs(dt):.1f}% vs 2025</span></div></div>', unsafe_allow_html=True)
with k2:
    st.markdown(f'<div class="kpi tl"><div class="kpi-lbl">Internacionais 2026</div><div class="kpi-val tl">{i26:,}</div><div class="kpi-sub"><span class="{ic}">{ia} {abs(di):.1f}% vs 2025</span></div></div>', unsafe_allow_html=True)
with k3:
    st.markdown(f'<div class="kpi gr"><div class="kpi-lbl">Companhias Aéreas</div><div class="kpi-val gr">{n_air}</div><div class="kpi-sub">{n_rts} origens distintas</div></div>', unsafe_allow_html=True)
with k4:
    st.markdown(f'<div class="kpi lv"><div class="kpi-lbl">Capacidade Total</div><div class="kpi-val lv">{seats_tot:,}</div><div class="kpi-sub">Média {avg_s:.0f} lugares/voo</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# SEC 2 — EVOLUÇÃO MENSAL
# ═══════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-title">02 · evolução mensal — 2025 vs 2026</div>', unsafe_allow_html=True)

pivot = (
    dfv.groupby(["Ano","MesNome"])["NumerodeVoos"].sum().reset_index()
    .assign(MesOrd=lambda d: d["MesNome"].map(MES_ORD))
    .sort_values("MesOrd")
)

fig_line = go.Figure()
for ano, cor, dash, w in [(2025, COR_2025, "dash", 2), (2026, COR_2026, "solid", 3)]:
    d = pivot[pivot["Ano"]==ano]
    fig_line.add_trace(go.Scatter(
        x=d["MesNome"], y=d["NumerodeVoos"], name=str(ano),
        mode="lines+markers",
        line=dict(color=cor, width=w, dash=dash),
        marker=dict(size=8, color=cor, line=dict(width=2, color=AZ_MIDNIGHT)),
        hovertemplate=f"<b>%{{x}} {ano}</b><br>%{{y:,}} voos<extra></extra>",
    ))
apply_layout(fig_line,
    height=340,
    legend=dict(orientation="h", y=1.12, x=0,
                font=dict(color=LEGEND_COLOR, size=12, family="DM Sans"),
                bgcolor="rgba(0,0,0,0)"),
    yaxis={"title": "Nº de Voos"},
    margin=dict(l=0, r=0, t=35, b=0),
)
st.plotly_chart(fig_line, width='stretch')

# Variação %
pv25 = pivot[pivot["Ano"]==2025].set_index("MesNome")["NumerodeVoos"]
pv26 = pivot[pivot["Ano"]==2026].set_index("MesNome")["NumerodeVoos"]
vm   = ((pv26-pv25)/pv25*100).reset_index()
vm.columns = ["MesNome","Var"]
vm = vm.assign(MesOrd=lambda d: d["MesNome"].map(MES_ORD)).sort_values("MesOrd")
vm["Cor"] = vm["Var"].apply(lambda x: AZ_GREEN if x>=0 else AZ_LAVA)

fig_var = go.Figure(go.Bar(
    x=vm["MesNome"], y=vm["Var"],
    marker_color=vm["Cor"],
    text=vm["Var"].apply(lambda x: f"{x:+.1f}%"),
    textposition="outside",
    textfont=dict(color=LABEL_COLOR, size=11, family="DM Mono"),
    hovertemplate="<b>%{x}</b><br>%{y:+.1f}%<extra></extra>",
))
apply_layout(fig_var,
    height=400, showlegend=False,
    title=dict(text="Variação % por Mês (2026 vs 2025)", font=dict(size=13, color=TITLE_COLOR, family="DM Sans")),
    yaxis={"ticksuffix": "%"},
    margin=dict(l=0, r=0, t=30, b=0),
)
st.plotly_chart(fig_var, width='stretch')

# ═══════════════════════════════════════════════════════════════════
# SEC 3 — CATEGORIA
# ═══════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-title">03 · comparação por categoria de voo</div>', unsafe_allow_html=True)
cl, cr = st.columns(2)

with cl:
    dfg = dfv.groupby(["Ano","TipoLabel"])["NumerodeVoos"].sum().reset_index()
    fig_stk = go.Figure()
    for tipo in ["Inter-Ilhas","Territoriais","Internacionais"]:
        d = dfg[dfg["TipoLabel"]==tipo]
        fig_stk.add_trace(go.Bar(
            name=tipo, x=d["Ano"].astype(str), y=d["NumerodeVoos"],
            marker_color=CORES_TIPO[tipo],
            text=d["NumerodeVoos"], textposition="inside",
            insidetextanchor="middle",
            textfont=dict(color=AZ_MIDNIGHT, size=11, family="DM Mono"),
            hovertemplate=f"<b>{tipo}</b><br>%{{x}}: %{{y:,}}<extra></extra>",
        ))
    apply_layout(fig_stk,
        barmode="stack", height=380,
        title=dict(text="Total por Categoria", font=dict(size=13, color=TITLE_COLOR, family="DM Sans")),
        legend=dict(orientation="h", y=1.08, x=0,
                    font=dict(color=LEGEND_COLOR, size=11, family="DM Sans"),
                    bgcolor="rgba(0,0,0,0)"),
        xaxis={"tickfont": dict(size=13, color=TICK_COLOR)},
        margin=dict(l=0, r=0, t=55, b=0),
    )
    st.plotly_chart(fig_stk, width='stretch')

with cr:
    ph = (
        dfv.groupby(["Ano","MesNome","TipoLabel"])["NumerodeVoos"].sum().reset_index()
        .assign(MesOrd=lambda d: d["MesNome"].map(MES_ORD))
        .sort_values("MesOrd")
    )
    fig_heat = make_subplots(rows=1, cols=2, subplot_titles=["2025","2026"], shared_yaxes=True)
    for i, ano in enumerate([2025,2026]):
        d  = ph[ph["Ano"]==ano]
        pt = d.pivot(index="TipoLabel", columns="MesNome", values="NumerodeVoos")
        pt = pt[[m for m in ["Jun","Jul","Ago","Set"] if m in pt.columns]]
        fig_heat.add_trace(go.Heatmap(
            z=pt.values, x=pt.columns.tolist(), y=pt.index.tolist(),
            colorscale=[[0, AZ_BLUE],[0.5, AZ_TEAL],[1, AZ_AQUA]],
            showscale=(i==1),
            text=pt.values, texttemplate="%{text}",
            textfont=dict(color=AZ_MIDNIGHT, size=11, family="DM Mono"),
            hovertemplate="<b>%{y}</b> – %{x}<br>%{z:,}<extra></extra>",
        ), row=1, col=i+1)

    fig_heat.update_layout(
        **{k: v for k, v in LAYOUT_BASE.items() if k not in ("xaxis","yaxis","margin")},
        height=380,
        title=dict(text="Heatmap: Voos Mês × Categoria", font=dict(size=13, color=TITLE_COLOR, family="DM Sans")),
        margin=dict(l=0, r=0, t=65, b=0),
    )
    fig_heat.update_xaxes(**{k:v for k,v in AXIS_BASE.items() if k != "title_font"})
    fig_heat.update_yaxes(**{k:v for k,v in AXIS_BASE.items() if k != "title_font"})
    for ann in fig_heat.layout.annotations:
        ann.font = dict(color=LABEL_COLOR, size=12, family="DM Sans")
    st.plotly_chart(fig_heat, width='stretch')

# ═══════════════════════════════════════════════════════════════════
# SEC 4 — INTERNACIONAIS
# ═══════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-title">04 · voos internacionais 2026 — origens &amp; companhias</div>', unsafe_allow_html=True)
df_int = dfa[dfa["TipoVoo"]=="Internacionais"].copy()
ca, cb = st.columns(2)

with ca:
    top_ori = (
        df_int.groupby(["iata","origin"]).agg(n_voos=("flight","count"))
        .reset_index().sort_values("n_voos", ascending=False).head(15)
    )
    top_ori["label"] = top_ori["origin"].str.extract(r"^([^(]+)").iloc[:,0].str.strip()

    fig_ori = go.Figure(go.Bar(
        y=top_ori["label"][::-1], x=top_ori["n_voos"][::-1],
        orientation="h",
        marker=dict(
            color=top_ori["n_voos"][::-1],
            colorscale=[[0, AZ_BLUE],[1, AZ_AQUA]],
        ),
        text=top_ori["n_voos"][::-1], textposition="outside",
        textfont=dict(color=LABEL_COLOR, size=11, family="DM Mono"),
        hovertemplate="<b>%{y}</b><br>%{x} voos<extra></extra>",
    ))
    apply_layout(fig_ori,
        height=420,
        title=dict(text="Top Origens Internacionais", font=dict(size=13, color=TITLE_COLOR, family="DM Sans")),
        yaxis={"tickfont": dict(size=10, color=TICK_COLOR)},
        margin=dict(l=0, r=60, t=50, b=0),
    )
    st.plotly_chart(fig_ori, width='stretch')

with cb:
    comp = (
        df_int.groupby("airline").agg(n_voos=("flight","count"))
        .reset_index().sort_values("n_voos", ascending=False)
    )
    # Paleta derivada da brand guide
    pie_colors = [AZ_AQUA, AZ_TEAL, AZ_GREEN, AZ_LAVA, AZ_BLUE,
                  "#17B8C4","#25A87A","#C44A25","#0A3D54","#1AAAB6",
                  "#22C47A","#D45030","#094460","#18C0CA","#20B870"]

    fig_comp = go.Figure(go.Pie(
        labels=comp["airline"], values=comp["n_voos"], hole=0.58,
        marker=dict(colors=pie_colors[:len(comp)],
                    line=dict(color=AZ_MIDNIGHT, width=2)),
        textinfo="label+percent",
        textfont=dict(size=10, color=LABEL_COLOR, family="DM Sans"),
        hovertemplate="<b>%{label}</b><br>%{value} voos (%{percent})<extra></extra>",
    ))
    fig_comp.add_annotation(
        text=f"<b>{comp['n_voos'].sum():,}</b><br>voos",
        x=0.5, y=0.5, showarrow=False, align="center",
        font=dict(size=16, color=AZ_AQUA, family="Syne"),
    )
    apply_layout(fig_comp,
        height=420,
        title=dict(text="Quota de Mercado por Companhia", font=dict(size=13, color=TITLE_COLOR, family="DM Sans")),
        legend=dict(orientation="v", x=1.02, y=0.5,
                    font=dict(color=LEGEND_COLOR, size=10, family="DM Sans"),
                    bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=0, r=0, t=50, b=0),
    )
    st.plotly_chart(fig_comp, width='stretch')

# ═══════════════════════════════════════════════════════════════════
# SEC 5 — CAPACIDADE
# ═══════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-title">05 · capacidade de lugares disponíveis — 2026</div>', unsafe_allow_html=True)

cap = (
    dfa.groupby(["MesNome","TipoLabel"])["seats_per_flight"].sum().reset_index()
    .assign(MesOrd=lambda d: d["MesNome"].map(MES_ORD))
    .sort_values("MesOrd")
)
fig_cap = go.Figure()
for tipo in ["Inter-Ilhas","Territoriais","Internacionais"]:
    d = cap[cap["TipoLabel"]==tipo]
    fig_cap.add_trace(go.Bar(
        name=tipo, x=d["MesNome"], y=d["seats_per_flight"],
        marker_color=CORES_TIPO[tipo],
        text=d["seats_per_flight"].apply(lambda x: f"{x:,}"),
        textposition="inside", insidetextanchor="middle",
        textfont=dict(color=AZ_MIDNIGHT, size=10, family="DM Mono"),
        hovertemplate=f"<b>{tipo}</b> – %{{x}}<br>%{{y:,}} lugares<extra></extra>",
    ))
apply_layout(fig_cap,
    barmode="stack", height=350,
    title=dict(text="Lugares Disponíveis por Mês e Categoria (2026)", font=dict(size=13, color=TITLE_COLOR, family="DM Sans")),
    legend=dict(orientation="h", y=1.08, x=0,
                font=dict(color=LEGEND_COLOR, size=12, family="DM Sans"),
                bgcolor="rgba(0,0,0,0)"),
    yaxis={"title": "Nº de Lugares"},
    xaxis={"tickfont": dict(size=13, color=TICK_COLOR)},
    margin=dict(l=0, r=0, t=55, b=0),
)
st.plotly_chart(fig_cap, width='stretch')


# ═══════════════════════════════════════════════════════════════════
# SEC 6 — CONCLUSÕES
# ═══════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-title">06 · análise &amp; conclusões</div>', unsafe_allow_html=True)

pico  = pivot[pivot["Ano"]==2026].sort_values("NumerodeVoos", ascending=False).iloc[0]
top_a = (dfa.groupby("airline")["flight"].count()
         .reset_index().sort_values("flight", ascending=False).iloc[0])

st.markdown(f"""
<div class="ibox">
  <h4>📈 Tendência Geral do Tráfego</h4>
  <p>O aeroporto de Ponta Delgada registou um <b>{'crescimento' if dt>0 else 'redução'} de {abs(dt):.1f}%</b>
  no total de movimentos aéreos no verão de 2026 face a 2025, passando de <b>{t25:,}</b> para
  <b>{t26:,} voos</b> entre Junho e Setembro..</p>
</div>
<div class="ibox">
  <h4>🌍 Conectividade Internacional</h4>
  <p>Os voos internacionais registaram uma variação de
  <b>{'crescimento' if di>0 else 'redução'} de {abs(di):.1f}%</b>,
  com <b>{i26:,} operações em 2026</b> versus <b>{i25:,} em 2025</b>.
  A diversidade de <b>{n_air} companhias</b> e <b>{n_rts} origens distintas</b> evidencia a atratividade
  do destino — com destaque para rotas diretas das Américas do Norte (Nova Iorque, Boston,
  Toronto e Montreal).</p>
</div>
<div class="ibox">
  <h4>📅 Pico de Tráfego e Sazonalidade</h4>
  <p>O mês de maior movimento em 2026 é <b>{pico['MesNome']}</b> com
  <b>{int(pico['NumerodeVoos']):,} voos</b>, confirmando o padrão de concentração estival dos
  destinos insulares. A categoria <b>Inter-Ilhas</b> mantém o maior peso absoluto, enquanto os
  voos <b>Territoriais</b> constituem a espinha dorsal da ligação ao continente português.</p>
</div>
<div class="ibox">
  <h4>✈️ Operadores &amp; Capacidade</h4>
  <p>A <b>{top_a['airline']}</b> lidera com <b>{top_a['flight']:,} voos</b>.
  Com uma capacidade total de <b>{seats_tot:,} lugares</b> e média de <b>{avg_s:.0f} lugares/voo</b>,
  as rotas de longa distância utilizam aeronaves de maior porte (180+ lugares), enquanto as rotas
  inter-ilhas operam com aeronaves de 37–79 lugares.</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# SEC 8 — TABELA
# ═══════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-title">08 · tabela resumo comparativa</div>', unsafe_allow_html=True)

res   = dfv.groupby(["Ano","TipoLabel"])["NumerodeVoos"].sum().reset_index()
res_p = res.pivot(index="TipoLabel", columns="Ano", values="NumerodeVoos").reset_index()
res_p.columns.name = None
res_p["Var (%)"] = ((res_p[2026]-res_p[2025])/res_p[2025]*100).round(1)
res_p.columns    = ["Categoria","Voos 2025","Voos 2026","Var (%)"]
tot = pd.DataFrame({
    "Categoria":["TOTAL"],
    "Voos 2025":[res_p["Voos 2025"].sum()],
    "Voos 2026":[res_p["Voos 2026"].sum()],
    "Var (%)"  :[round((res_p["Voos 2026"].sum()-res_p["Voos 2025"].sum())/res_p["Voos 2025"].sum()*100,1)],
})
tab = pd.concat([res_p, tot], ignore_index=True)


def cor_v(v):
    try:
        f = float(v)
        if f > 0: return f"color:{AZ_GREEN}; font-weight:700"
        if f < 0: return f"color:{AZ_LAVA}; font-weight:700"
    except: pass
    return ""

#st.dataframe(tab.style.map(cor_v, subset=["Var (%)"]), width='stretch', hide_index=True)
st.dataframe(
    tab.style
       .map(cor_v, subset=["Var (%)"])
       .format({"Var (%)": "{:+.2f}%"})  # <- formata apenas visualmente
       , width='stretch', hide_index=True
)

# ═══════════════════════════════════════════════════════════════════
# RODAPÉ
# ═══════════════════════════════════════════════════════════════════
st.markdown("""
<div class="fnote">
  <span>
    <b>📌 Fontes:</b> Dados 2025 — SREA (Serviço Regional de Estatística dos Açores)
    &nbsp;·&nbsp; Dados 2026 — flight.info
    &nbsp;·&nbsp; Jun–Set (verão IATA)
  </span>
  <span class="fnote-brand">∧ AzData Solutions · azdata.pt</span>
</div>
""", unsafe_allow_html=True)