"""
Page Dashboard Produits - Performance Catalogue
📊 Category Manager / Responsable Produits
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import requests
import os
from datetime import datetime

# === CONFIGURATION PAGE ===
st.set_page_config(
    page_title="Produits - Superstore BI",
    page_icon="📊",
    layout="wide"
)

# === CONFIGURATION API ===
API_URL = os.getenv("API_URL", "http://localhost:8000")

@st.cache_data(ttl=300)
def appeler_api(endpoint: str, params: dict = None):
    try:
        response = requests.get(f"{API_URL}{endpoint}", params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"⚠️ Erreur API : {e}")
        return None

def formater_euro(v): return f"{v:,.2f} €".replace(",", " ").replace(".", ",")
def formater_nombre(v): return f"{v:,}".replace(",", " ")

# === SIDEBAR - FILTRES ===
st.sidebar.header("🎯 Filtres d'analyse")
valeurs_filtres = appeler_api("/filters/valeurs")

if valeurs_filtres:
    st.sidebar.subheader("📅 Période")
    date_min = datetime.strptime(valeurs_filtres['plage_dates']['min'], '%Y-%m-%d')
    date_max = datetime.strptime(valeurs_filtres['plage_dates']['max'], '%Y-%m-%d')
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        date_debut = st.date_input("Du", value=date_min, min_value=date_min, max_value=date_max)
    with col2:
        date_fin = st.date_input("Au", value=date_max, min_value=date_min, max_value=date_max)
    
    st.sidebar.subheader("📦 Catégorie")
    categorie = st.sidebar.selectbox("Sélectionner", options=["Toutes"] + valeurs_filtres['categories'])
    
    st.sidebar.subheader("🌍 Région")
    region = st.sidebar.selectbox("Sélectionner ", options=["Toutes"] + valeurs_filtres['regions'])
    
    st.sidebar.subheader("👥 Segment")
    segment = st.sidebar.selectbox("Sélectionner  ", options=["Tous"] + valeurs_filtres['segments'])
    
    if st.sidebar.button("🔄 Réinitialiser"):
        st.rerun()
    
    params_filtres = {
        'date_debut': date_debut.strftime('%Y-%m-%d'),
        'date_fin': date_fin.strftime('%Y-%m-%d')
    }
    if categorie != "Toutes": params_filtres['categorie'] = categorie
    if region != "Toutes": params_filtres['region'] = region
    if segment != "Tous": params_filtres['segment'] = segment
else:
    params_filtres = {}

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

# === PAGE PRINCIPALE ===
st.header("📊 Tableau de Bord Produits")
st.markdown("**Optimisation du catalogue : performances, matrices stratégiques**")
st.divider()

tab1, tab2= st.tabs(["🎯 PRIORITÉS STRATÉGIQUES", "📦 PERFORMANCE PRODUITS & CATÉGORIES"])

# ========== TAB 1 : MATRICES ==========
with tab1:
    st.markdown("### 🎯 Priorités Stratégiques")
    st.markdown("*Analyses stratégiques : Matrices BCG et Performance, Produits à faible marge*")
    st.divider()

    # Sous-tabs pour analyses stratégiques
    strat_tab1, strat_tab2, strat_tab3 = st.tabs([
        "📊 Matrice BCG",
        "🎯 Matrice Performance",
        "⚠️ Produits Faible Marge"
    ])

    # --- MATRICE BCG (déplacé depuis ancien Tab1 Produits) ---
    with strat_tab1:
        st.markdown("#### 📊 Matrice BCG (Boston Consulting Group)")
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

        st.markdown(
            """
            <div class="info-card">
                <div class="info-title">Data Storytelling</div>
                Cette matrice BCG révèle un portefeuille déséquilibré avec 60 produits "Dilemmes" nécessitant des décisions stratégiques urgentes, 
                contre seulement 20 "Étoiles" à développer et 3 "Vaches à lait" à rentabiliser. Les 17 "Poids morts" devraient être abandonnés 
                rapidement. 
                La concentration de produits dans le quadrant "Dilemmes" indique une dispersion des efforts sur trop de 
                références non rentables, obligeant l'entreprise à choisir lesquelles méritent l'investissement pour 
                devenir des "Étoiles" et lesquelles éliminer pour libérer des ressources.
            </div>
            """,
            unsafe_allow_html=True
        )

    # --- MATRICE PERFORMANCE CATÉGORIES (déplacé depuis ancien Tab2) ---
    with strat_tab2:
        st.markdown("#### 🎯 Matrice Performance/Marge")
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
        
        st.markdown(
            """
            <div class="info-card">
                <div class="info-title">Data Storytelling</div>
                L'analyse performance/marge segmente le catalogue en 4 priorités stratégiques : 3 produits 
                "Priorité à protéger absolument, 6 produits "À optimiser" nécessitant 
                une renégociation des coûts, 6 produits "À développer" offrant un potentiel 
                de croissance, et 2 produits "À abandonner". Cette répartition équilibrée entre optimisation et 
                développement 
                suggère qu'avec les bonnes actions correctives sur les 6 produits à optimiser, l'entreprise pourrait 
                significativement améliorer sa rentabilité globale sans compromettre le volume.
            </div>
            """,
            unsafe_allow_html=True
        )

    # --- PRODUITS FAIBLE MARGE (déplacé depuis ancien Tab1) ---
    with strat_tab3:
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
        
        st.markdown(
            """
            <div class="info-card">
                <div class="info-title">Data Storytelling</div>
                20 produits génèrent à peine du profit avec un seuil de marge sous 5%, représentant 259 015€ 
                de CA (11,28% du total) mais détruisant de la valeur avec 15 références en perte réelle. La ligne rouge de marge affiche des 
                valeurs négatives catastrophiques (jusqu'à -80%), transformant du 
                chiffre d'affaires en pertes. Cette situation critique exige une action immédiate : augmenter les prix de 10-15% 
                sur ces références, renégocier les conditions d'achat, ou supprimer ces produits toxiques qui drainent la 
                rentabilité globale de l'entreprise.
            </div>
            """,
            unsafe_allow_html=True
        )

# ========== TAB 2 : TOP PRODUITS ==========
with tab2:
    st.markdown("### 📦 Performance Produits & Catégories")
    st.markdown("*Analyses opérationnelles détaillées des produits et catégories*")
    st.divider()

    perf_tab1, perf_tab2, perf_tab3 = st.tabs(["🏆 Top Produits", "📊 Vue Catégories", "📊 Analyse ABC (Pareto)"])

    # --- TOP PRODUITS ---
    with perf_tab1:
        st.markdown("#### 🏆 Top Produits")

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

        st.markdown(
            """
            <div class="info-card">
                <div class="info-title">Data Storytelling</div>
                <b>1. Top 10 Produits par Chiffre d’Affaires</b><br>
                Le Canon imageCLASS 2200 domine largement le chiffre d’affaires (> 60 000€, soit presque 3x
                plus que le deuxième produit), révélant une forte dépendance à quelques références technologiques, 
                notamment des copieurs et systèmes de reliure. 
                Cette concentration souligne le positionnement B2B de l’entreprise, mais suggère aussi un risque de 
                dépendance et une opportunité de diversification des produits vedettes. <br><br>
                <b>2. Top 10 Produits par Profit</b><br>
                Si le Canon imageCLASS reste le plus rentable (~25 000€), son avance est plus modérée, indiquant 
                une marge plus serrée. À l’inverse, le Fellowes PB500 se distingue par un excellent 
                ratio profit / chiffre d’affaires, montrant que volume et rentabilité ne coïncident pas 
                toujours et qu’un arbitrage stratégique est nécessaire. <br><br>
                <b>3. Top 10 Produits par Quantité</b><br>
                Les consommables bureautiques (papier, enveloppes, agrafes) dominent les volumes, mais ont 
                un faible impact sur le chiffre d’affaires. Cette structure révèle un modèle à deux 
                vitesses : les consommables génèrent récurrence et fidélisation, tandis que les équipements 
                technologiques portent la rentabilité.
                </div>
            """,
            unsafe_allow_html=True
        )

    # --- VUE CATÉGORIES ---
    with perf_tab2:
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

        st.markdown(
            """
            <div class="info-card">
                <div class="info-title">Data Storytelling</div>
                La catégorie Technology domine avec 836 000€ de CA et 145 000€ de profit (marge 17,4%).
                Les Office Supplies suivent avec un CA similaire mais marge comparable, tandis que 
                Furniture, malgré un CA correct, affiche une marge très faible (2,5%), détruisant 
                presque la rentabilité.
                La vraie valeur se situe donc dans Technology et Office Supplies.
                L’entreprise devrait repenser sa stratégie Furniture : augmenter les prix, réduire les coûts 
                ou envisager un abandon.
                </div>
            """,
            unsafe_allow_html=True
        )

    # --- ANALYSE ABC (PARETO) ---
    with perf_tab3:
        st.markdown("#### 📊 Analyse ABC (Pareto)")
        st.markdown("""
        **Principe de Pareto (80/20) :**
        - 🌟 **Classe A** : Éléments générant 80% du CA (priorité maximale)
        - 📊 **Classe B** : Éléments générant 15% du CA (importance moyenne)
        - 📉 **Classe C** : Éléments générant 5% du CA (faible importance)
        """)

        niveau_abc = st.radio(
            "Niveau d'analyse",
            options=['produit', 'categorie', 'client'],
            format_func=lambda x: {'produit': '📦 Par Produit', 'categorie': '📂 Par Catégorie', 'client': '👥 Par Client'}[x],
            horizontal=True
        )

        abc_data = appeler_api("/kpi/analyse-abc", params={'niveau': niveau_abc})

        # Définir le mapping de couleurs cohérent
        COLOR_MAP_ABC = {
            "A 🌟": "#28a745",  # Vert
            "B 📊": "#ffc107",  # Jaune
            "C 📉": "#dc3545"   # Rouge
        }

        # Statistiques globales
        stats_abc = abc_data['statistiques']
        col_abc1, col_abc2 = st.columns(2)
        with col_abc1:
            st.metric("📊 Total Éléments", formater_nombre(stats_abc['total_elements']))
        with col_abc2:
            st.metric("💰 CA Total", formater_euro(stats_abc['ca_total']))

        st.divider()

        # Statistiques par classe
        df_classes = pd.DataFrame(abc_data['par_classe'])

        col_classe1, col_classe2 = st.columns(2)

        with col_classe1:
            fig_abc_pie = px.pie(
                df_classes,
                values='nombre',
                names='classe',
                title="Répartition du Nombre d'Éléments par Classe",
                color='classe',  # Utiliser color au lieu de color_discrete_sequence
                color_discrete_map=COLOR_MAP_ABC,  # Utiliser le même mapping
                height=350
            )
            st.plotly_chart(fig_abc_pie, use_container_width=True)

        with col_classe2:
            fig_abc_ca = px.bar(
                df_classes,
                x='classe',
                y='pct_ca',
                title="% CA par Classe",
                labels={'pct_ca': '% CA', 'classe': 'Classe'},
                text='pct_ca',
                color='classe',
                color_discrete_map=COLOR_MAP_ABC,  # Utiliser le même mapping
                height=350
            )
            fig_abc_ca.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            st.plotly_chart(fig_abc_ca, use_container_width=True)

        # Tableau des statistiques par classe
        st.markdown("#### 📋 Détail par Classe")
        st.dataframe(
            df_classes[['classe', 'nombre', 'pct_nombre', 'ca_total', 'pct_ca', 'profit_total']].rename(columns={
                'classe': 'Classe',
                'nombre': 'Nombre',
                'pct_nombre': '% Nombre',
                'ca_total': 'CA Total (€)',
                'pct_ca': '% CA',
                'profit_total': 'Profit Total (€)'
            }),
            use_container_width=True,
            hide_index=True
        )

        st.markdown(
            """
            <div class="info-card">
                <div class="info-title">Data Storytelling</div>
                L'analyse ABC confirme le principe de Pareto : seulement 22,6% des produits génèrent 79,96% du CA, tandis que la Classe B contribue à 15,05% du CA. Le déséquilibre majeur provient de la Classe C : 50,8% des produits ne représentent que 5% du CA, révélant une sur-prolifération du catalogue. Cette répartition impose une action urgente : éliminer 30-50% des références Classe C libérerait des ressources critiques (achats, stockage, merchandising) pour concentrer les efforts sur les 419 produits stratégiques de Classe A qui portent réellement la performance.
                </div>
            """,
            unsafe_allow_html=True
        )

        st.divider()

        # Courbe de Pareto
        st.markdown("#### 📈 Courbe de Pareto (% cumulé du CA)")
        df_abc_full = pd.DataFrame(abc_data['data'])
        
        # Ajuster les paramètres du slider en fonction du nombre d'éléments
        nb_elements = len(df_abc_full)
        
        # Définir min et max de manière adaptative
        if nb_elements <= 10:
            # Si très peu d'éléments, afficher tous sans slider
            nb_affichage = nb_elements
            st.info(f"Affichage des {nb_elements} éléments disponibles")
        else:
            # Sinon, afficher un slider avec des valeurs cohérentes
            min_slider = min(10, nb_elements)
            max_slider = min(100, nb_elements)
            default_slider = min(50, nb_elements)
            
            nb_affichage = st.slider(
                "Nombre d'éléments à afficher", 
                min_slider, 
                max_slider, 
                default_slider, 
                key="abc_pareto"
            )
        
        df_abc_display = df_abc_full.head(nb_affichage)
        
        fig_pareto = make_subplots(specs=[[{"secondary_y": True}]])
        fig_pareto.add_trace(
            go.Bar(
                name='CA',
                x=list(range(1, len(df_abc_display) + 1)),
                y=df_abc_display['ca'],
                marker_color='#3498db'
            ),
            secondary_y=False
        )
        fig_pareto.add_trace(
            go.Scatter(
                name='% Cumulé',
                x=list(range(1, len(df_abc_display) + 1)),
                y=df_abc_display['pct_cumul'],
                mode='lines+markers',
                line=dict(color='#e74c3c', width=3),
                marker=dict(size=8)
            ),
            secondary_y=True
        )

        # Ajouter ligne 80%
        fig_pareto.add_hline(y=80, line_dash="dash", line_color="green", annotation_text="80%", secondary_y=True)
        fig_pareto.update_layout(
            title="Courbe de Pareto",
            height=500
        )
        fig_pareto.update_xaxes(title_text="Rang (du plus important au moins important)")
        fig_pareto.update_yaxes(title_text="CA (€)", secondary_y=False)
        fig_pareto.update_yaxes(title_text="% CA Cumulé", secondary_y=True, range=[0, 105])
        st.plotly_chart(fig_pareto, use_container_width=True)

        # Tableau détaillé avec filtrage par classe
        with st.expander("📋 Tableau détaillé des variations"):
            st.markdown("#### 📋 Tableau Détaillé")

            classe_filter = st.selectbox(
                "Filtrer par classe",
                options=['Toutes'] + list(df_abc_full['classe'].unique()),
                key="abc_filter"
            )

            if classe_filter == 'Toutes':
                df_abc_filtered = df_abc_full.head(100)  # Limiter à 100 pour performance
            else:
                df_abc_filtered = df_abc_full[df_abc_full['classe'] == classe_filter].head(100)

            st.dataframe(
                df_abc_filtered[['nom', 'categorie', 'ca', 'profit', 'pct_ca', 'pct_cumul', 'classe']].rename(columns={
                    'nom': 'Nom',
                    'categorie': 'Catégorie',
                    'ca': 'CA (€)',
                    'profit': 'Profit (€)',
                    'pct_ca': '% CA',
                    'pct_cumul': '% Cumulé',
                    'classe': 'Classe'
                }),
                use_container_width=True,
                hide_index=True
            ) 

        st.markdown(
            """
            <div class="info-card">
                <div class="info-title">Data Storytelling</div>
                La courbe de Pareto visualise la concentration extrême du CA : les 50 premiers produits (sur 1 850) génèrent déjà 30% du CA total, formant le coude critique de la courbe. Le premier produit seul pèse environ 60 000€, et les 10 premiers cumulent près de 10% du CA. Cette visualisation confirme qu'un tout petit nombre de références pilote la performance : concentrer les efforts commerciaux, la gestion des stocks et les négociations fournisseurs sur ces 50 produits critiques pourrait maximiser l'efficacité opérationnelle, tandis que les 1 800 autres références mériteraient une gestion plus automatisée et simplifiée.
                </div>
            """,
            unsafe_allow_html=True
        )