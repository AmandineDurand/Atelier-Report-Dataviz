"""
API FastAPI pour l'analyse du dataset Superstore
🎯 Version avancée - Analyses BI professionnelles
📊 KPI e-commerce + Matrices BCG, Waterfall, Analyses temporelles avancées
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
from datetime import datetime
import pandas as pd
import numpy as np
from pydantic import BaseModel
import logging

# Configuration du logger pour faciliter le débogage
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialisation de l'application FastAPI
app = FastAPI(
    title="Superstore BI API - Advanced",
    description="API d'analyse Business Intelligence avancée pour le dataset Superstore",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS pour permettre les appels depuis Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === CHARGEMENT DES DONNÉES ===

DATASET_URL = "https://raw.githubusercontent.com/leonism/sample-superstore/master/data/superstore.csv"

def load_data() -> pd.DataFrame:
    """
    Charge le dataset Superstore depuis GitHub
    Nettoie et prépare les données pour l'analyse
    """
    try:
        logger.info(f"Chargement du dataset depuis {DATASET_URL}")
        
        df = pd.read_csv(DATASET_URL, encoding='latin-1')
        df.columns = df.columns.str.strip()
        df['Order Date'] = pd.to_datetime(df['Order Date'])
        df['Ship Date'] = pd.to_datetime(df['Ship Date'])
        df = df.dropna(subset=['Order ID', 'Customer ID', 'Sales'])
        
        # Ajout de colonnes calculées utiles
        df['Year'] = df['Order Date'].dt.year
        df['Month'] = df['Order Date'].dt.month
        df['YearMonth'] = df['Order Date'].dt.to_period('M').astype(str)
        df['Marge_Pct'] = (df['Profit'] / df['Sales'] * 100).replace([np.inf, -np.inf], 0).fillna(0)
        
        logger.info(f"✅ Dataset chargé : {len(df)} commandes")
        return df
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du chargement des données : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur de chargement : {str(e)}")

# Chargement des données au démarrage
df = load_data()

# === MODÈLES PYDANTIC ===

class KPIGlobaux(BaseModel):
    ca_total: float
    nb_commandes: int
    nb_clients: int
    panier_moyen: float
    quantite_vendue: int
    profit_total: float
    marge_moyenne: float

class ProduitTop(BaseModel):
    produit: str
    categorie: str
    ca: float
    quantite: int
    profit: float

class CategoriePerf(BaseModel):
    categorie: str
    ca: float
    profit: float
    nb_commandes: int
    marge_pct: float

# === FONCTIONS UTILITAIRES ===

def filtrer_dataframe(
    df: pd.DataFrame,
    date_debut: Optional[str] = None,
    date_fin: Optional[str] = None,
    categorie: Optional[str] = None,
    region: Optional[str] = None,
    segment: Optional[str] = None
) -> pd.DataFrame:
    """Applique les filtres sur le dataframe"""
    df_filtered = df.copy()
    
    if date_debut:
        df_filtered = df_filtered[df_filtered['Order Date'] >= date_debut]
    if date_fin:
        df_filtered = df_filtered[df_filtered['Order Date'] <= date_fin]
    if categorie and categorie != "Toutes":
        df_filtered = df_filtered[df_filtered['Category'] == categorie]
    if region and region != "Toutes":
        df_filtered = df_filtered[df_filtered['Region'] == region]
    if segment and segment != "Tous":
        df_filtered = df_filtered[df_filtered['Segment'] == segment]
    
    return df_filtered

# === ENDPOINTS EXISTANTS ===

@app.get("/", tags=["Info"])
def root():
    """Endpoint racine - Informations sur l'API"""
    return {
        "message": "🛒 API Superstore BI - Advanced",
        "version": "2.0.0",
        "dataset": "Sample Superstore",
        "nb_lignes": len(df),
        "periode": {
            "debut": df['Order Date'].min().strftime('%Y-%m-%d'),
            "fin": df['Order Date'].max().strftime('%Y-%m-%d')
        },
        "endpoints": {
            "documentation": "/docs",
            "kpi_globaux": "/kpi/globaux",
            "top_produits": "/kpi/produits/top",
            "bcg_matrix": "/kpi/produits/bcg",
            "faible_marge": "/kpi/produits/faible-marge",
            "categories": "/kpi/categories",
            "categories_waterfall": "/kpi/categories/waterfall",
            "categories_matrix": "/kpi/categories/matrix",
            "evolution_temporelle": "/kpi/temporel",
            "temporel_avance": "/kpi/temporel/avance",
            "performance_geo": "/kpi/geographique",
            "geo_etats": "/kpi/geographique/etats",
            "geo_villes": "/kpi/geographique/villes",
            "analyse_clients": "/kpi/clients"
        }
    }

