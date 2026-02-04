"""
Page Dashboard Finance - Rentabilité et Pertes
💰 Directeur Financier / Contrôleur de Gestion
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
    page_title="Finance - Superstore BI",
    page_icon="💰",
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

# === PAGE PRINCIPALE ===
st.header("💰 Tableau de Bord Finance")
st.markdown("**Analyse de rentabilité : marges, remises, pertes**")
st.divider()

detail_tab1, detail_tab2, detail_tab3 = st.tabs([
    "🔴 Commandes en Perte",
    "💸 Pertes liées aux Remises",
    "💰 Marges Insuffisantes"
])

# --- COMMANDES EN PERTE ---
with detail_tab1:
    st.markdown("#### 🔴 Commandes en Perte")
    st.markdown("*Identification des commandes générant une perte nette - Analyse des causes (remises excessives, coûts élevés, mix produits)*")

    nb_cmd_def = st.slider("Nombre de commandes", 10, 100, 50, key="cmd_def")

    cmd_def_data = appeler_api("/kpi/commandes/deficitaires", params={'limite': nb_cmd_def})

    # Statistiques
    stats_cmd = cmd_def_data['statistiques']
    col_d1, col_d2, col_d3, col_d4 = st.columns(4)
    with col_d1:
        st.metric("🔴 Nb Commandes", stats_cmd['nb_commandes_deficitaires'])
    with col_d2:
        st.metric("💸 Perte Totale", formater_euro(stats_cmd['perte_totale']))
    with col_d3:
        st.metric("📊 Perte Moyenne", formater_euro(stats_cmd['perte_moyenne']))
    with col_d4:
        st.metric("📈 % Commandes", f"{stats_cmd['pct_commandes_deficitaires']:.2f}%")

    df_cmd_def = pd.DataFrame(cmd_def_data['data'])

    if len(df_cmd_def) > 0:
        # Graphique des pertes
        fig_def = px.bar(
            df_cmd_def.head(20),
            x='order_id',
            y='perte_abs',
            color='discount_moyen',
            title="Top 20 Commandes Déficitaires (valeur absolue de la perte)",
            labels={'perte_abs': 'Perte (€)', 'order_id': 'Commande', 'discount_moyen': 'Discount (%)'},
            color_continuous_scale='Reds',
            height=450
        )
        fig_def.update_xaxes(tickangle=-45)
        st.plotly_chart(fig_def, use_container_width=True)

        # Tableau détaillé
        with st.expander("📋 Tableau détaillé des commandes déficitaires"):
            st.dataframe(
                df_cmd_def[['order_id', 'date', 'client', 'categories', 'ca', 'profit', 'marge_pct', 'discount_moyen']].rename(columns={
                    'order_id': 'Commande',
                    'date': 'Date',
                    'client': 'Client',
                    'categories': 'Catégories',
                    'ca': 'CA (€)',
                    'profit': 'Profit (€)',
                    'marge_pct': 'Marge (%)',
                    'discount_moyen': 'Discount (%)'
                }),
                use_container_width=True,
                hide_index=True
            )
    
    st.markdown(
        """
        <div class="info-card">
            <div class="info-title">Data Storytelling</div>
            Sur les 5 009 commandes totales, 1 022 (20,40%) génèrent une perte nette de 66 897€, soit une perte moyenne de 65€ par commande déficitaire. Le top 20 des commandes les plus déficitaires révèle des pertes allant jusqu'à 7 000€ (commande CA-2017-160326), principalement causées par des remises excessives (50-80% de discount en rouge foncé). Cette hémorragie financière concentrée sur quelques transactions catastrophiques indique un manque de contrôle sur les politiques de remise : certaines commandes sont vendues à perte massive, détruisant plusieurs milliers d'euros de marge. L'entreprise doit immédiatement instaurer des seuils d'approbation pour les remises supérieures à 20% et investiguer ces transactions aberrantes pour identifier s'il s'agit d'erreurs commerciales, de tarifications inadaptées ou de clients exploitant les politiques de discount.
        </div>
        """,
        unsafe_allow_html=True
    )

# --- PERTES LIÉES AUX REMISES ---
with detail_tab2:
    st.markdown("#### 💸 Impact des Remises (Discount)")
    st.markdown("*Quantification de l'impact des remises sur la rentabilité - Détection des politiques de remise trop généreuses entraînant des pertes*")

    remises_data = appeler_api("/kpi/remises/impact")

    # Statistiques globales
    stats_remises = remises_data['statistiques']

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.markdown("**📊 Avec Remise**")
        col_r1a, col_r1b = st.columns(2)
        with col_r1a:
            st.metric("CA", formater_euro(stats_remises['ca_avec_discount']))
        with col_r1b:
            st.metric("Marge", f"{stats_remises['marge_avec_discount']:.2f}%")

    with col_r2:
        st.markdown("**📊 Sans Remise**")
        col_r2a, col_r2b = st.columns(2)
        with col_r2a:
            st.metric("CA", formater_euro(stats_remises['ca_sans_discount']))
        with col_r2b:
            st.metric("Marge", f"{stats_remises['marge_sans_discount']:.2f}%")

    st.metric("📈 % CA avec remise", f"{stats_remises['pct_ca_avec_discount']:.2f}%")

    st.divider()

    # Graphique par tranche de remise
    df_remises = pd.DataFrame(remises_data['data'])

    fig_remises = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Impact sur le CA", "Impact sur la Marge"),
        specs=[[{"type": "bar"}, {"type": "bar"}]]
    )

    fig_remises.add_trace(
        go.Bar(
            x=df_remises['tranche_discount'],
            y=df_remises['ca_total'],
            name='CA',
            marker_color='#3498db',
            text=df_remises['ca_total'].apply(lambda x: f"{x:,.0f}€"),
            textposition='outside'
        ),
        row=1, col=1
    )

    fig_remises.add_trace(
        go.Bar(
            x=df_remises['tranche_discount'],
            y=df_remises['marge_pct'],
            name='Marge %',
            marker_color='#e74c3c',
            text=df_remises['marge_pct'].apply(lambda x: f"{x:.1f}%"),
            textposition='outside'
        ),
        row=1, col=2
    )

    fig_remises.update_layout(height=400, showlegend=False)
    fig_remises.update_xaxes(title_text="Tranche de remise", row=1, col=1)
    fig_remises.update_xaxes(title_text="Tranche de remise", row=1, col=2)
    fig_remises.update_yaxes(title_text="CA (€)", row=1, col=1)
    fig_remises.update_yaxes(title_text="Marge (%)", row=1, col=2)

    st.plotly_chart(fig_remises, use_container_width=True)

    # Tableau détaillé
    with st.expander("📋 Détail par tranche de remise"):
        st.dataframe(
            df_remises[['tranche_discount', 'nb_commandes', 'ca_total', 'profit_total', 'marge_pct', 'ca_moyen']].rename(columns={
                'tranche_discount': 'Tranche',
                'nb_commandes': 'Nb Commandes',
                'ca_total': 'CA (€)',
                'profit_total': 'Profit (€)',
                'marge_pct': 'Marge (%)',
                'ca_moyen': 'CA Moyen (€)'
            }),
            use_container_width=True,
            hide_index=True
        )

    st.markdown(
        """
        <div class="info-card">
            <div class="info-title">Data Storytelling</div>
            L'analyse comparative révèle un paradoxe destructeur : 52,64% du CA (1,2M€) bénéficie de remises, générant une marge négative catastrophique de -2,86%, tandis que les ventes sans remise (1,09M€) affichent une marge saine de 29,51%. Les remises supérieures à 20% créent une destruction massive de valeur avec une marge de -40%, et même les tranches 0-5% et 5-10% dégradent significativement la rentabilité (respectivement 29,5% et 16,6% de marge). Cette politique de remise agressive transforme plus de la moitié du CA en activité déficitaire : chaque euro de remise accordée coûte bien plus qu'il ne rapporte. L'entreprise doit radicalement restreindre les remises, interdire tout discount au-delà de 15%, et former les commerciaux à vendre la valeur plutôt que le prix pour restaurer la rentabilité.
        </div>
        """,
        unsafe_allow_html=True
    )

# --- MARGES INSUFFISANTES ---
with detail_tab3:
    st.markdown("#### 💰 Produits à Marges Insuffisantes")
    st.markdown("*Identification des produits dont le prix de vente est trop proche du coût - Risque de perte en cas de remises ou coûts imprévus*")

    nb_prod_cout = st.slider("Nombre de produits", 10, 50, 30, key="prod_cout")

    cout_prix_data = appeler_api("/kpi/produits/cout-prix", params={'limite': nb_prod_cout})

    # Statistiques
    stats_cout = cout_prix_data['statistiques']
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        st.metric("💰 Prix Unit. Moyen", formater_euro(stats_cout['prix_unitaire_moyen']))
    with col_c2:
        st.metric("📊 Coût Unit. Moyen", formater_euro(stats_cout['cout_unitaire_moyen']))
    with col_c3:
        st.metric("💎 Marge Unit. Moyenne", formater_euro(stats_cout['marge_unitaire_moyenne']))

    df_cout = pd.DataFrame(cout_prix_data['data'])

    # Graphique Prix vs Coût
    fig_cout = go.Figure()

    fig_cout.add_trace(go.Bar(
        name='Prix Unitaire',
        x=df_cout['produit'].str[:30] + '...',
        y=df_cout['prix_unitaire'],
        marker_color='#2ecc71'
    ))

    fig_cout.add_trace(go.Bar(
        name='Coût Unitaire',
        x=df_cout['produit'].str[:30] + '...',
        y=df_cout['cout_unitaire'],
        marker_color='#e74c3c'
    ))

    fig_cout.update_layout(
        title="Prix Unitaire vs Coût Unitaire",
        barmode='group',
        height=500,
        xaxis_tickangle=-45
    )

    st.plotly_chart(fig_cout, use_container_width=True)

    # Tableau détaillé
    with st.expander("📋 Tableau détaillé"):
        st.dataframe(
            df_cout[['produit', 'categorie', 'prix_unitaire', 'cout_unitaire', 'marge_unitaire', 'marge_pct', 'quantite_vendue']].rename(columns={
                'produit': 'Produit',
                'categorie': 'Catégorie',
                'prix_unitaire': 'Prix Unit. (€)',
                'cout_unitaire': 'Coût Unit. (€)',
                'marge_unitaire': 'Marge Unit. (€)',
                'marge_pct': 'Marge (%)',
                'quantite_vendue': 'Qté Vendue'
            }),
            use_container_width=True,
            hide_index=True
        )

    st.markdown(
        """
        <div class="info-card">
            <div class="info-title">Data Storytelling</div>
            Le graphique Prix vs Coût révèle plusieurs produits vendus à perte ou quasi à perte, notamment le Canon imageCLASS (près de 4 000€ de prix pour un coût similaire) et plusieurs systèmes de reliure où le coût dépasse le prix de vente (barres rouges supérieures aux vertes). Ces références toxiques nécessitent une action immédiate : augmentation tarifaire de 15-25%, renégociation des prix d'achat fournisseurs, ou retrait pur et simple du catalogue pour éviter de subventionner les clients avec des produits non rentables.
        </div>
        """,
        unsafe_allow_html=True
    )