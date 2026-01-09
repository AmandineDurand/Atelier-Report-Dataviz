"""
Dashboard Streamlit Avancé pour l'analyse Superstore
🎯 Version professionnelle - Analyses BI avancées
📊 BCG Matrix, Waterfall, Saisonnalité, Heatmaps
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# === CONFIGURATION PAGE ===
st.set_page_config(
    page_title="Superstore BI Dashboard - Advanced",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === STYLES CSS PERSONNALISÉS ===
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
    h2 { color: #34495e; font-weight: 600; }
    h3 { color: #5a6c7d; font-weight: 500; }
    
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
</style>
""", unsafe_allow_html=True)

# === CONFIGURATION API ===
API_URL = os.getenv("API_URL", "http://localhost:8000")

# === FONCTIONS HELPERS ===

@st.cache_data(ttl=300)
def appeler_api(endpoint: str, params: dict = None):
    """Appelle l'API et retourne les données"""
    try:
        url = f"{API_URL}{endpoint}"
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ **Impossible de se connecter à l'API**")
        st.info(f"💡 Vérifiez que l'API est démarrée sur: {API_URL}")
        st.stop()
    except requests.exceptions.Timeout:
        st.error("⏱️ **Timeout : l'API met trop de temps à répondre**")
        st.stop()
    except requests.exceptions.HTTPError as e:
        st.error(f"⚠️ **Erreur HTTP** : {e}")
        st.stop()
    except Exception as e:
        st.error(f"⚠️ **Erreur inattendue** : {e}")
        st.stop()

def formater_euro(valeur: float) -> str:
    return f"{valeur:,.2f} €".replace(",", " ").replace(".", ",")

def formater_nombre(valeur: int) -> str:
    return f"{valeur:,}".replace(",", " ")

def formater_pourcentage(valeur: float) -> str:
    return f"{valeur:.2f}%"

# === VÉRIFICATION CONNEXION API ===
with st.spinner("🔄 Connexion à l'API..."):
    try:
        info_api = appeler_api("/")
        st.success(f"✅ Connecté à l'API v{info_api['version']} - Dataset : {info_api['nb_lignes']} lignes")
    except:
        st.error(f"❌ L'API n'est pas accessible sur {API_URL}")
        st.stop()

# === HEADER ===
st.title("🛒 Superstore BI Dashboard - Advanced Analytics")
st.markdown("**Analyse Business Intelligence avancée avec matrices stratégiques et analyses temporelles**")
st.divider()

# === SIDEBAR - FILTRES ===
st.sidebar.header("🎯 Filtres d'analyse")
valeurs_filtres = appeler_api("/filters/valeurs")

# Filtres temporels
st.sidebar.subheader("📅 Période")
date_min = datetime.strptime(valeurs_filtres['plage_dates']['min'], '%Y-%m-%d')
date_max = datetime.strptime(valeurs_filtres['plage_dates']['max'], '%Y-%m-%d')

col1, col2 = st.sidebar.columns(2)
with col1:
    date_debut = st.date_input("Du", value=date_min, min_value=date_min, max_value=date_max)
with col2:
    date_fin = st.date_input("Au", value=date_max, min_value=date_min, max_value=date_max)

# Autres filtres
st.sidebar.subheader("📦 Catégorie")
categorie = st.sidebar.selectbox("Sélectionner", options=["Toutes"] + valeurs_filtres['categories'])

st.sidebar.subheader("🌍 Région")
region = st.sidebar.selectbox("Sélectionner ", options=["Toutes"] + valeurs_filtres['regions'])

st.sidebar.subheader("👥 Segment")
segment = st.sidebar.selectbox("Sélectionner  ", options=["Tous"] + valeurs_filtres['segments'])

if st.sidebar.button("🔄 Réinitialiser", use_container_width=True):
    st.rerun()

st.sidebar.divider()
st.sidebar.info("💡 Les graphiques sont interactifs !")

# Paramètres filtres
params_filtres = {
    'date_debut': date_debut.strftime('%Y-%m-%d'),
    'date_fin': date_fin.strftime('%Y-%m-%d')
}
if categorie != "Toutes":
    params_filtres['categorie'] = categorie
if region != "Toutes":
    params_filtres['region'] = region
if segment != "Tous":
    params_filtres['segment'] = segment