@app.get("/kpi/globaux", response_model=KPIGlobaux, tags=["KPI"])
def get_kpi_globaux(
    date_debut: Optional[str] = Query(None, description="Date début (YYYY-MM-DD)"),
    date_fin: Optional[str] = Query(None, description="Date fin (YYYY-MM-DD)"),
    categorie: Optional[str] = Query(None, description="Catégorie produit"),
    region: Optional[str] = Query(None, description="Région"),
    segment: Optional[str] = Query(None, description="Segment client")
):
    """📊 KPI GLOBAUX"""
    df_filtered = filtrer_dataframe(df, date_debut, date_fin, categorie, region, segment)
    
    ca_total = df_filtered['Sales'].sum()
    nb_commandes = df_filtered['Order ID'].nunique()
    nb_clients = df_filtered['Customer ID'].nunique()
    panier_moyen = ca_total / nb_commandes if nb_commandes > 0 else 0
    quantite_vendue = int(df_filtered['Quantity'].sum())
    profit_total = df_filtered['Profit'].sum()
    marge_moyenne = (profit_total / ca_total * 100) if ca_total > 0 else 0
    
    return KPIGlobaux(
        ca_total=round(ca_total, 2),
        nb_commandes=nb_commandes,
        nb_clients=nb_clients,
        panier_moyen=round(panier_moyen, 2),
        quantite_vendue=quantite_vendue,
        profit_total=round(profit_total, 2),
        marge_moyenne=round(marge_moyenne, 2)
    )

@app.get("/kpi/produits/top", tags=["KPI"])
def get_top_produits(
    limite: int = Query(10, ge=1, le=50, description="Nombre de produits à retourner"),
    tri_par: str = Query("ca", regex="^(ca|profit|quantite)$", description="Critère de tri")
):
    """🏆 TOP PRODUITS"""
    produits = df.groupby(['Product Name', 'Category']).agg({
        'Sales': 'sum',
        'Quantity': 'sum',
        'Profit': 'sum'
    }).reset_index()
    
    if tri_par == "ca":
        produits = produits.sort_values('Sales', ascending=False)
    elif tri_par == "profit":
        produits = produits.sort_values('Profit', ascending=False)
    else:
        produits = produits.sort_values('Quantity', ascending=False)
    
    top = produits.head(limite)
    
    result = []
    for _, row in top.iterrows():
        result.append({
            "produit": row['Product Name'],
            "categorie": row['Category'],
            "ca": round(row['Sales'], 2),
            "quantite": int(row['Quantity']),
            "profit": round(row['Profit'], 2)
        })
    
    return result

# === NOUVEAUX ENDPOINTS - TAB 1 : PRODUITS AVANCÉS ===

