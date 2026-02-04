import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import requests
import os
from datetime import datetime
st.set_page_config(page_title="Direction - Superstore BI", page_icon="👔", layout="wide")
API_URL = os.getenv("API_URL", "http://localhost:8000")

@st.cache_data(ttl=300)
def appeler_api(endpoint: str, params: dict = None):
    try:
        r = requests.get(f"{API_URL}{endpoint}", params=params, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Erreur API : {e}")
        return None
    
def formater_euro(valeur: float) -> str:
    return f"{valeur:,.2f} €".replace(",", " ").replace(".", ",")

def formater_nombre(valeur: int) -> str:
    return f"{valeur:,}".replace(",", " ")

def formater_pourcentage(valeur: float) -> str:
    return f"{valeur:.2f}%"

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

st.header("👔 Tableau de Bord Direction")
st.markdown("**Vision stratégique globale : performance, clients, géographie, logistique**")
st.divider()

tab1, tab2, tab3, tab4 = st.tabs(["📈 Évolution", "🌍 Géographie", "👥 Clients", "🚚 Logistique"])

# ================= EVOLUTION =================
with tab1:
    st.markdown("### 📅 Évolution Temporelle")
    st.markdown("*Analyses temporelles consolidées : tendances, moyennes mobiles et comparaisons*")
    st.divider()

    # Sous-onglets pour la section temporelle
    temp_tab1, temp_tab2, temp_tab3 = st.tabs([
        "📈 Évolution du CA et Profit",
        "📊 Indicateurs clés par période",
        "📉 Variations annuelles"
    ])

    # --- SOUS-ONGLET 1 : ÉVOLUTION CA ET PROFIT ---
    with temp_tab1:
        st.markdown("#### 📊 Évolution du CA, Profit et Commandes")

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

        st.markdown(
            """
            <div class="info-card">
                <div class="info-title">Data Storytelling</div>
                <b>1. Évolution Temporelle par jour</b><br>
                La vue quotidienne montre une forte volatilité avec des pics jusqu’à 30 000€ certains jours et de
                longues périodes quasi-nulles. Les gros CA ponctuels proviennent probablement de grosses commandes B2B, 
                posant un défi de trésorerie et de planification. <br><br>
                <b>2. Évolution Temporelle par mois</b><br>
                L’agrégation mensuelle lisse la volatilité et révèle une tendance haussière de 2015 à 2018 : le CA moyen 
                passe de 40 000€ à plus de 100 000€. Les commandes suivent une progression régulière, confirmant 
                une croissance soutenue sur 4 ans, avec accélération notable depuis mi-2017. <br><br>
                <b>3. Évolution Temporelle par année</b><br>
                La vue annuelle confirme une croissance solide : le CA progresse de 470 000€ à 700 000€ 
                entre 2015 et 2018, et les commandes de 1 000 à 1 600+. L’ascension constante démontre la solidité du modèle
                et l’efficacité opérationnelle, avec 2018 comme année record. La question stratégique : comment dépasser le 
                million d’euros ?
            </div>
            """,
            unsafe_allow_html=True
        )

    # --- SOUS-ONGLET 2 : INDICATEURS CLÉS PAR PÉRIODE ---
    with temp_tab2:
        st.markdown("#### 📊 Statistiques et Tendances par Période")

        # Utiliser les données déjà chargées
        temporal = appeler_api("/kpi/temporel", params={'periode': 'mois'})
        df_temporal = pd.DataFrame(temporal)

        # Statistiques temporelles
        col_stats1, col_stats2, col_stats3 = st.columns(3)
        with col_stats1:
            st.metric("CA moyen/période", formater_euro(df_temporal['ca'].mean()))
        with col_stats2:
            st.metric("Commandes moy/période", formater_nombre(int(df_temporal['nb_commandes'].mean())))
        with col_stats3:
            meilleure_periode = df_temporal.loc[df_temporal['ca'].idxmax()]
            st.metric("Meilleure période", meilleure_periode['periode'])

        st.divider()

        temporal_avance = appeler_api("/kpi/temporel/avance")
        df_temp = pd.DataFrame(temporal_avance['data'])

        # Statistiques
        stats_temp = temporal_avance['statistiques']
        col_t2, col_t4 = st.columns(2)
        with col_t2:
            st.metric("Croissance moy.", f"{stats_temp['croissance_moyenne']:.1f}%")
        with col_t4:
            st.metric("Pire mois", stats_temp['pire_mois'])

        st.markdown(
            """
            <div class="info-card">
                <div class="info-title">Data Storytelling</div>
                Le CA moyen mensuel atteint 47 858€ avec 104 commandes moyennes par mois, le pic historique 
                restant novembre 2018. La croissance moyenne de 40,7% démontre une dynamique exceptionnelle, bien que le pire mois (février 
                2015) contraste fortement avec cette tendance. 
            </div>
            """,
            unsafe_allow_html=True
        )

    # --- SOUS-ONGLET 3 : VARIATIONS ANNUELLES ---
    with temp_tab3:
        st.markdown("#### 📉 Comparaison N/N-1 (Year-over-Year)")

        temporal_avance = appeler_api("/kpi/temporel/avance")
        df_comp = pd.DataFrame(temporal_avance['data'])

        # Filtrer les données avec N-1 disponible
        df_comp_valid = df_comp[df_comp['ca_n1'].notna()].copy()

        if len(df_comp_valid) > 0:
            # Variation YoY simplifiée
            fig_yoy = px.bar(
                df_comp_valid,
                x='periode',
                y='variation_yoy',
                color='variation_yoy',
                color_continuous_scale=['#dc3545', '#ffc107', '#28a745'],
                color_continuous_midpoint=0,
                title="Variation Year-over-Year (%)",
                labels={'variation_yoy': 'Variation YoY (%)'},
                height=500
            )

            st.plotly_chart(fig_yoy, use_container_width=True)

            # Tableau détaillé des variations
            with st.expander("📋 Tableau détaillé des variations"):
                st.dataframe(
                    df_comp_valid[['periode', 'ca', 'ca_n1', 'variation_yoy']].rename(columns={
                        'periode': 'Période',
                        'ca': 'CA Année N (€)',
                        'ca_n1': 'CA Année N-1 (€)',
                        'variation_yoy': 'Variation (%)'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.warning("⚠️ Pas assez de données pour la comparaison N/N-1")

        st.markdown(
            """
            <div class="info-card">
                <div class="info-title">Data Storytelling</div>
                L'analyse Year-over-Year montre une croissance volatile mais majoritairement positive : janvier 2016 
                explose à +160% (effet de base faible), suivie de fluctuations entre -40% et +140%. À partir de 2017, la 
                croissance se stabilise entre +10% et +90%, avec une tendance haussière marquée. Fin 2018 ralentit légèrement (+20-
                50%), ce qui est normal après une forte croissance. Cette volatilité en dents de scie suggère des effets 
                saisonniers ou des variations ponctuelles de commandes importantes, mais la tendance générale reste 
                solidement positive sur 3 ans.
            </div>
            """,
            unsafe_allow_html=True
        )

# ================= GEO =================
with tab2:
    st.markdown("### 🌍 Analyse Géographique")
    st.markdown("*Analyses spatiales : performance par région, état et ville*")
    st.divider()

    geo_tab1, geo_tab2, geo_tab3 = st.tabs(["🗺️ Performance États", "🏙️ Top Villes", "📊 Vue Régions"])

    # --- PERFORMANCE PAR ÉTAT ---
    with geo_tab1:
        st.markdown("**Performance par État (Heatmap)**")

        etats_data = appeler_api("/kpi/geographique/etats")
        df_etats = pd.DataFrame(etats_data['data'])

        # Heatmap des états par marge
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
        
        st.markdown(
            """
            <div class="info-card">
                <div class="info-title">Data Storytelling</div>
                La heatmap révèle une performance par État très contrastée : la Californie (West) domine en taille mais pas en marge, 
                tout comme Pennsylvania, Texas, Ohio et Illinois (en rouge/orange) qui affichent des marges négatives ou très 
                faibles malgré des volumes importants. New York, bien que générant du CA, souffre également de rentabilité. A l'inverse, des états peu volumineux ont des marges plutôt élevées.
                Cette cartographie met en évidence un paradoxe : les plus gros États ne sont pas les plus rentables. 
                L'entreprise doit investiguer les causes (prix trop bas, coûts logistiques, mix produit défavorable) et 
                corriger rapidement la situation dans ces États stratégiques pour transformer du volume en profit.
            </div>
            """,
            unsafe_allow_html=True
        )

    # --- TOP VILLES ---
    with geo_tab2:
        st.markdown("**Top Villes Performantes**")

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

        st.markdown(
            """
            <div class="info-card">
                <div class="info-title">Data Storytelling</div>
                604 villes génèrent un CA moyen de 3 803€ par ville, New York City dominant largement avec plus 
                de 250 000€, soit presque le double de Los Angeles (200 000€). Les régions East et West concentrent les plus grosses villes 
                performantes, tandis que Central (Houston, Chicago, Detroit) et South (Jacksonville, San Antonio) ont des 
                contributions plus modestes. Cette concentration géographique sur quelques métropoles majeures révèle un 
                potentiel inexploité dans les villes moyennes : développer la présence commerciale dans les 580+ villes 
                à faible CA pourrait doubler le chiffre d'affaires national.
            </div>
            """,
            unsafe_allow_html=True
        )

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

        st.markdown(
            """
            <div class="info-card">
                <div class="info-title">Analyse Géographique – Synthèse</div>
                Les régions West et East dominent le chiffre d’affaires (725 000€ et 679 000€), 
                représentant 55% de l’activité. La répartition des clients reste équilibrée (27,4% West, 26,9% East), 
                mais le profit par région montre une surperformance de West (108 000€ vs 91 000€).
                Les régions Central et South, avec une densité de clients similaire mais un CA inférieur, 
                représentent un potentiel de croissance important si les actions commerciales sont adaptées.
            </div>
            """,
            unsafe_allow_html=True
        )

# ================= EVOLUTION =================
with tab3:
    st.markdown("### 👥 Analyse Clients")
    st.markdown("*Comportement client, fidélisation, segmentation et valeur vie client*")
    st.divider()

    client_tab1, client_tab2, client_tab3, client_tab4, client_tab5 = st.tabs([
        "📊 Vue Générale",
        "🎯 Segmentation RFM",
        "💰 Customer Lifetime Value",
        "🔄 Délai de Réachat",
        "📈 Taux de Rétention"
    ])

    # --- VUE GÉNÉRALE ---
    with client_tab1:
        st.markdown("#### 📊 Vue Générale des Clients")

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

        st.markdown(
            """
            <div class="info-card">
                <div class="info-title">Data Storytelling</div>
                Avec 98,5 % de clients récurrents, l’entreprise affiche une fidélisation exceptionnelle et 
                des relations commerciales régulières (6,3 commandes par client).
                Le faible nombre de nouveaux clients suggère une phase de maturité ou un ralentissement de 
                l’acquisition.
                Enfin, la répartition homogène du chiffre d’affaires du top 10 clients indique une 
                base clients équilibrée, sans dépendance excessive à un compte unique.
                </div>
            """,
            unsafe_allow_html=True
        )

        # Segments
        df_segments = pd.DataFrame(clients_data['segments'])
        fig_segments = go.Figure()
        fig_segments.add_trace(go.Bar(name='CA', x=df_segments['segment'], y=df_segments['ca'], marker_color='#3498db'))
        fig_segments.add_trace(go.Bar(name='Profit', x=df_segments['segment'], y=df_segments['profit'], marker_color='#2ecc71'))
        fig_segments.update_layout(title="CA et Profit par Segment", barmode='group', height=350)
        st.plotly_chart(fig_segments, use_container_width=True)

        st.markdown(
            """
            <div class="info-card">
                <div class="info-title">Data Storytelling</div>
                Le segment Consumer domine largement le chiffre d’affaires (> 1,2 M€), loin devant les 
                segments Corporate et Home Office.
                Cependant, les écarts de marge suggèrent que ces segments plus modestes pourraient offrir 
                une rentabilité ou une stabilité supérieure.
                Cette structure pose un enjeu stratégique clair : poursuivre la spécialisation Consumer ou 
                diversifier vers des segments à plus forte valeur ajoutée.
            </div>
            """,
            unsafe_allow_html=True
        )

    # --- SEGMENTATION RFM ---
    with client_tab2:
        st.markdown("#### 🎯 Segmentation RFM")
        st.markdown("""
        **Segmentation basée sur :**
        - **R** (Recency) : Ancienneté du dernier achat
        - **F** (Frequency) : Fréquence d'achat
        - **M** (Monetary) : Montant total dépensé
        """)

        rfm_data = appeler_api("/kpi/clients/rfm")

        # Statistiques globales
        stats_rfm = rfm_data['statistiques']
        col_rfm1, col_rfm2, col_rfm3, col_rfm4 = st.columns(4)
        with col_rfm1:
            st.metric("👥 Total Clients", formater_nombre(stats_rfm['nb_total_clients']))
        with col_rfm2:
            st.metric("📅 Récence Moy.", f"{stats_rfm['recency_moyenne']:.0f} jours")
        with col_rfm3:
            st.metric("🔄 Fréquence Moy.", f"{stats_rfm['frequency_moyenne']:.1f}")
        with col_rfm4:
            st.metric("💰 Montant Moy.", formater_euro(stats_rfm['monetary_moyenne']))

        st.divider()

        # Répartition par segment
        df_segments_rfm = pd.DataFrame(rfm_data['segments'])

        col_left_rfm, col_right_rfm = st.columns([1, 1])

        with col_left_rfm:
            fig_rfm_pie = px.pie(
                df_segments_rfm,
                values='nb_clients',
                names='segment',
                title="Répartition des Clients par Segment RFM",
                height=400,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_rfm_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_rfm_pie, use_container_width=True)

        with col_right_rfm:
            fig_rfm_bar = px.bar(
                df_segments_rfm.sort_values('ca_total', ascending=True),
                y='segment',
                x='ca_total',
                orientation='h',
                title="CA Total par Segment RFM",
                labels={'ca_total': 'CA Total (€)', 'segment': 'Segment'},
                color='ca_total',
                color_continuous_scale='Greens',
                height=400
            )
            st.plotly_chart(fig_rfm_bar, use_container_width=True)

        st.markdown(
            """
            <div class="info-card">
                <div class="info-title">Data Storytelling</div>
                La segmentation RFM (Récence, Fréquence, Montant) classe les 793 clients selon leur comportement d'achat, révélant une récence moyenne de 147 jours et une fréquence de 6,3 achats pour un montant moyen de 2 897€. Les segments "Fidèles" et "Champions" dominent le CA avec plus de 600 000€ chacun, représentant les clients les plus actifs et généreux. Les "À risque" (18,3% des clients) et "Perdus" (21,6%) nécessitent des actions de reconquête urgentes, tandis que les "Nouveaux" (11,2%) doivent être rapidement convertis en clients réguliers. Cette segmentation actionnable permet de prioriser les efforts marketing : récompenser les Champions, réactiver les clients À risque, et accompagner les Nouveaux vers la fidélisation.
            </div>
            """,
            unsafe_allow_html=True
        )

    # --- CUSTOMER LIFETIME VALUE ---
    with client_tab3:
        st.markdown("#### 💰 Customer Lifetime Value (CLV)")
        st.markdown("*Valeur vie client projetée sur 3 ans*")

        nb_clients_clv = st.slider("Nombre de clients", 10, 100, 50, key="clv_slider")

        clv_data = appeler_api("/kpi/clients/clv", params={'limite': nb_clients_clv})

        # Statistiques
        stats_clv = clv_data['statistiques']
        col_clv1, col_clv2, col_clv3 = st.columns(3)
        with col_clv1:
            st.metric("💎 CLV Moyenne", formater_euro(stats_clv['clv_moyenne']))
        with col_clv2:
            st.metric("📊 CLV Médiane", formater_euro(stats_clv['clv_mediane']))
        with col_clv3:
            st.metric("📈 CA Annuel Moy.", formater_euro(stats_clv['ca_annuel_moyen']))

        st.divider()

        # Répartition par catégorie
        df_cat_clv = pd.DataFrame(clv_data['par_categorie'])

        col_cat1, col_cat2 = st.columns(2)

        with col_cat1:
            fig_clv_cat = px.pie(
                df_cat_clv,
                values='nb_clients',
                names='categorie',
                title="Répartition des Clients par Catégorie CLV",
                height=350
            )
            st.plotly_chart(fig_clv_cat, use_container_width=True)

        with col_cat2:
            fig_clv_value = px.bar(
                df_cat_clv,
                x='categorie',
                y='clv_total',
                title="CLV Totale par Catégorie",
                labels={'clv_total': 'CLV Totale (€)', 'categorie': 'Catégorie'},
                color='clv_total',
                color_continuous_scale='Blues',
                height=350
            )
            st.plotly_chart(fig_clv_value, use_container_width=True)

        # Top clients par CLV
        df_top_clv = pd.DataFrame(clv_data['top_clients'])

        fig_clv_top = px.bar(
            df_top_clv.head(20),
            x='clv_3_ans',
            y='client',
            orientation='h',
            title="Top 20 Clients par CLV (3 ans)",
            labels={'clv_3_ans': 'CLV 3 ans (€)', 'client': 'Client'},
            color='categorie',
            height=600
        )
        fig_clv_top.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_clv_top, use_container_width=True)

        # Tableau détaillé
        with st.expander("📋 Tableau détaillé CLV"):
            st.dataframe(
                df_top_clv[['client', 'ca_total', 'nb_commandes', 'ca_annuel', 'clv_3_ans', 'profit_clv_3_ans', 'categorie']].rename(columns={
                    'client': 'Client',
                    'ca_total': 'CA Total (€)',
                    'nb_commandes': 'Nb Commandes',
                    'ca_annuel': 'CA Annuel (€)',
                    'clv_3_ans': 'CLV 3 ans (€)',
                    'profit_clv_3_ans': 'Profit CLV 3 ans (€)',
                    'categorie': 'Catégorie'
                }),
                use_container_width=True,
                hide_index=True
            )

        st.markdown(
            """
            <div class="info-card">
                <div class="info-title">Data Storytelling</div>
                La CLV moyenne de 11 434€ sur 3 ans (médiane à 2 603€) révèle une forte disparité de valeur client, avec 31,4% des clients "Élevés" représentant 7 millions d'euros cumulés. Cette concentration atteint son paroxysme dans le top 20, dominé par Jenna Caffey, Susan Mackendrick et Theresa Coyne, soit des actifs clients extraordinaires qui, à eux seuls, représentent plus de 15% de la valeur future totale. L'écart brutal avec le reste du top 20 (sous 200 000€) et les 23% de clients à "Faible" CLV crée un double enjeu stratégique : d'une part, la perte d'un seul top 5 client détruirait plusieurs centaines de milliers d'euros de valeur, nécessitant un account management dédié avec contrats pluriannuels et support premium ; d'autre part, l'allocation budgétaire doit impérativement être repensée pour surinvestir dans la rétention des clients à fort potentiel tout en automatisant le service des clients à faible CLV pour préserver la rentabilité globale.
            </div>
            """,
            unsafe_allow_html=True
        )

    # --- DÉLAI DE RÉACHAT ---
    with client_tab4:
        st.markdown("#### 🔄 Délai Moyen de Réachat")
        st.markdown("*Temps moyen entre deux achats par client*")

        delai_data = appeler_api("/kpi/clients/delai-rachat")

        # Statistiques globales
        stats_delai = delai_data['statistiques']
        col_del1, col_del2, col_del3 = st.columns(3)
        with col_del1:
            st.metric("📅 Délai Moyen", f"{stats_delai['delai_moyen_jours']:.0f} jours")
        with col_del2:
            st.metric("📊 Délai Médian", f"{stats_delai['delai_median_jours']:.0f} jours")
        with col_del3:
            st.metric("🔄 Nb Rachats", formater_nombre(stats_delai['nb_rachats_total']))

        st.divider()

        # Distribution des délais
        distribution_delai = delai_data['distribution']

        df_distrib = pd.DataFrame([
            {'tranche': k, 'nb_rachats': v}
            for k, v in distribution_delai.items()
        ])

        fig_distrib = px.bar(
            df_distrib,
            x='tranche',
            y='nb_rachats',
            title="Distribution des Délais de Réachat",
            labels={'tranche': 'Tranche de délai', 'nb_rachats': 'Nombre de rachats'},
            color='nb_rachats',
            color_continuous_scale='Viridis',
            height=400
        )
        st.plotly_chart(fig_distrib, use_container_width=True)

        st.markdown(
            """
            <div class="info-card">
                <div class="info-title">Data Storytelling</div>
                Le délai moyen de réachat de 189 jours (médiane 129 jours) sur 4 199 rachats révèle un cycle d'achat relativement long, cohérent avec un modèle B2B de fournitures et équipements. La distribution montre une concentration dans les tranches 90-180 jours (environ 2 000 rachats), suggérant un cycle naturel trimestriel ou semestriel. Cette donnée permet d'optimiser les relances commerciales : contacter proactivement les clients 15-30 jours avant leur date de réachat prévue pourrait améliorer la rétention et prévenir le churn.
            </div>
            """,
            unsafe_allow_html=True
        )

    # --- TAUX DE RÉTENTION ---
    with client_tab5:
        st.markdown("#### 📈 Taux de Rétention (Cohort Analysis)")
        st.markdown("*Analyse de la rétention client par cohorte (mois de première commande)*")

        retention_data = appeler_api("/kpi/clients/retention")

        # Statistiques
        stats_ret = retention_data['statistiques']
        col_ret1, col_ret2, col_ret3, col_ret4 = st.columns(4)
        with col_ret1:
            st.metric("📊 Nb Cohortes", stats_ret['nb_cohortes'])
        with col_ret2:
            st.metric("📅 Rétention 1M", f"{stats_ret['retention_1_mois']:.1f}%")
        with col_ret3:
            st.metric("📅 Rétention 3M", f"{stats_ret['retention_3_mois']:.1f}%")
        with col_ret4:
            st.metric("📅 Rétention 6M", f"{stats_ret['retention_6_mois']:.1f}%")

        st.divider()

        # Heatmap de rétention
        df_cohort_retention = pd.DataFrame(retention_data['cohort_data'])

        if len(df_cohort_retention) > 0:
            st.markdown("**📊 Matrice de Rétention (12 dernières cohortes)**")
            st.markdown("*Chaque ligne = cohorte (mois première commande), Chaque colonne = mois depuis première commande*")

            # Créer une matrice pour la heatmap
            cohort_cols = [col for col in df_cohort_retention.columns if col.startswith('month_')]

            if len(cohort_cols) > 0:
                matrix_data = df_cohort_retention[['cohort'] + cohort_cols].set_index('cohort')

                fig_retention = px.imshow(
                    matrix_data,
                    labels=dict(x="Mois depuis 1ère commande", y="Cohorte", color="Rétention (%)"),
                    x=[f"M{i}" for i in range(len(cohort_cols))],
                    y=matrix_data.index,
                    color_continuous_scale='RdYlGn',
                    aspect='auto',
                    height=500
                )

                fig_retention.update_xaxes(side="bottom")
                st.plotly_chart(fig_retention, use_container_width=True)

                st.info("💡 **Interprétation** : Plus la couleur est verte, meilleure est la rétention. Les cohortes récentes ont moins de données historiques (normal).")
            else:
                st.warning("Pas assez de données pour afficher la matrice de rétention.")
        else:
            st.warning("Aucune donnée de cohorte disponible.")

        st.markdown(
            """
            <div class="info-card">
                <div class="info-title">Data Storytelling</div>
                L'analyse de cohorte révèle des taux de rétention alarmants : seulement 6,1% des clients rachètent après 1 mois, 8,6% après 3 mois et 10,2% après 6 mois. La matrice par cohorte (12 derniers mois) montre un schéma récurrent de forte attrition : le premier mois (M0) affiche 100% de rétention (vert), puis chute drastiquement à moins de 20% dès M1-M2 (rouge), avec quelques périodes de réactivation sporadiques (jaune-orange). Cette hémorragie de clients nouveaux indique un problème majeur d'onboarding ou d'adéquation produit-marché : moins de 10% des nouveaux clients deviennent récurrents, obligeant à une acquisition constante coûteuse plutôt qu'à capitaliser sur une base fidèle. Des actions d'activation post-première commande sont critiques pour inverser cette tendance.
            </div>
            """,
            unsafe_allow_html=True
        )

# ================= LOGISTIQUE =================
with tab4:
    st.markdown("### 🚚 Analyse des Livraisons")
    st.markdown("*Performance logistique : délais, retards et modes d'expédition*")
    st.divider()

    livraison_tab1, livraison_tab2, livraison_tab3 = st.tabs([
        "📦 Délais de Livraison",
        "⏰ Livraisons Tardives",
        "🚚 Performance par Mode"
    ])

    # --- DÉLAIS DE LIVRAISON ---
    with livraison_tab1:
        st.markdown("#### 📦 Délais de Livraison Réels")
        st.markdown("*Analyse des délais entre commande et livraison effective*")

        delais_data = appeler_api("/kpi/livraisons/delais")

        # Statistiques globales
        stats_delais = delais_data['statistiques']
        col_d1, col_d2, col_d3, col_d4 = st.columns(4)
        with col_d1:
            st.metric("📅 Délai Moyen", f"{stats_delais['delai_moyen_jours']:.1f} jours")
        with col_d2:
            st.metric("📊 Délai Médian", f"{stats_delais['delai_median_jours']:.1f} jours")
        with col_d3:
            st.metric("⚡ Délai Min", f"{stats_delais['delai_min_jours']} jours")
        with col_d4:
            st.metric("🐌 Délai Max", f"{stats_delais['delai_max_jours']} jours")

        st.divider()

        # Par mode d'expédition
        df_delais_mode = pd.DataFrame(delais_data['par_mode'])

        fig_delais_mode = go.Figure()

        fig_delais_mode.add_trace(go.Bar(
            name='Délai Moyen',
            x=df_delais_mode['mode'],
            y=df_delais_mode['delai_moyen'],
            marker_color='#3498db',
            text=df_delais_mode['delai_moyen'].apply(lambda x: f"{x:.1f}j"),
            textposition='outside'
        ))

        fig_delais_mode.add_trace(go.Bar(
            name='Délai Médian',
            x=df_delais_mode['mode'],
            y=df_delais_mode['delai_median'],
            marker_color='#2ecc71',
            text=df_delais_mode['delai_median'].apply(lambda x: f"{x:.1f}j"),
            textposition='outside'
        ))

        fig_delais_mode.update_layout(
            title="Délais de Livraison par Mode d'Expédition",
            xaxis_title="Mode d'Expédition",
            yaxis_title="Délai (jours)",
            barmode='group',
            height=450
        )

        st.plotly_chart(fig_delais_mode, use_container_width=True)

        # Distribution des délais
        distribution_delais = delais_data['distribution']
        df_distrib_delais = pd.DataFrame([
            {'tranche': k, 'nb_livraisons': v}
            for k, v in distribution_delais.items()
        ])

        col_dist1, col_dist2 = st.columns([2, 1])

        with col_dist1:
            fig_distrib_delais = px.bar(
                df_distrib_delais,
                x='tranche',
                y='nb_livraisons',
                title="Distribution des Délais de Livraison",
                labels={'tranche': 'Tranche de délai', 'nb_livraisons': 'Nombre de livraisons'},
                color='nb_livraisons',
                color_continuous_scale='Blues',
                height=400
            )
            st.plotly_chart(fig_distrib_delais, use_container_width=True)

        with col_dist2:
            # Par région
            df_delais_region = pd.DataFrame(delais_data['par_region'])

            fig_delais_region = px.bar(
                df_delais_region.sort_values('delai_moyen', ascending=True),
                y='region',
                x='delai_moyen',
                orientation='h',
                title="Délai Moyen par Région",
                labels={'delai_moyen': 'Délai (j)', 'region': 'Région'},
                color='delai_moyen',
                color_continuous_scale='Oranges',
                height=400
            )
            st.plotly_chart(fig_delais_region, use_container_width=True)

        st.markdown(
            """
            <div class="info-card">
                <div class="info-title">Data Storytelling</div>
                Les délais de livraison moyens et médians s'établissent à 4 jours, avec un minimum de 0 jour (livraison le jour même) et un maximum de 7 jours, démontrant une performance logistique plutôt correcte. L'analyse par mode d'expédition montre que First Class et Second Class offrent les délais les plus courts (2 & 3 jours moyens/médians) après Same day qui est à 0 jours, tandis que Standard Class prend logiquement plus de temps (5 jours). La distribution des délais révèle une forte concentration dans les tranches 2-4 jours et 4-7 jours (environ 4 000 livraisons chacun), avec très peu de retards extrêmes (>7 jours). Par région, Central affiche les délais les plus élevés (4 jours), suggérant des contraintes géographiques ou logistiques. Cette performance opérationnelle satisfaisante constitue un atout compétitif à capitaliser dans la communication client, tout en optimisant la région Central pour homogénéiser le service.
            </div>
            """,
            unsafe_allow_html=True
        )

    # --- LIVRAISONS TARDIVES ---
    with livraison_tab2:
        st.markdown("#### ⏰ Analyse des Livraisons Tardives")
        st.markdown("*Identification et analyse des retards de livraison*")

        retards_data = appeler_api("/kpi/livraisons/retards")

        # Statistiques globales
        stats_retards = retards_data['statistiques']
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            st.metric("📦 Total Livraisons", formater_nombre(stats_retards['nb_total_livraisons']))
        with col_r2:
            st.metric("⏰ Livraisons en Retard", formater_nombre(stats_retards['nb_retards']))
        with col_r3:
            st.metric("📊 Taux de Retard", f"{stats_retards['taux_retard_global']:.2f}%")

        # Affichage des seuils
        seuils = retards_data['seuils_utilises']
        st.info(f"**Seuils de retard utilisés** : {', '.join([f'{k}: {v}j' for k, v in seuils.items()])}")

        st.divider()

        # Par mode d'expédition
        df_retards_mode = pd.DataFrame(retards_data['par_mode'])

        col_mode1, col_mode2 = st.columns(2)

        with col_mode1:
            fig_retards_mode = px.bar(
                df_retards_mode,
                x='mode',
                y='taux_retard',
                title="Taux de Retard par Mode d'Expédition",
                labels={'taux_retard': 'Taux de Retard (%)', 'mode': 'Mode'},
                text='taux_retard',
                color='taux_retard',
                color_continuous_scale='Reds',
                height=400
            )
            fig_retards_mode.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            st.plotly_chart(fig_retards_mode, use_container_width=True)

        with col_mode2:
            # Par région
            df_retards_region = pd.DataFrame(retards_data['par_region'])

            fig_retards_region = px.bar(
                df_retards_region,
                x='region',
                y='taux_retard',
                title="Taux de Retard par Région",
                labels={'taux_retard': 'Taux de Retard (%)', 'region': 'Région'},
                text='taux_retard',
                color='taux_retard',
                color_continuous_scale='Oranges',
                height=400
            )
            fig_retards_region.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            st.plotly_chart(fig_retards_region, use_container_width=True)

        # Par catégorie
        df_retards_categorie = pd.DataFrame(retards_data['par_categorie'])

        fig_retards_cat = px.pie(
            df_retards_categorie,
            values='nb_retards',
            names='categorie',
            title="Répartition des Retards par Catégorie",
            height=400
        )
        st.plotly_chart(fig_retards_cat, use_container_width=True)

        # Tableau détaillé
        with st.expander("📋 Tableau détaillé par mode"):
            st.dataframe(
                df_retards_mode[['mode', 'nb_retards', 'nb_total', 'taux_retard']].rename(columns={
                    'mode': 'Mode',
                    'nb_retards': 'Nb Retards',
                    'nb_total': 'Nb Total',
                    'taux_retard': 'Taux (%)'
                }),
                use_container_width=True,
                hide_index=True
            )

        st.markdown(
            """
            <div class="info-card">
                <div class="info-title">Data Storytelling</div>
                Sur 9 994 livraisons totales, seulement 1 livraison est en retard (0,01%), démontrant une excellence opérationnelle quasi-parfaite. Cette unique livraison tardive provient du mode First Class et de la région East. La totalité des retards provient de la catégorie Office Supplies. Cette performance logistique exceptionnelle constitue un différenciateur majeur face à la concurrence : 99,99% de fiabilité de livraison est un argument commercial puissant qui devrait être mis en avant dans toute la communication, renforçant la confiance client et justifiant potentiellement des prix premium par rapport aux concurrents moins fiables.
            </div>
            """,
            unsafe_allow_html=True
        )

    # --- PERFORMANCE PAR MODE ---
    with livraison_tab3:
        st.markdown("#### 🚚 Performance par Mode d'Expédition")
        st.markdown("*Analyse complète : rentabilité, rapidité et volume*")

        perf_mode_data = appeler_api("/kpi/livraisons/performance-mode")

        # Insights
        insights = perf_mode_data['insights']
        col_i1, col_i2, col_i3 = st.columns(3)
        with col_i1:
            st.metric("💰 Plus Rentable", insights['mode_plus_rentable'])
        with col_i2:
            st.metric("⚡ Plus Rapide", insights['mode_plus_rapide'])
        with col_i3:
            st.metric("📊 Plus Utilisé", insights['mode_plus_utilise'])

        st.divider()

        # Données
        df_perf_mode = pd.DataFrame(perf_mode_data['data'])

        # Graphique comparatif
        fig_perf_compare = make_subplots(
            rows=2, cols=2,
            subplot_titles=("CA par Mode", "Nombre de Commandes", "Délai Moyen", "Marge"),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )

        fig_perf_compare.add_trace(
            go.Bar(x=df_perf_mode['mode'], y=df_perf_mode['ca'], name='CA', marker_color='#3498db'),
            row=1, col=1
        )

        fig_perf_compare.add_trace(
            go.Bar(x=df_perf_mode['mode'], y=df_perf_mode['nb_commandes'], name='Commandes', marker_color='#2ecc71'),
            row=1, col=2
        )

        fig_perf_compare.add_trace(
            go.Bar(x=df_perf_mode['mode'], y=df_perf_mode['delai_moyen'], name='Délai', marker_color='#e74c3c'),
            row=2, col=1
        )

        fig_perf_compare.add_trace(
            go.Bar(x=df_perf_mode['mode'], y=df_perf_mode['marge_pct'], name='Marge', marker_color='#f39c12'),
            row=2, col=2
        )

        fig_perf_compare.update_layout(height=700, showlegend=False)
        fig_perf_compare.update_xaxes(tickangle=-45)

        st.plotly_chart(fig_perf_compare, use_container_width=True)

        # Scatter : Rapidité vs Rentabilité
        st.markdown("#### ⚖️ Compromis Rapidité vs Rentabilité")

        fig_scatter = px.scatter(
            df_perf_mode,
            x='delai_moyen',
            y='marge_pct',
            size='nb_commandes',
            color='mode',
            hover_name='mode',
            hover_data={'ca': ':.2f', 'profit': ':.2f', 'nb_commandes': True},
            title="Délai Moyen vs Marge (taille = volume)",
            labels={'delai_moyen': 'Délai Moyen (jours)', 'marge_pct': 'Marge (%)', 'nb_commandes': 'Nb Commandes'},
            height=500
        )

        st.plotly_chart(fig_scatter, use_container_width=True)

        # Tableau récapitulatif
        st.markdown("#### 📋 Tableau Récapitulatif")

        st.dataframe(
            df_perf_mode[['mode', 'ca', 'profit', 'marge_pct', 'nb_commandes', 'pct_commandes', 'delai_moyen', 'delai_median']].rename(columns={
                'mode': 'Mode',
                'ca': 'CA (€)',
                'profit': 'Profit (€)',
                'marge_pct': 'Marge (%)',
                'nb_commandes': 'Nb Commandes',
                'pct_commandes': '% Commandes',
                'delai_moyen': 'Délai Moy. (j)',
                'delai_median': 'Délai Méd. (j)'
            }),
            use_container_width=True,
            hide_index=True
        )

        st.markdown(
            """
            <div class="info-card">
                <div class="info-title">Data Storytelling</div>
                Standard Class domine massivement avec 1,36M€ de CA et 2 994 commandes, mais génère la marge la plus faible avec un délai de 5 jours, créant un dilemme stratégique visualisé dans le graphique de compromis. First Class, bien que ne représentant que 351 000€ de CA et 787 commandes, affiche la meilleure marge (13,93%) avec le délai le plus rapide après Same Day, démontrant qu'une livraison plus rapide peut être plus rentable. Same Day, malgré son délai minimal, affiche un positionnement intermédiaire peu attractif avec seulement 128 000€, 264 commandes et une marge de 12,38%, ne justifiant pas son coût opérationnel. Cette analyse croisée révèle une opportunité stratégique majeure : migrer progressivement 20-30% des clients Standard Class vers First Class ou Second Class en valorisant la réduction de délai (-2 à -3 jours) contre une légère surcharge tarifaire améliorerait simultanément la marge globale de 1-2 points, la satisfaction client, et l'efficacité opérationnelle, tout en compensant largement les coûts logistiques supplémentaires par une meilleure rentabilité unitaire.
            </div>
            """,
            unsafe_allow_html=True
        )