# === SECTION KPI GLOBAUX ===
st.header("📊 Indicateurs Clés de Performance")

kpi_data = appeler_api("/kpi/globaux", params=params_filtres)

# Niveau 1 : Performance Financière (KPI's Critiques)
st.subheader("💰 Performance Financière")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("💰 CA Total", formater_euro(kpi_data['ca_total']))
with col2:
    st.metric("💵 Profit Total", formater_euro(kpi_data['profit_total']))
with col3:
    st.metric("📈 Marge Moyenne", formater_pourcentage(kpi_data['marge_moyenne']))

st.markdown("---")

# Niveau 2 : Volume d'Activité (KPI's Opérationnels)
st.subheader("📊 Volume d'Activité")
col4, col5, col6 = st.columns(3)
with col4:
    st.metric("🧾 Commandes", formater_nombre(kpi_data['nb_commandes']))
with col5:
    st.metric("📦 Quantité Vendue", formater_nombre(kpi_data['quantite_vendue']))
with col6:
    st.metric("👥 Clients Uniques", formater_nombre(kpi_data['nb_clients']))

st.markdown("---")

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

st.divider()

# === TABS PRINCIPAUX ===
st.header("📈 Analyses Détaillées")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏆 Produits", "📦 Catégories", "📅 Temporel", "🌍 Géographique", "👥 Clients"])