@app.get("/kpi/produits/bcg", tags=["KPI Avancés - Produits"])
def get_bcg_matrix(limite: int = Query(50, ge=10, le=200)):
    """
    📊 MATRICE BCG
    
    Calcule la position BCG de chaque produit :
    - Axe X : Part de marché (% du CA total)
    - Axe Y : Croissance YoY
    - Quadrants : Étoiles, Vaches à lait, Dilemmes, Poids morts
    """
    # Obtenir les années disponibles
    years = sorted(df['Year'].unique())
    
    if len(years) < 2:
        # Pas assez de données pour calculer la croissance
        return {"error": "Pas assez d'années pour calculer la croissance", "data": []}
    
    last_year = years[-1]
    prev_year = years[-2]
    
    # CA par produit et par année
    ca_by_year = df.groupby(['Product Name', 'Category', 'Sub-Category', 'Year']).agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Quantity': 'sum'
    }).reset_index()
    
    # Pivot pour avoir les années en colonnes
    ca_pivot = ca_by_year.pivot_table(
        index=['Product Name', 'Category', 'Sub-Category'],
        columns='Year',
        values=['Sales', 'Profit', 'Quantity'],
        fill_value=0
    ).reset_index()
    
    ca_pivot.columns = ['_'.join(map(str, col)).strip('_') for col in ca_pivot.columns]
    
    # CA total pour calculer la part de marché
    ca_total = df['Sales'].sum()
    ca_total_last_year = df[df['Year'] == last_year]['Sales'].sum()
    
    result = []
    for _, row in ca_pivot.iterrows():
        ca_last = row.get(f'Sales_{last_year}', 0)
        ca_prev = row.get(f'Sales_{prev_year}', 0)
        profit_last = row.get(f'Profit_{last_year}', 0)
        qty_last = row.get(f'Quantity_{last_year}', 0)
        
        # Calcul de la croissance (éviter division par zéro)
        if ca_prev > 0:
            croissance = ((ca_last - ca_prev) / ca_prev) * 100
        elif ca_last > 0:
            croissance = 100  # Nouveau produit
        else:
            croissance = 0
        
        # Part de marché (sur dernière année)
        part_marche = (ca_last / ca_total_last_year * 100) if ca_total_last_year > 0 else 0
        
        # Marge
        marge = (profit_last / ca_last * 100) if ca_last > 0 else 0
        
        # Rotation des stocks (proxy)
        rotation = qty_last / ca_last * 1000 if ca_last > 0 else 0
        
        # Classification BCG
        # Médiane de la part de marché et croissance pour les seuils
        quadrant = ""
        if part_marche >= 0.5 and croissance >= 10:
            quadrant = "Étoile ⭐"
        elif part_marche >= 0.5 and croissance < 10:
            quadrant = "Vache à lait 🐄"
        elif part_marche < 0.5 and croissance >= 10:
            quadrant = "Dilemme ❓"
        else:
            quadrant = "Poids mort 💀"
        
        result.append({
            "produit": row['Product Name'],
            "categorie": row['Category'],
            "sous_categorie": row['Sub-Category'],
            "ca_actuel": round(ca_last, 2),
            "ca_precedent": round(ca_prev, 2),
            "part_marche": round(part_marche, 4),
            "croissance": round(croissance, 2),
            "profit": round(profit_last, 2),
            "marge_pct": round(marge, 2),
            "rotation": round(rotation, 4),
            "quadrant": quadrant
        })
    
    # Trier par CA décroissant et limiter
    result = sorted(result, key=lambda x: x['ca_actuel'], reverse=True)[:limite]
    
    # Statistiques globales pour les seuils
    parts = [r['part_marche'] for r in result if r['ca_actuel'] > 0]
    croissances = [r['croissance'] for r in result if r['ca_actuel'] > 0]
    
    return {
        "data": result,
        "seuils": {
            "part_marche_mediane": round(np.median(parts), 4) if parts else 0,
            "croissance_mediane": round(np.median(croissances), 2) if croissances else 0,
            "annee_actuelle": int(last_year),
            "annee_precedente": int(prev_year)
        },
        "repartition": {
            "etoiles": len([r for r in result if "Étoile" in r['quadrant']]),
            "vaches": len([r for r in result if "Vache" in r['quadrant']]),
            "dilemmes": len([r for r in result if "Dilemme" in r['quadrant']]),
            "poids_morts": len([r for r in result if "Poids mort" in r['quadrant']])
        }
    }

