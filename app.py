import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(page_title="Churn Risk Intelligence", page_icon="📉", layout="wide")

# =========================
# ESTILO VISUAL PREMIUM (DARK RED)
# =========================
st.markdown(
    """
<style>
.stApp {
    background: radial-gradient(circle at top, #14070b 0%, #070203 70%);
    color: #e5e7eb;
    overflow: hidden;
}

section.main > div {
    padding-top: 0.6rem;
    padding-bottom: 0.6rem;
}

div[data-testid="metric-container"] {
    background: linear-gradient(145deg, #14070b, #0b0306);
    border-radius: 14px;
    padding: 16px;
    border-left: 4px solid #b11226;
    box-shadow: 0 8px 30px rgba(0,0,0,0.7);
}

.stMainBlockContainer {
        padding: 50px 20px;
    }

h1 {
    font-size: 2.3rem;
}
h2, h3 {
    font-weight: 600;
}
p, span {
    color: #cbd5e1;
}
</style>
""",
    unsafe_allow_html=True,
)

# =========================
# CONFIGURAÇÃO PLOTLY
# =========================
px.defaults.template = "plotly_dark"
px.defaults.color_discrete_sequence = ["#ef4444", "#b11226", "#7f1d1d", "#991b1b"]


def ajustar_layout(fig, altura=290):
    fig.update_layout(
        height=altura,
        margin=dict(t=55, b=25, l=10, r=10),
        legend_title_text="Status do Cliente",
    )
    return fig


# =========================
# CARREGAMENTO DOS DADOS
# =========================
@st.cache_data
def load_data():
    return pd.read_csv("data/bank_churn_data.csv")


df = load_data()

# =========================
# HEADER
# =========================
st.markdown("## 📊 **Churn Risk Intelligence**")
st.markdown(
    "Painel executivo para **análise de risco de churn**, comportamento do cliente e impacto financeiro."
)

# =========================
# KPIs PRINCIPAIS
# =========================
total = len(df)
churned = df[df["Churn Flag"] == 1].shape[0]
active = total - churned
churn_rate = churned / total * 100

avg_balance = df["Balance"].mean()
avg_complaints = df["NumComplaints"].mean()

k1, k2, k3, k4, k5, k6 = st.columns(6)

k1.metric("👥 Clientes Totais", f"{total:,}")
k2.metric("✅ Clientes Ativos", f"{active:,}")
k3.metric("❌ Clientes Cancelados", f"{churned:,}")
k4.metric("📉 Taxa de Churn", f"{churn_rate:.2f}%")
k5.metric("💰 Saldo Médio", f"${avg_balance:,.0f}")
k6.metric("⚠️ Reclamações Médias", f"{avg_complaints:.2f}")

st.caption(
    "🔎 **Leitura executiva:** churn elevado combinado com alto saldo médio indica risco financeiro relevante."
)

# =========================
# VISÃO GERAL DE STATUS
# =========================
c1, c2, c3 = st.columns(3)

with c1:
    df_legenda = df.copy()
    df_legenda["Status do Cliente"] = df_legenda["Churn Flag"].map(
        {0: "Ativo (Adimplente)", 1: "Cancelado (Inadimplente)"}
    )

    fig = px.pie(
        df_legenda,
        names="Status do Cliente",
        hole=0.65,
        title="Status Geral da Base de Clientes",
    )
    fig = ajustar_layout(fig, altura=300)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "📘 **Legenda:** 0 = clientes ativos (adimplentes) | 1 = clientes cancelados (inadimplentes)."
    )

with c2:
    fig = px.box(
        df,
        x="Churn Flag",
        y="Customer Tenure",
        title="Tempo de Relacionamento vs Churn",
    )
    fig = ajustar_layout(fig)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Clientes com menor tempo de relacionamento apresentam maior propensão ao churn."
    )

with c3:
    fig = px.box(
        df, x="Churn Flag", y="Balance", title="Exposição Financeira por Churn"
    )
    fig = ajustar_layout(fig)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Cancelamentos com alto saldo representam maior impacto financeiro direto."
    )

# =========================
# COMPORTAMENTO E EXPERIÊNCIA
# =========================
c4, c5, c6 = st.columns(3)

with c4:
    fig = px.histogram(
        df,
        x="NumOfProducts",
        color="Churn Flag",
        barmode="group",
        title="Quantidade de Produtos por Cliente",
    )
    fig = ajustar_layout(fig, altura=270)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Clientes com poucos produtos tendem a cancelar com mais facilidade.")

with c5:
    fig = px.box(
        df, x="Churn Flag", y="NumComplaints", title="Reclamações vs Cancelamento"
    )
    fig = ajustar_layout(fig, altura=270)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Reclamações são um forte indicador antecipado de churn.")

with c6:
    fig = px.histogram(
        df,
        x="Customer Segment",
        color="Churn Flag",
        barmode="group",
        title="Risco de Churn por Segmento",
    )
    fig = ajustar_layout(fig, altura=270)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Segmentos específicos concentram maior risco de evasão.")

# =========================
# RANKING DE RISCO
# =========================
st.markdown("### 🚨 Clientes com Maior Risco de Churn")

risk_df = df.copy()
risk_df["Score de Risco"] = (
    risk_df["NumComplaints"] * 2
    + (risk_df["Balance"] / risk_df["Balance"].max()) * 3
    + (1 / (risk_df["Customer Tenure"] + 1)) * 4
)

top_risk = risk_df.sort_values("Score de Risco", ascending=False).head(10)

st.dataframe(
    top_risk[
        ["Surname", "Customer Segment", "Balance", "NumComplaints", "Score de Risco"]
    ],
    use_container_width=True,
    height=260,
)

st.caption(
    "🔴 Ranking priorizado para ações imediatas de retenção e mitigação de perdas."
)

# =========================
# IMPACTO FINANCEIRO
# =========================
estimated_loss = churned * avg_balance

st.markdown("### 💸 Impacto Financeiro Estimado do Churn")

st.metric(
    "Perda Financeira Potencial",
    f"${estimated_loss:,.0f}",
    help="Estimativa baseada no saldo médio dos clientes que cancelaram.",
)

st.caption(
    "📌 **Conclusão executiva:** reduzir churn em poucos pontos percentuais podem gerar economia significativa."
)
