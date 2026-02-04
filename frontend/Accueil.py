"""
Dashboard Superstore BI - Page d'Accueil
🏠 Sélectionnez votre profil dans le menu latéral
"""

import streamlit as st
import requests
import os

# === CONFIGURATION PAGE ===
st.set_page_config(
    page_title="Superstore BI Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === STYLES CSS ===
st.markdown("""
<style>
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .stMetric {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
    
    h1 { color: #2c3e50; font-weight: 700; }
    h2 { color: #34495e; font-weight: 600; margin-top: 0.5rem; margin-bottom: 0.5rem; }
    h3 { color: #5a6c7d; font-weight: 500; margin-top: 0.3rem; margin-bottom: 0.3rem; }
    
    .quadrant-box {
        padding: 10px;
        border-radius: 8px;
        margin: 5px;
        text-align: center;
    }
    
    .quadrant-q1 { background-color: #d4edda; border: 2px solid #28a745; }
    .quadrant-q2 { background-color: #fff3cd; border: 2px solid #ffc107; }
    .quadrant-q3 { background-color: #cce5ff; border: 2px solid #007bff; }
    .quadrant-q4 { background-color: #f8d7da; border: 2px solid #dc3545; }
            
    .info-card {
        background-color: #e8eef3;
        padding: 18px;
        border-radius: 10px;
        color: #2c3e50;
        border-left: 6px solid #5a7a92;
        line-height: 1.6;
        margin-bottom: 1rem;
    }

    .info-title {
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 8px;
        color: #3d5a6d;
    }
</style>
""", unsafe_allow_html=True)

# === CONFIGURATION API ===
API_URL = os.getenv("API_URL", "http://localhost:8000")

@st.cache_data(ttl=300)
def appeler_api(endpoint: str, params: dict = None):
    """Appelle l'API et retourne les données"""
    try:
        url = f"{API_URL}{endpoint}"
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except:
        return None
    
def formater_euro(valeur: float) -> str:
    return f"{valeur:,.2f} €".replace(",", " ").replace(".", ",")

def formater_nombre(valeur: int) -> str:
    return f"{valeur:,}".replace(",", " ")

def formater_pourcentage(valeur: float) -> str:
    return f"{valeur:.2f}%"

# === VÉRIFICATION CONNEXION API ===
info_api = appeler_api("/")

# === HEADER ===
st.title("🛒 Superstore BI Dashboard")
st.markdown("### Bienvenue sur votre plateforme d'analyse Business Intelligence")

if info_api:
    st.success(f"✅ API connectée | Dataset : {info_api['nb_lignes']} lignes | Version : {info_api['version']}")
else:
    st.warning(f"⚠️ API non accessible sur {API_URL}")

st.divider()

# === SECTION KPI GLOBAUX ===
st.header("📊 Indicateurs Clés de Performance")

kpi_data = appeler_api("/kpi/globaux")

# Niveau 1 : Performance Financière (KPI's Critiques)
st.subheader("💰 Performance Financière")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("💰 CA Total", formater_euro(kpi_data['ca_total']))
with col2:
    st.metric("💵 Profit Total", formater_euro(kpi_data['profit_total']))
with col3:
    st.metric("📈 Marge Moyenne", formater_pourcentage(kpi_data['marge_moyenne']))
with col4:
    st.metric("💎 Marge Brute/Cmd", formater_euro(kpi_data['marge_brute_par_commande']))

# Niveau 2 : Volume d'Activité (KPI's Opérationnels)
st.subheader("📊 Volume d'Activité")
col4, col5, col6 = st.columns(3)
with col4:
    st.metric("🧾 Commandes", formater_nombre(kpi_data['nb_commandes']))
with col5:
    st.metric("📦 Quantité Vendue", formater_nombre(kpi_data['quantite_vendue']))
with col6:
    st.metric("👥 Clients Uniques", formater_nombre(kpi_data['nb_clients']))

# Niveau 3 : Indicateurs d'Efficacité (Ratios)
st.subheader("💎 Indicateurs d'Efficacité")
col7, col8, col9 = st.columns(3)
with col7:
    st.metric("🛒 Panier Moyen", formater_euro(kpi_data['panier_moyen']))
with col8:
    articles_cmd = kpi_data['quantite_vendue'] / kpi_data['nb_commandes'] if kpi_data['nb_commandes'] > 0 else 0
    st.metric("📊 Articles/Commande", f"{articles_cmd:.2f}")
with col9:
    ca_par_client = kpi_data['ca_total'] / kpi_data['nb_clients'] if kpi_data['nb_clients'] > 0 else 0
    st.metric("💎 CA/Client", formater_euro(ca_par_client))

st.markdown(
    """
    <div class="info-card">
        <div class="info-title">Data Storytelling</div>
        <p>L'entreprise affiche une santé financière solide avec un chiffre d'affaires de 
        <b>2,3 millions d'euros</b> généré par <b>5 009 commandes</b> auprès de 
        <b>793 clients</b>, représentant <b>37 873 articles vendus</b>.</p>
        <p>La <b>marge moyenne de 12,47%</b> et un <b>profit total de 286 397€</b> démontrent 
        une gestion efficace des coûts. Le <b>panier moyen de 458,61€</b> confirme une 
        clientèle <b>B2B</b> plutôt que grand public, tandis que la moyenne de 7,56 articles 
        par commande indique des achats groupés significatifs, typiques d'entreprises s'équipant 
        en fournitures ou matériel.</p>
    </div>
    """,
    unsafe_allow_html=True
)
st.divider()

# === FOOTER ===
st.markdown("""
<div style='text-align: center; color: #7f8c8d; margin-top: 40px;'>
    <p>📊 <b>Superstore BI Dashboard</b> | FastAPI + Streamlit + Plotly</p>
    <p style='font-size: 0.9em;'>Développé pour l'analyse avancée de données e-commerce</p>
</div>
""", unsafe_allow_html=True)