@app.get("/kpi/produits/faible-marge", tags=["KPI Avancés - Produits"])
def get_produits_faible_marge(
    seuil_marge: float = Query(5.0, description="Seuil de marge (%) en dessous duquel un produit est considéré à faible marge"),
    limite: int = Query(20, ge=5, le=100)
):
    """
    ⚠️ PRODUITS À FAIBLE MARGE
    
    Identifie les produits qui vendent mais ne rapportent pas :
    - Marge < seuil défini
    - Triés par CA décroissant (impact business)
    """
    produits = df.groupby(['Product Name', 'Category', 'Sub-Category']).agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Quantity': 'sum',
        'Discount': 'mean'
    }).reset_index()
    
    produits['marge_pct'] = (produits['Profit'] / produits['Sales'] * 100).replace([np.inf, -np.inf], 0).fillna(0)
    produits['rotation'] = (produits['Quantity'] / produits['Sales'] * 1000).replace([np.inf, -np.inf], 0).fillna(0)
    
    # Filtrer les produits à faible marge
    faible_marge = produits[produits['marge_pct'] < seuil_marge].copy()
    faible_marge = faible_marge.sort_values('Sales', ascending=False).head(limite)
    
    result = []
    for _, row in faible_marge.iterrows():
        result.append({
            "produit": row['Product Name'],
            "categorie": row['Category'],
            "sous_categorie": row['Sub-Category'],
            "ca": round(row['Sales'], 2),
            "profit": round(row['Profit'], 2),
            "marge_pct": round(row['marge_pct'], 2),
            "quantite": int(row['Quantity']),
            "discount_moyen": round(row['Discount'] * 100, 2),
            "rotation": round(row['rotation'], 4),
            "alerte": "🔴 Perte" if row['Profit'] < 0 else "🟠 Faible"
        })
    
    # Statistiques
    total_ca_faible = faible_marge['Sales'].sum()
    total_profit_faible = faible_marge['Profit'].sum()
    
    return {
        "data": result,
        "statistiques": {
            "nb_produits_faible_marge": len(faible_marge),
            "ca_total_faible_marge": round(total_ca_faible, 2),
            "profit_total_faible_marge": round(total_profit_faible, 2),
            "pct_ca_total": round(total_ca_faible / df['Sales'].sum() * 100, 2),
            "nb_produits_perte": len(faible_marge[faible_marge['Profit'] < 0]),
            "seuil_utilise": seuil_marge
        }
    }

# === NOUVEAUX ENDPOINTS - TAB 2 : CATÉGORIES AVANCÉES ===

@app.get("/kpi/categories", tags=["KPI"])
def get_performance_categories():
    """📦 PERFORMANCE PAR CATÉGORIE"""
    categories = df.groupby('Category').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Order ID': 'nunique'
    }).reset_index()
    
    categories['marge_pct'] = (categories['Profit'] / categories['Sales'] * 100).round(2)
    categories.columns = ['categorie', 'ca', 'profit', 'nb_commandes', 'marge_pct']
    categories = categories.sort_values('ca', ascending=False)
    
    return categories.to_dict('records')