# =============================================
# TAB 1 : PRODUITS AVANCÉS
# =============================================
with tab1:
    st.subheader("🎯 Analyse Stratégique des Produits")
    
    # Sous-tabs pour les différentes analyses produits
    prod_tab1, prod_tab2, prod_tab3 = st.tabs(["📊 Matrice BCG", "⚠️ Produits Faible Marge", "🏆 Top Produits"])
    
    # --- MATRICE BCG ---
    with prod_tab1:
        st.markdown("### 📊 Matrice BCG (Boston Consulting Group)")
        st.markdown("""
        **Interprétation des quadrants :**
        - ⭐ **Étoiles** : Part de marché élevée + Croissance forte → Investir
        - 🐄 **Vaches à lait** : Part de marché élevée + Croissance faible → Rentabiliser
        - ❓ **Dilemmes** : Part de marché faible + Croissance forte → Décider
        - 💀 **Poids morts** : Part de marché faible + Croissance faible → Abandonner
        """)
        
        bcg_data = appeler_api("/kpi/produits/bcg", params={'limite': 100})
        
        if "error" not in bcg_data:
            df_bcg = pd.DataFrame(bcg_data['data'])
            
            # Affichage des seuils et répartition
            col_info1, col_info2, col_info3, col_info4 = st.columns(4)
            with col_info1:
                st.metric("⭐ Étoiles", bcg_data['repartition']['etoiles'])
            with col_info2:
                st.metric("🐄 Vaches à lait", bcg_data['repartition']['vaches'])
            with col_info3:
                st.metric("❓ Dilemmes", bcg_data['repartition']['dilemmes'])
            with col_info4:
                st.metric("💀 Poids morts", bcg_data['repartition']['poids_morts'])
            
            # Graphique BCG
            # Définir les couleurs par quadrant
            color_map = {
                "Étoile ⭐": "#28a745",
                "Vache à lait 🐄": "#007bff", 
                "Dilemme ❓": "#ffc107",
                "Poids mort 💀": "#dc3545"
            }
            
            df_bcg['color'] = df_bcg['quadrant'].map(color_map)
            
            fig_bcg = px.scatter(
                df_bcg[df_bcg['ca_actuel'] > 0],
                x='part_marche',
                y='croissance',
                size='ca_actuel',
                color='quadrant',
                hover_name='produit',
                hover_data={
                    'categorie': True,
                    'ca_actuel': ':.2f',
                    'marge_pct': ':.2f',
                    'part_marche': ':.4f',
                    'croissance': ':.2f'
                },
                color_discrete_map=color_map,
                title=f"Matrice BCG - {bcg_data['seuils']['annee_precedente']} vs {bcg_data['seuils']['annee_actuelle']}",
                labels={
                    'part_marche': 'Part de marché (%)',
                    'croissance': 'Croissance YoY (%)',
                    'quadrant': 'Quadrant'
                },
                height=600
            )
            
            # Ajouter les lignes de seuil
            fig_bcg.add_hline(y=10, line_dash="dash", line_color="gray", annotation_text="Seuil croissance (10%)")
            fig_bcg.add_vline(x=0.5, line_dash="dash", line_color="gray", annotation_text="Seuil part marché (0.5%)")
            
            fig_bcg.update_layout(
                xaxis_type="log",
                showlegend=True
            )
            
            st.plotly_chart(fig_bcg, use_container_width=True)
            
            # Tableau détaillé par quadrant
            with st.expander("📋 Détail par quadrant"):
                quadrant_select = st.selectbox(
                    "Filtrer par quadrant",
                    options=["Tous"] + list(df_bcg['quadrant'].unique())
                )
                
                df_display = df_bcg if quadrant_select == "Tous" else df_bcg[df_bcg['quadrant'] == quadrant_select]
                
                st.dataframe(
                    df_display[['produit', 'categorie', 'ca_actuel', 'croissance', 'part_marche', 'marge_pct', 'quadrant']].rename(columns={
                        'produit': 'Produit',
                        'categorie': 'Catégorie',
                        'ca_actuel': 'CA (€)',
                        'croissance': 'Croissance (%)',
                        'part_marche': 'Part marché (%)',
                        'marge_pct': 'Marge (%)',
                        'quadrant': 'Quadrant'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.warning("⚠️ Pas assez de données historiques pour la matrice BCG")
    
    # --- PRODUITS FAIBLE MARGE ---
    with prod_tab2:
        st.markdown("### ⚠️ Produits à Faible Marge")
        st.markdown("*Produits qui génèrent du CA mais peu de profit - À optimiser ou abandonner*")
        
        col_seuil, col_limite = st.columns([1, 1])
        with col_seuil:
            seuil_marge = st.slider("Seuil de marge (%)", 0.0, 20.0, 5.0, 0.5)
        with col_limite:
            nb_produits_fm = st.slider("Nombre de produits", 10, 50, 20)
        
        faible_marge_data = appeler_api("/kpi/produits/faible-marge", params={'seuil_marge': seuil_marge, 'limite': nb_produits_fm})
        
        # Statistiques
        stats = faible_marge_data['statistiques']
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        with col_s1:
            st.metric("Nb produits", stats['nb_produits_faible_marge'])
        with col_s2:
            st.metric("CA concerné", formater_euro(stats['ca_total_faible_marge']))
        with col_s3:
            st.metric("% CA total", f"{stats['pct_ca_total']}%")
        with col_s4:
            st.metric("🔴 En perte", stats['nb_produits_perte'])
        
        df_fm = pd.DataFrame(faible_marge_data['data'])
        
        if len(df_fm) > 0:
            # Graphique double axe : CA vs Marge
            fig_fm = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig_fm.add_trace(
                go.Bar(
                    name='CA',
                    x=df_fm['produit'].str[:30] + '...',
                    y=df_fm['ca'],
                    marker_color='#3498db',
                    text=df_fm['ca'].apply(lambda x: f"{x:,.0f}€"),
                    textposition='outside'
                ),
                secondary_y=False
            )
            
            fig_fm.add_trace(
                go.Scatter(
                    name='Marge %',
                    x=df_fm['produit'].str[:30] + '...',
                    y=df_fm['marge_pct'],
                    mode='lines+markers',
                    line=dict(color='#e74c3c', width=3),
                    marker=dict(size=10)
                ),
                secondary_y=True
            )
            
            fig_fm.update_layout(
                title="Produits à faible marge : CA vs Marge",
                height=500,
                xaxis_tickangle=-45
            )
            fig_fm.update_yaxes(title_text="CA (€)", secondary_y=False)
            fig_fm.update_yaxes(title_text="Marge (%)", secondary_y=True)
            
            st.plotly_chart(fig_fm, use_container_width=True)
            
            # Tableau avec indicateur de rotation
            with st.expander("📋 Tableau détaillé avec rotation des stocks"):
                st.dataframe(
                    df_fm[['produit', 'categorie', 'ca', 'profit', 'marge_pct', 'discount_moyen', 'rotation', 'alerte']].rename(columns={
                        'produit': 'Produit',
                        'categorie': 'Catégorie',
                        'ca': 'CA (€)',
                        'profit': 'Profit (€)',
                        'marge_pct': 'Marge (%)',
                        'discount_moyen': 'Discount moy (%)',
                        'rotation': 'Rotation',
                        'alerte': 'Alerte'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
    
    # --- TOP PRODUITS CLASSIQUE ---
    with prod_tab3:
        st.markdown("### 🏆 Top Produits")
        
        col_tri, col_nb = st.columns([3, 1])
        with col_tri:
            critere_tri = st.radio(
                "Trier par",
                options=['ca', 'profit', 'quantite'],
                format_func=lambda x: {'ca': '💰 CA', 'profit': '💵 Profit', 'quantite': '📦 Quantité'}[x],
                horizontal=True
            )
        with col_nb:
            nb_produits = st.number_input("Afficher", min_value=5, max_value=50, value=10, step=5)
        
        top_produits = appeler_api("/kpi/produits/top", params={'limite': nb_produits, 'tri_par': critere_tri})
        df_produits = pd.DataFrame(top_produits)
        
        fig_produits = px.bar(
            df_produits,
            x=critere_tri,
            y='produit',
            color='categorie',
            orientation='h',
            title=f"Top {nb_produits} Produits",
            labels={'ca': 'CA (€)', 'profit': 'Profit (€)', 'quantite': 'Quantité', 'produit': 'Produit'},
            color_discrete_sequence=px.colors.qualitative.Set2,
            height=500
        )
        fig_produits.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_produits, use_container_width=True)

# =============================================
# TAB 2 : CATÉGORIES AVANCÉES
# =============================================
with tab2:
    st.subheader("📦 Analyse Stratégique des Catégories")
    
    cat_tab1, cat_tab2, cat_tab3 = st.tabs(["📊 Waterfall Profit", "🎯 Matrice Performance", "📈 Vue Standard"])
    
    # --- WATERFALL ---
    with cat_tab1:
        st.markdown("### 📊 Cascade de Contribution au Profit")
        st.markdown("*Visualisation de la contribution de chaque catégorie et sous-catégorie au profit total*")
        
        waterfall_data = appeler_api("/kpi/categories/waterfall")
        
        # Graphique Waterfall par catégorie
        df_wf = pd.DataFrame(waterfall_data['waterfall'])
        
        fig_waterfall = go.Figure(go.Waterfall(
            name="Profit",
            orientation="v",
            measure=["relative"] * len(df_wf) + ["total"],
            x=list(df_wf['label']) + ["Total"],
            y=list(df_wf['value']) + [waterfall_data['profit_total']],
            textposition="outside",
            text=[f"{v:,.0f}€" for v in df_wf['value']] + [f"{waterfall_data['profit_total']:,.0f}€"],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            increasing={"marker": {"color": "#28a745"}},
            decreasing={"marker": {"color": "#dc3545"}},
            totals={"marker": {"color": "#007bff"}}
        ))
        
        fig_waterfall.update_layout(
            title="Contribution au Profit par Catégorie",
            height=450,
            showlegend=False
        )
        
        st.plotly_chart(fig_waterfall, use_container_width=True)
        
        # Détail par sous-catégorie
        st.markdown("#### Détail par Sous-catégorie")
        df_subcat = pd.DataFrame(waterfall_data['detail_sous_categories'])
        
        fig_subcat = px.bar(
            df_subcat.sort_values('profit', ascending=True),
            x='profit',
            y='sous_categorie',
            color='categorie',
            orientation='h',
            title="Profit par Sous-catégorie",
            labels={'profit': 'Profit (€)', 'sous_categorie': 'Sous-catégorie'},
            color_discrete_sequence=px.colors.qualitative.Set2,
            height=600
        )
        
        st.plotly_chart(fig_subcat, use_container_width=True)
        
        with st.expander("📋 Tableau détaillé"):
            st.dataframe(
                df_subcat[['categorie', 'sous_categorie', 'ca', 'profit', 'marge_pct', 'contribution_pct']].rename(columns={
                    'categorie': 'Catégorie',
                    'sous_categorie': 'Sous-catégorie',
                    'ca': 'CA (€)',
                    'profit': 'Profit (€)',
                    'marge_pct': 'Marge (%)',
                    'contribution_pct': 'Contribution (%)'
                }).sort_values('Profit (€)', ascending=False),
                use_container_width=True,
                hide_index=True
            )
    
    # --- MATRICE PERFORMANCE/MARGE ---
    with cat_tab2:
        st.markdown("### 🎯 Matrice Performance/Marge")
        st.markdown("""
        **Quadrants stratégiques :**
        - 🌟 **Q1 - Priorité** : CA élevé + Marge élevée → Investir et développer
        - ⚙️ **Q2 - À optimiser** : CA élevé + Marge faible → Réduire les coûts
        - 📈 **Q3 - À développer** : CA faible + Marge élevée → Augmenter visibilité
        - ❌ **Q4 - À abandonner** : CA faible + Marge faible → Réduire ou arrêter
        """)
        
        matrix_data = appeler_api("/kpi/categories/matrix")
        df_matrix = pd.DataFrame(matrix_data['data'])
        
        # Répartition
        rep = matrix_data['repartition']
        col_q1, col_q2, col_q3, col_q4 = st.columns(4)
        with col_q1:
            st.markdown(f"""<div class="quadrant-box quadrant-q1">
                <h4>🌟 Priorité</h4><h2>{rep['Q1_priorite']}</h2>
            </div>""", unsafe_allow_html=True)
        with col_q2:
            st.markdown(f"""<div class="quadrant-box quadrant-q2">
                <h4>⚙️ À optimiser</h4><h2>{rep['Q2_optimiser']}</h2>
            </div>""", unsafe_allow_html=True)
        with col_q3:
            st.markdown(f"""<div class="quadrant-box quadrant-q3">
                <h4>📈 À développer</h4><h2>{rep['Q3_developper']}</h2>
            </div>""", unsafe_allow_html=True)
        with col_q4:
            st.markdown(f"""<div class="quadrant-box quadrant-q4">
                <h4>❌ À abandonner</h4><h2>{rep['Q4_abandonner']}</h2>
            </div>""", unsafe_allow_html=True)
        
        # Graphique scatter
        color_map_matrix = {
            "Q1 - Priorité 🌟": "#28a745",
            "Q2 - À optimiser ⚙️": "#ffc107",
            "Q3 - À développer 📈": "#007bff",
            "Q4 - À abandonner ❌": "#dc3545"
        }

        # Use absolute value of profit for size (scatter size must be non-negative)
        df_matrix['profit_abs'] = df_matrix['profit'].abs()

        fig_matrix = px.scatter(
            df_matrix,
            x='ca',
            y='marge_pct',
            size='profit_abs',
            color='quadrant',
            hover_name='sous_categorie',
            hover_data={
                'categorie': True,
                'ca': ':.2f',
                'marge_pct': ':.2f',
                'profit': ':.2f',
                'action_recommandee': True
            },
            color_discrete_map=color_map_matrix,
            title="Matrice Performance/Marge par Sous-catégorie",
            labels={'ca': 'Chiffre d\'affaires (€)', 'marge_pct': 'Marge (%)'},
            height=550
        )
        
        # Lignes de seuil
        fig_matrix.add_hline(y=matrix_data['seuils']['marge_median'], line_dash="dash", line_color="gray")
        fig_matrix.add_vline(x=matrix_data['seuils']['ca_median'], line_dash="dash", line_color="gray")
        
        st.plotly_chart(fig_matrix, use_container_width=True)
        
        # Tableau avec actions
        with st.expander("📋 Plan d'action par sous-catégorie"):
            st.dataframe(
                df_matrix[['categorie', 'sous_categorie', 'ca', 'marge_pct', 'quadrant', 'action_recommandee']].rename(columns={
                    'categorie': 'Catégorie',
                    'sous_categorie': 'Sous-catégorie',
                    'ca': 'CA (€)',
                    'marge_pct': 'Marge (%)',
                    'quadrant': 'Quadrant',
                    'action_recommandee': 'Action'
                }),
                use_container_width=True,
                hide_index=True
            )
    
    # --- VUE STANDARD ---
    with cat_tab3:
        categories = appeler_api("/kpi/categories")
        df_cat = pd.DataFrame(categories)
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            fig_cat = go.Figure()
            fig_cat.add_trace(go.Bar(name='CA', x=df_cat['categorie'], y=df_cat['ca'], marker_color='#667eea'))
            fig_cat.add_trace(go.Bar(name='Profit', x=df_cat['categorie'], y=df_cat['profit'], marker_color='#764ba2'))
            fig_cat.update_layout(title="CA et Profit par Catégorie", barmode='group', height=400)
            st.plotly_chart(fig_cat, use_container_width=True)
        
        with col_right:
            fig_marge = px.bar(df_cat, x='categorie', y='marge_pct', title="Marge par Catégorie (%)",
                              color='marge_pct', color_continuous_scale='Viridis', text='marge_pct', height=400)
            fig_marge.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
            st.plotly_chart(fig_marge, use_container_width=True)

# =============================================
# TAB 3 : TEMPOREL AVANCÉ
# =============================================
with tab3:
    st.subheader("📅 Analyse Temporelle Avancée")

    temp_tab1, temp_tab2, temp_tab3 = st.tabs(["📊 Évolutions Classiques", "📈 Tendances & Moyenne Mobile", "🔄 Comparaison N/N-1"])

    # --- ÉVOLUTIONS CLASSIQUES (CA, PROFIT, COMMANDES) ---
    with temp_tab1:
        st.markdown("### 📊 Évolution du CA, Profit et Commandes")

        # Sélecteur de granularité
        granularite = st.radio(
            "Période d'analyse",
            options=['jour', 'mois', 'annee'],
            format_func=lambda x: {'jour': '📅 Par jour', 'mois': '📊 Par mois', 'annee': '📈 Par année'}[x],
            horizontal=True
        )

        temporal = appeler_api("/kpi/temporel", params={'periode': granularite})
        df_temporal = pd.DataFrame(temporal)

        # Graphique d'évolution
        fig_temporal = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Évolution du CA et Profit", "Évolution du Nombre de Commandes"),
            vertical_spacing=0.12,
            specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
        )

        # Graphique CA et Profit
        fig_temporal.add_trace(
            go.Scatter(
                x=df_temporal['periode'],
                y=df_temporal['ca'],
                mode='lines+markers',
                name='CA',
                line=dict(color='#667eea', width=3),
                fill='tozeroy'
            ),
            row=1, col=1
        )

        fig_temporal.add_trace(
            go.Scatter(
                x=df_temporal['periode'],
                y=df_temporal['profit'],
                mode='lines+markers',
                name='Profit',
                line=dict(color='#764ba2', width=3)
            ),
            row=1, col=1
        )

        # Graphique nombre de commandes
        fig_temporal.add_trace(
            go.Bar(
                x=df_temporal['periode'],
                y=df_temporal['nb_commandes'],
                name='Commandes',
                marker_color='#f39c12'
            ),
            row=2, col=1
        )

        fig_temporal.update_xaxes(title_text="Période", row=2, col=1)
        fig_temporal.update_yaxes(title_text="Montant (€)", row=1, col=1)
        fig_temporal.update_yaxes(title_text="Nombre", row=2, col=1)
        fig_temporal.update_layout(height=700, showlegend=True)

        st.plotly_chart(fig_temporal, use_container_width=True)

        # Statistiques temporelles
        col_stats1, col_stats2, col_stats3 = st.columns(3)
        with col_stats1:
            st.metric("📈 CA moyen/période", formater_euro(df_temporal['ca'].mean()))
        with col_stats2:
            st.metric("📊 Commandes moy/période", formater_nombre(int(df_temporal['nb_commandes'].mean())))
        with col_stats3:
            meilleure_periode = df_temporal.loc[df_temporal['ca'].idxmax()]
            st.metric("🏆 Meilleure période", meilleure_periode['periode'])

    # --- ÉVOLUTION AVEC MOYENNE MOBILE ---
    with temp_tab2:
        st.markdown("### 📈 Évolution avec Moyenne Mobile")
        
        temporal_avance = appeler_api("/kpi/temporel/avance")
        df_temp = pd.DataFrame(temporal_avance['data'])
        
        # Statistiques
        stats_temp = temporal_avance['statistiques']
        col_t1, col_t2, col_t3, col_t4 = st.columns(4)
        with col_t1:
            st.metric("CA moyen/mois", formater_euro(stats_temp['ca_moyen_mensuel']))
        with col_t2:
            st.metric("Croissance moy.", f"{stats_temp['croissance_moyenne']:.1f}%")
        with col_t3:
            st.metric("Meilleur mois", stats_temp['meilleur_mois'])
        with col_t4:
            st.metric("Pire mois", stats_temp['pire_mois'])
        
        # Graphique avec moyenne mobile
        fig_mm = go.Figure()
        
        fig_mm.add_trace(go.Scatter(
            x=df_temp['periode'],
            y=df_temp['ca'],
            mode='lines+markers',
            name='CA réel',
            line=dict(color='#3498db', width=2),
            fill='tozeroy',
            fillcolor='rgba(52, 152, 219, 0.2)'
        ))
        
        fig_mm.add_trace(go.Scatter(
            x=df_temp['periode'],
            y=df_temp['ca_mm3'],
            mode='lines',
            name='Moyenne mobile 3 mois',
            line=dict(color='#e74c3c', width=3, dash='solid')
        ))
        
        fig_mm.update_layout(
            title="CA Mensuel avec Moyenne Mobile (3 mois)",
            xaxis_title="Période",
            yaxis_title="CA (€)",
            height=450,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_mm, use_container_width=True)
    
    # --- COMPARAISON N/N-1 ---
    with temp_tab3:
        st.markdown("### 🔄 Comparaison Année N vs N-1")
        
        df_comp = pd.DataFrame(temporal_avance['data'])
        
        # Filtrer les données avec N-1 disponible
        df_comp_valid = df_comp[df_comp['ca_n1'].notna()].copy()
        
        if len(df_comp_valid) > 0:
            fig_comp = go.Figure()
            
            # Année N
            fig_comp.add_trace(go.Bar(
                x=df_comp_valid['periode'],
                y=df_comp_valid['ca'],
                name='Année N',
                marker_color='#3498db'
            ))
            
            # Année N-1 (en transparence)
            fig_comp.add_trace(go.Bar(
                x=df_comp_valid['periode'],
                y=df_comp_valid['ca_n1'],
                name='Année N-1',
                marker_color='rgba(52, 152, 219, 0.3)'
            ))
            
            fig_comp.update_layout(
                title="Comparaison CA : Année N vs N-1",
                barmode='overlay',
                xaxis_title="Période",
                yaxis_title="CA (€)",
                height=450
            )
            
            st.plotly_chart(fig_comp, use_container_width=True)
            
            # Variation YoY
            fig_yoy = px.bar(
                df_comp_valid,
                x='periode',
                y='variation_yoy',
                color='variation_yoy',
                color_continuous_scale=['#dc3545', '#ffc107', '#28a745'],
                color_continuous_midpoint=0,
                title="Variation Year-over-Year (%)",
                labels={'variation_yoy': 'Variation YoY (%)'},
                height=350
            )
            
            st.plotly_chart(fig_yoy, use_container_width=True)
        else:
            st.warning("⚠️ Pas assez de données pour la comparaison N/N-1")

# =============================================
# TAB 4 : GÉOGRAPHIQUE AVANCÉ
# =============================================
with tab4:
    st.subheader("🌍 Analyse Géographique Avancée")
    
    geo_tab1, geo_tab2, geo_tab3 = st.tabs(["🗺️ Performance États", "🏙️ Top Villes", "📊 Vue Régions"])
    
    # --- PERFORMANCE PAR ÉTAT ---
    with geo_tab1:
        st.markdown("### 🗺️ Performance par État (Heatmap)")
        
        etats_data = appeler_api("/kpi/geographique/etats")
        df_etats = pd.DataFrame(etats_data['data'])
        
        # Heatmap des états par marge
        st.markdown("#### Carte thermique : Marge par État")
        
        fig_heatmap_etats = px.treemap(
            df_etats,
            path=['region', 'etat'],
            values='ca',
            color='marge_pct',
            color_continuous_scale='RdYlGn',
            color_continuous_midpoint=df_etats['marge_pct'].median(),
            title="Treemap : CA (taille) et Marge (couleur) par État",
            hover_data=['profit', 'nb_clients', 'ca_par_client'],
            height=600
        )
        
        st.plotly_chart(fig_heatmap_etats, use_container_width=True)

        # Tableau complet
        with st.expander("📋 Tableau complet par État"):
            st.dataframe(
                df_etats[['etat', 'region', 'ca', 'profit', 'marge_pct', 'nb_clients', 'ca_par_client', 'performance']].rename(columns={
                    'etat': 'État',
                    'region': 'Région',
                    'ca': 'CA (€)',
                    'profit': 'Profit (€)',
                    'marge_pct': 'Marge (%)',
                    'nb_clients': 'Clients',
                    'ca_par_client': 'CA/Client (€)',
                    'performance': 'Performance'
                }),
                use_container_width=True,
                hide_index=True
            )
    
    # --- TOP VILLES ---
    with geo_tab2:
        st.markdown("### 🏙️ Top Villes Performantes")
        
        nb_villes = st.slider("Nombre de villes", 10, 50, 20)
        villes_data = appeler_api("/kpi/geographique/villes", params={'limite': nb_villes})
        
        # Stats
        stats_villes = villes_data['statistiques']
        col_v1, col_v2, col_v3 = st.columns(3)
        with col_v1:
            st.metric("Nb villes total", stats_villes['nb_villes_total'])
        with col_v2:
            st.metric("CA moyen/ville", formater_euro(stats_villes['ca_moyen_ville']))
        with col_v3:
            st.metric("Clients moy/ville", f"{stats_villes['clients_moyen_ville']:.1f}")
        
        # Top CA
        st.markdown("#### 💰 Top Villes par CA")
        df_villes_ca = pd.DataFrame(villes_data['top_ca'])
        
        fig_villes = px.bar(
            df_villes_ca.head(15),
            x='ca',
            y='ville',
            color='region',
            orientation='h',
            title=f"Top 15 Villes par CA",
            labels={'ca': 'CA (€)', 'ville': 'Ville'},
            height=500
        )
        fig_villes.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_villes, use_container_width=True)

    # --- VUE RÉGIONS STANDARD ---
    with geo_tab3:
        geo = appeler_api("/kpi/geographique")
        df_geo = pd.DataFrame(geo)
        
        col_geo1, col_geo2 = st.columns(2)
        
        with col_geo1:
            fig_geo_ca = px.bar(
                df_geo, x='region', y='ca',
                title="CA par Région",
                color='ca', color_continuous_scale='Blues',
                text='ca', height=400
            )
            fig_geo_ca.update_traces(texttemplate='%{text:,.0f}€', textposition='outside')
            st.plotly_chart(fig_geo_ca, use_container_width=True)
        
        with col_geo2:
            fig_geo_clients = px.pie(
                df_geo, values='nb_clients', names='region',
                title="Répartition Clients par Région",
                color_discrete_sequence=px.colors.qualitative.Set3,
                height=400
            )
            fig_geo_clients.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_geo_clients, use_container_width=True)

# =============================================
# TAB 5 : CLIENTS
# =============================================
with tab5:
    st.subheader("👥 Analyse Clients")

    clients_data = appeler_api("/kpi/clients", params={'limite': 10})

    col_client1, col_client2 = st.columns([2, 1])

    with col_client1:
        df_top_clients = pd.DataFrame(clients_data['top_clients'])
        fig_clients = px.bar(
            df_top_clients, x='ca_total', y='nom', orientation='h',
            title="Top 10 Clients par CA",
            color='nb_commandes', color_continuous_scale='Viridis',
            height=400
        )
        st.plotly_chart(fig_clients, use_container_width=True)

    with col_client2:
        rec = clients_data['recurrence']
        st.metric("Total clients", formater_nombre(rec['total_clients']))
        st.metric("Clients récurrents", formater_nombre(rec['clients_recurrents']))
        st.metric("Clients 1 achat", formater_nombre(rec['clients_1_achat']))
        taux_fid = (rec['clients_recurrents'] / rec['total_clients'] * 100) if rec['total_clients'] > 0 else 0
        st.metric("Taux fidélisation", f"{taux_fid:.1f}%")

    # Segments
    df_segments = pd.DataFrame(clients_data['segments'])
    fig_segments = go.Figure()
    fig_segments.add_trace(go.Bar(name='CA', x=df_segments['segment'], y=df_segments['ca'], marker_color='#3498db'))
    fig_segments.add_trace(go.Bar(name='Profit', x=df_segments['segment'], y=df_segments['profit'], marker_color='#2ecc71'))
    fig_segments.update_layout(title="CA et Profit par Segment", barmode='group', height=350)
    st.plotly_chart(fig_segments, use_container_width=True)

st.divider()

# === FOOTER ===
st.divider()
st.markdown("""
<div style='text-align: center; color: #7f8c8d;'>
    <p>📊 <b>Superstore BI Dashboard - Advanced Analytics</b> | FastAPI + Streamlit + Plotly</p>
    <p>🎯 Matrices BCG, Waterfall, Saisonnalité, Analyses géographiques avancées</p>
</div>
""", unsafe_allow_html=True)