@app.get("/kpi/categories/waterfall", tags=["KPI Avancés - Catégories"])
def get_categories_waterfall():
    """
    📊 WATERFALL PROFIT PAR CATÉGORIE
    
    Graphique en cascade montrant la contribution de chaque catégorie
    et sous-catégorie au profit total
    """
    # Agrégation par catégorie
    cat_profit = df.groupby('Category').agg({
        'Profit': 'sum',
        'Sales': 'sum'
    }).reset_index()
    cat_profit = cat_profit.sort_values('Profit', ascending=False)
    
    # Agrégation par sous-catégorie
    subcat_profit = df.groupby(['Category', 'Sub-Category']).agg({
        'Profit': 'sum',
        'Sales': 'sum'
    }).reset_index()
    subcat_profit = subcat_profit.sort_values('Profit', ascending=False)
    
    # Préparation des données waterfall
    waterfall_data = []
    cumul = 0
    
    for _, row in cat_profit.iterrows():
        waterfall_data.append({
            "label": row['Category'],
            "value": round(row['Profit'], 2),
            "cumul": round(cumul + row['Profit'], 2),
            "type": "category",
            "ca": round(row['Sales'], 2),
            "marge_pct": round(row['Profit'] / row['Sales'] * 100, 2) if row['Sales'] > 0 else 0
        })
        cumul += row['Profit']
    
    # Détail par sous-catégorie
    subcat_detail = []
    for _, row in subcat_profit.iterrows():
        subcat_detail.append({
            "categorie": row['Category'],
            "sous_categorie": row['Sub-Category'],
            "profit": round(row['Profit'], 2),
            "ca": round(row['Sales'], 2),
            "marge_pct": round(row['Profit'] / row['Sales'] * 100, 2) if row['Sales'] > 0 else 0,
            "contribution_pct": round(row['Profit'] / df['Profit'].sum() * 100, 2)
        })
    
    return {
        "waterfall": waterfall_data,
        "detail_sous_categories": subcat_detail,
        "profit_total": round(df['Profit'].sum(), 2),
        "ca_total": round(df['Sales'].sum(), 2)
    }

@app.get("/kpi/categories/matrix", tags=["KPI Avancés - Catégories"])
def get_categories_matrix():
    """
    📊 MATRICE PERFORMANCE/MARGE
    
    Quadrants :
    - Q1 (↗) : CA élevé + Marge élevée → Priorité
    - Q2 (↘) : CA élevé + Marge faible → À optimiser  
    - Q3 (↖) : CA faible + Marge élevée → À développer
    - Q4 (↙) : CA faible + Marge faible → À abandonner
    """
    # Agrégation par sous-catégorie
    subcats = df.groupby(['Category', 'Sub-Category']).agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Quantity': 'sum',
        'Order ID': 'nunique'
    }).reset_index()
    
    subcats['marge_pct'] = (subcats['Profit'] / subcats['Sales'] * 100).replace([np.inf, -np.inf], 0).fillna(0)
    
    # Calcul des seuils (médianes)
    ca_median = subcats['Sales'].median()
    marge_median = subcats['marge_pct'].median()
    
    result = []
    for _, row in subcats.iterrows():
        ca = row['Sales']
        marge = row['marge_pct']
        
        # Classification en quadrant
        if ca >= ca_median and marge >= marge_median:
            quadrant = "Q1 - Priorité 🌟"
            action = "Investir et développer"
        elif ca >= ca_median and marge < marge_median:
            quadrant = "Q2 - À optimiser ⚙️"
            action = "Réduire coûts/discounts"
        elif ca < ca_median and marge >= marge_median:
            quadrant = "Q3 - À développer 📈"
            action = "Augmenter visibilité"
        else:
            quadrant = "Q4 - À abandonner ❌"
            action = "Réduire ou arrêter"
        
        result.append({
            "categorie": row['Category'],
            "sous_categorie": row['Sub-Category'],
            "ca": round(ca, 2),
            "profit": round(row['Profit'], 2),
            "marge_pct": round(marge, 2),
            "quantite": int(row['Quantity']),
            "nb_commandes": int(row['Order ID']),
            "quadrant": quadrant,
            "action_recommandee": action
        })
    
    # Tri par CA
    result = sorted(result, key=lambda x: x['ca'], reverse=True)
    
    return {
        "data": result,
        "seuils": {
            "ca_median": round(ca_median, 2),
            "marge_median": round(marge_median, 2)
        },
        "repartition": {
            "Q1_priorite": len([r for r in result if "Q1" in r['quadrant']]),
            "Q2_optimiser": len([r for r in result if "Q2" in r['quadrant']]),
            "Q3_developper": len([r for r in result if "Q3" in r['quadrant']]),
            "Q4_abandonner": len([r for r in result if "Q4" in r['quadrant']])
        }
    }

# === NOUVEAUX ENDPOINTS - TAB 3 : TEMPOREL AVANCÉ ===

@app.get("/kpi/temporel", tags=["KPI"])
def get_evolution_temporelle(
    periode: str = Query('mois', regex='^(jour|mois|annee)$', description="Granularité temporelle")
):
    """📈 ÉVOLUTION TEMPORELLE"""
    df_temp = df.copy()
    
    if periode == 'jour':
        df_temp['periode'] = df_temp['Order Date'].dt.strftime('%Y-%m-%d')
    elif periode == 'mois':
        df_temp['periode'] = df_temp['Order Date'].dt.strftime('%Y-%m')
    else:
        df_temp['periode'] = df_temp['Order Date'].dt.strftime('%Y')
    
    temporal = df_temp.groupby('periode').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Order ID': 'nunique',
        'Quantity': 'sum'
    }).reset_index()
    
    temporal.columns = ['periode', 'ca', 'profit', 'nb_commandes', 'quantite']
    temporal = temporal.sort_values('periode')
    
    return temporal.to_dict('records')

@app.get("/kpi/temporel/avance", tags=["KPI Avancés - Temporel"])
def get_temporel_avance():
    """
    📈 ANALYSE TEMPORELLE AVANCÉE
    
    Inclut :
    - Moyenne mobile (3 mois)
    - Comparaison N vs N-1
    - Taux de croissance période par période
    """
    # Agrégation mensuelle
    df_temp = df.copy()
    df_temp['periode'] = df_temp['Order Date'].dt.to_period('M')
    df_temp['year'] = df_temp['Order Date'].dt.year
    df_temp['month'] = df_temp['Order Date'].dt.month
    
    monthly = df_temp.groupby(['periode', 'year', 'month']).agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Order ID': 'nunique',
        'Quantity': 'sum'
    }).reset_index()
    
    monthly = monthly.sort_values('periode')
    monthly['periode_str'] = monthly['periode'].astype(str)
    
    # Moyenne mobile 3 mois
    monthly['ca_mm3'] = monthly['Sales'].rolling(window=3, min_periods=1).mean()
    monthly['profit_mm3'] = monthly['Profit'].rolling(window=3, min_periods=1).mean()
    
    # Croissance période par période
    monthly['ca_prev'] = monthly['Sales'].shift(1)
    monthly['croissance_pct'] = ((monthly['Sales'] - monthly['ca_prev']) / monthly['ca_prev'] * 100).replace([np.inf, -np.inf], 0).fillna(0)
    
    # Préparation des données avec comparaison N-1
    years = sorted(monthly['year'].unique())
    
    result = []
    for _, row in monthly.iterrows():
        # Recherche de la même période l'année précédente
        prev_year_data = monthly[(monthly['year'] == row['year'] - 1) & (monthly['month'] == row['month'])]
        ca_n1 = prev_year_data['Sales'].values[0] if len(prev_year_data) > 0 else None
        profit_n1 = prev_year_data['Profit'].values[0] if len(prev_year_data) > 0 else None
        
        # Calcul variation YoY
        variation_yoy = None
        if ca_n1 is not None and ca_n1 > 0:
            variation_yoy = round((row['Sales'] - ca_n1) / ca_n1 * 100, 2)
        
        result.append({
            "periode": row['periode_str'],
            "year": int(row['year']),
            "month": int(row['month']),
            "ca": round(row['Sales'], 2),
            "profit": round(row['Profit'], 2),
            "nb_commandes": int(row['Order ID']),
            "quantite": int(row['Quantity']),
            "ca_mm3": round(row['ca_mm3'], 2),
            "profit_mm3": round(row['profit_mm3'], 2),
            "croissance_pct": round(row['croissance_pct'], 2),
            "ca_n1": round(ca_n1, 2) if ca_n1 is not None else None,
            "profit_n1": round(profit_n1, 2) if profit_n1 is not None else None,
            "variation_yoy": variation_yoy
        })
    
    return {
        "data": result,
        "annees_disponibles": [int(y) for y in years],
        "statistiques": {
            "ca_moyen_mensuel": round(monthly['Sales'].mean(), 2),
            "croissance_moyenne": round(monthly['croissance_pct'].mean(), 2),
            "meilleur_mois": monthly.loc[monthly['Sales'].idxmax(), 'periode_str'],
            "pire_mois": monthly.loc[monthly['Sales'].idxmin(), 'periode_str']
        }
    }

# === NOUVEAUX ENDPOINTS - TAB 4 : GÉOGRAPHIQUE AVANCÉ ===

@app.get("/kpi/geographique", tags=["KPI"])
def get_performance_geographique():
    """🌍 PERFORMANCE GÉOGRAPHIQUE"""
    geo = df.groupby('Region').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Customer ID': 'nunique',
        'Order ID': 'nunique'
    }).reset_index()
    
    geo.columns = ['region', 'ca', 'profit', 'nb_clients', 'nb_commandes']
    geo = geo.sort_values('ca', ascending=False)
    
    return geo.to_dict('records')

@app.get("/kpi/geographique/etats", tags=["KPI Avancés - Géographique"])
def get_performance_etats():
    """
    🗺️ PERFORMANCE PAR ÉTAT (HEATMAP)
    
    Performance détaillée par État avec marge et CA/client
    """
    states = df.groupby(['State', 'Region']).agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Customer ID': 'nunique',
        'Order ID': 'nunique',
        'Quantity': 'sum'
    }).reset_index()
    
    states['marge_pct'] = (states['Profit'] / states['Sales'] * 100).replace([np.inf, -np.inf], 0).fillna(0)
    states['ca_par_client'] = (states['Sales'] / states['Customer ID']).replace([np.inf, -np.inf], 0).fillna(0)
    states['commandes_par_client'] = (states['Order ID'] / states['Customer ID']).replace([np.inf, -np.inf], 0).fillna(0)
    
    # Classification par performance
    marge_median = states['marge_pct'].median()
    ca_median = states['Sales'].median()
    
    result = []
    for _, row in states.iterrows():
        # Classification
        if row['marge_pct'] >= marge_median and row['Sales'] >= ca_median:
            perf_class = "Haute performance 🟢"
        elif row['marge_pct'] >= marge_median:
            perf_class = "Bonne marge 🟡"
        elif row['Sales'] >= ca_median:
            perf_class = "Volume élevé 🟠"
        else:
            perf_class = "À développer 🔴"
        
        result.append({
            "etat": row['State'],
            "region": row['Region'],
            "ca": round(row['Sales'], 2),
            "profit": round(row['Profit'], 2),
            "marge_pct": round(row['marge_pct'], 2),
            "nb_clients": int(row['Customer ID']),
            "nb_commandes": int(row['Order ID']),
            "ca_par_client": round(row['ca_par_client'], 2),
            "commandes_par_client": round(row['commandes_par_client'], 2),
            "quantite": int(row['Quantity']),
            "performance": perf_class
        })
    
    result = sorted(result, key=lambda x: x['ca'], reverse=True)
    
    return {
        "data": result,
        "seuils": {
            "marge_median": round(marge_median, 2),
            "ca_median": round(ca_median, 2)
        }
    }

@app.get("/kpi/geographique/villes", tags=["KPI Avancés - Géographique"])
def get_top_villes(limite: int = Query(20, ge=5, le=100)):
    """
    🏙️ TOP VILLES
    
    Classement des villes les plus performantes
    """
    cities = df.groupby(['City', 'State', 'Region']).agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Customer ID': 'nunique',
        'Order ID': 'nunique'
    }).reset_index()
    
    cities['marge_pct'] = (cities['Profit'] / cities['Sales'] * 100).replace([np.inf, -np.inf], 0).fillna(0)
    cities['ca_par_client'] = (cities['Sales'] / cities['Customer ID']).replace([np.inf, -np.inf], 0).fillna(0)
    
    # Top par CA
    top_ca = cities.nlargest(limite, 'Sales')

    result_ca = []
    for _, row in top_ca.iterrows():
        result_ca.append({
            "ville": row['City'],
            "etat": row['State'],
            "region": row['Region'],
            "ca": round(row['Sales'], 2),
            "profit": round(row['Profit'], 2),
            "marge_pct": round(row['marge_pct'], 2),
            "nb_clients": int(row['Customer ID']),
            "ca_par_client": round(row['ca_par_client'], 2)
        })

    return {
        "top_ca": result_ca,
        "statistiques": {
            "nb_villes_total": len(cities),
            "ca_moyen_ville": round(cities['Sales'].mean(), 2),
            "clients_moyen_ville": round(cities['Customer ID'].mean(), 2)
        }
    }

# === ENDPOINT CLIENTS ===

@app.get("/kpi/clients", tags=["KPI"])
def get_analyse_clients(
    limite: int = Query(10, ge=1, le=100, description="Nombre de top clients")
):
    """👥 ANALYSE CLIENTS"""
    clients = df.groupby('Customer ID').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Order ID': 'nunique',
        'Customer Name': 'first'
    }).reset_index()
    
    clients.columns = ['customer_id', 'ca_total', 'profit_total', 'nb_commandes', 'nom']
    clients['valeur_commande_moy'] = (clients['ca_total'] / clients['nb_commandes']).round(2)
    
    top_clients = clients.sort_values('ca_total', ascending=False).head(limite)
    
    recurrence = {
        "clients_1_achat": len(clients[clients['nb_commandes'] == 1]),
        "clients_recurrents": len(clients[clients['nb_commandes'] > 1]),
        "nb_commandes_moyen": round(clients['nb_commandes'].mean(), 2),
        "total_clients": len(clients)
    }
    
    segments = df.groupby('Segment').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Customer ID': 'nunique'
    }).reset_index()
    segments.columns = ['segment', 'ca', 'profit', 'nb_clients']
    
    return {
        "top_clients": top_clients.to_dict('records'),
        "recurrence": recurrence,
        "segments": segments.to_dict('records')
    }

@app.get("/filters/valeurs", tags=["Filtres"])
def get_valeurs_filtres():
    """🎯 VALEURS POUR LES FILTRES"""
    return {
        "categories": sorted(df['Category'].unique().tolist()),
        "regions": sorted(df['Region'].unique().tolist()),
        "segments": sorted(df['Segment'].unique().tolist()),
        "etats": sorted(df['State'].unique().tolist()),
        "plage_dates": {
            "min": df['Order Date'].min().strftime('%Y-%m-%d'),
            "max": df['Order Date'].max().strftime('%Y-%m-%d')
        }
    }

@app.get("/data/commandes", tags=["Données brutes"])
def get_commandes(
    limite: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """📋 DONNÉES BRUTES"""
    total = len(df)
    commandes = df.iloc[offset:offset+limite]
    
    commandes_dict = commandes.copy()
    commandes_dict['Order Date'] = commandes_dict['Order Date'].dt.strftime('%Y-%m-%d')
    commandes_dict['Ship Date'] = commandes_dict['Ship Date'].dt.strftime('%Y-%m-%d')
    
    return {
        "total": total,
        "limite": limite,
        "offset": offset,
        "data": commandes_dict.to_dict('records')
    }

# === DÉMARRAGE DU SERVEUR ===

if __name__ == "__main__":
    import uvicorn
    print("🚀 Démarrage de l'API Superstore BI Advanced sur http://localhost:8000")
    print("📚 Documentation disponible sur http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
