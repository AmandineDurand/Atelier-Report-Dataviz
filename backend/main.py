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
    marge_brute_par_commande: float

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
    marge_brute_par_commande = profit_total / nb_commandes if nb_commandes > 0 else 0

    return KPIGlobaux(
        ca_total=round(ca_total, 2),
        nb_commandes=nb_commandes,
        nb_clients=nb_clients,
        panier_moyen=round(panier_moyen, 2),
        quantite_vendue=quantite_vendue,
        profit_total=round(profit_total, 2),
        marge_moyenne=round(marge_moyenne, 2),
        marge_brute_par_commande=round(marge_brute_par_commande, 2)
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

# === ENDPOINTS CLIENTS AVANCÉS ===

@app.get("/kpi/clients/rfm", tags=["KPI Avancés - Clients"])
def get_segmentation_rfm():
    """
    📊 SEGMENTATION RFM (Recency, Frequency, Monetary)

    Segmentation client basée sur:
    - R: Récence du dernier achat
    - F: Fréquence d'achat
    - M: Montant total dépensé
    """
    # Date de référence (dernière date du dataset)
    date_reference = df['Order Date'].max()

    # Calcul RFM par client
    rfm = df.groupby('Customer ID').agg({
        'Order Date': lambda x: (date_reference - x.max()).days,  # Recency
        'Order ID': 'nunique',  # Frequency
        'Sales': 'sum'  # Monetary
    }).reset_index()

    rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']

    # Ajout du nom client
    client_names = df.groupby('Customer ID')['Customer Name'].first().reset_index()
    rfm = rfm.merge(client_names, left_on='customer_id', right_on='Customer ID', how='left')
    rfm = rfm.drop('Customer ID', axis=1)

    # Calcul des scores RFM (quintiles inversés pour R, normaux pour F et M)
    rfm['r_score'] = pd.qcut(rfm['recency'], q=5, labels=[5, 4, 3, 2, 1], duplicates='drop')
    rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')
    rfm['m_score'] = pd.qcut(rfm['monetary'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')

    # Score RFM global
    rfm['rfm_score'] = rfm['r_score'].astype(str) + rfm['f_score'].astype(str) + rfm['m_score'].astype(str)
    rfm['rfm_score_value'] = rfm['r_score'].astype(int) + rfm['f_score'].astype(int) + rfm['m_score'].astype(int)

    # Segmentation client
    def segment_client(row):
        r, f, m = int(row['r_score']), int(row['f_score']), int(row['m_score'])

        if r >= 4 and f >= 4 and m >= 4:
            return "Champions 🏆"
        elif r >= 3 and f >= 3 and m >= 3:
            return "Fidèles 💎"
        elif r >= 4 and f <= 2:
            return "Nouveaux 🌱"
        elif r <= 2 and f >= 3:
            return "À risque ⚠️"
        elif r <= 2 and f <= 2:
            return "Perdus 💔"
        elif m >= 4:
            return "Gros dépensiers 💰"
        else:
            return "Occasionnels 📊"

    rfm['segment'] = rfm.apply(segment_client, axis=1)

    # Statistiques par segment
    segment_stats = rfm.groupby('segment').agg({
        'customer_id': 'count',
        'recency': 'mean',
        'frequency': 'mean',
        'monetary': ['mean', 'sum']
    }).reset_index()

    segment_stats.columns = ['segment', 'nb_clients', 'recency_moy', 'frequency_moy', 'monetary_moy', 'ca_total']
    segment_stats['pct_clients'] = (segment_stats['nb_clients'] / len(rfm) * 100).round(2)

    # Top clients
    top_clients_rfm = rfm.nlargest(20, 'rfm_score_value')

    result_clients = []
    for _, row in top_clients_rfm.iterrows():
        result_clients.append({
            "client": row['Customer Name'],
            "recency": int(row['recency']),
            "frequency": int(row['frequency']),
            "monetary": round(row['monetary'], 2),
            "rfm_score": row['rfm_score'],
            "segment": row['segment']
        })

    return {
        "top_clients": result_clients,
        "segments": segment_stats.to_dict('records'),
        "statistiques": {
            "nb_total_clients": len(rfm),
            "recency_moyenne": round(rfm['recency'].mean(), 1),
            "frequency_moyenne": round(rfm['frequency'].mean(), 2),
            "monetary_moyenne": round(rfm['monetary'].mean(), 2)
        }
    }

@app.get("/kpi/clients/delai-rachat", tags=["KPI Avancés - Clients"])
def get_delai_rachat():
    """
    🔄 DÉLAI MOYEN DE RÉACHAT

    Analyse du temps moyen entre deux achats par client
    """
    try:
        # Tri par client et date - on doit dédupliquer les commandes du même jour
        df_temp = df[['Customer ID', 'Order Date', 'Segment', 'Order ID']].copy()

        # Garder une seule ligne par client et par date (certains clients peuvent avoir plusieurs commandes le même jour)
        df_temp = df_temp.sort_values(['Customer ID', 'Order Date', 'Order ID']).drop_duplicates(
            subset=['Customer ID', 'Order Date'],
            keep='first'
        )

        df_sorted = df_temp[['Customer ID', 'Order Date', 'Segment']].sort_values(['Customer ID', 'Order Date']).copy()

        # Calcul du délai entre achats
        df_sorted['prev_order_date'] = df_sorted.groupby('Customer ID')['Order Date'].shift(1)
        df_sorted['days_since_last_order'] = (df_sorted['Order Date'] - df_sorted['prev_order_date']).dt.days

        # Clients avec au moins 2 achats (exclure les délais de 0 jour qui sont des commandes multiples le même jour)
        delais = df_sorted[
            (df_sorted['days_since_last_order'].notna()) &
            (df_sorted['days_since_last_order'] > 0)
        ].copy()

        logger.info(f"📊 Délai de réachat - {len(delais)} rachats trouvés")

        if len(delais) == 0:
            logger.warning("⚠️ Aucun rachat trouvé")
            return {
                "statistiques": {
                    "delai_moyen_jours": 0,
                    "delai_median_jours": 0,
                    "nb_rachats_total": 0
                },
                "par_segment": [],
                "distribution": {}
            }

        # Statistiques globales
        delai_moyen = delais['days_since_last_order'].mean()
        delai_median = delais['days_since_last_order'].median()

        logger.info(f"📈 Délai moyen: {delai_moyen:.1f}j, médian: {delai_median:.1f}j")

        # Par segment
        segment_delais = delais.groupby('Segment').agg({
            'days_since_last_order': ['mean', 'median', 'count']
        }).reset_index()

        segment_delais.columns = ['segment', 'delai_moyen', 'delai_median', 'nb_rachats']

        # Distribution des délais
        delai_bins = pd.cut(
            delais['days_since_last_order'],
            bins=[0, 30, 60, 90, 180, 365, 999999],
            labels=['<30j', '30-60j', '60-90j', '90-180j', '180-365j', '>365j']
        )

        distribution = delai_bins.value_counts().sort_index()

        return {
            "statistiques": {
                "delai_moyen_jours": round(delai_moyen, 1) if not pd.isna(delai_moyen) else 0,
                "delai_median_jours": round(delai_median, 1) if not pd.isna(delai_median) else 0,
                "nb_rachats_total": len(delais)
            },
            "par_segment": segment_delais.to_dict('records'),
            "distribution": {str(k): int(v) for k, v in distribution.items()}
        }
    except Exception as e:
        logger.error(f"❌ Erreur dans get_delai_rachat : {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erreur lors du calcul du délai de réachat : {str(e)}")

@app.get("/kpi/clients/clv", tags=["KPI Avancés - Clients"])
def get_customer_lifetime_value(limite: int = Query(50, ge=10, le=200)):
    """
    💰 CUSTOMER LIFETIME VALUE (CLV)

    Valeur vie client avec projections
    """
    # Calculs par client
    clients_clv = df.groupby('Customer ID').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Order ID': 'nunique',
        'Order Date': ['min', 'max'],
        'Customer Name': 'first'
    }).reset_index()

    clients_clv.columns = ['customer_id', 'ca_total', 'profit_total', 'nb_commandes', 'first_order', 'last_order', 'nom']

    # Durée de vie client (en jours)
    clients_clv['lifetime_days'] = (clients_clv['last_order'] - clients_clv['first_order']).dt.days
    clients_clv['lifetime_days'] = clients_clv['lifetime_days'].replace(0, 1)  # Éviter division par 0

    # Calculs CLV
    clients_clv['ca_moyen_commande'] = clients_clv['ca_total'] / clients_clv['nb_commandes']
    clients_clv['frequence_achat_annuelle'] = clients_clv['nb_commandes'] / (clients_clv['lifetime_days'] / 365)
    clients_clv['ca_annuel'] = clients_clv['ca_total'] / (clients_clv['lifetime_days'] / 365)

    # CLV projetée sur 3 ans (simple)
    clients_clv['clv_3_ans'] = clients_clv['ca_annuel'] * 3
    clients_clv['profit_annuel'] = clients_clv['profit_total'] / (clients_clv['lifetime_days'] / 365)
    clients_clv['profit_clv_3_ans'] = clients_clv['profit_annuel'] * 3

    # Classification
    clv_median = clients_clv['clv_3_ans'].median()

    def classify_clv(clv_value):
        if clv_value >= clv_median * 2:
            return "Très élevée 🌟"
        elif clv_value >= clv_median:
            return "Élevée 💎"
        elif clv_value >= clv_median * 0.5:
            return "Moyenne 📊"
        else:
            return "Faible 📉"

    clients_clv['categorie_clv'] = clients_clv['clv_3_ans'].apply(classify_clv)

    # Top clients par CLV
    top_clv = clients_clv.nlargest(limite, 'clv_3_ans')

    result = []
    for _, row in top_clv.iterrows():
        result.append({
            "client": row['nom'],
            "ca_total": round(row['ca_total'], 2),
            "nb_commandes": int(row['nb_commandes']),
            "ca_annuel": round(row['ca_annuel'], 2),
            "clv_3_ans": round(row['clv_3_ans'], 2),
            "profit_clv_3_ans": round(row['profit_clv_3_ans'], 2),
            "categorie": row['categorie_clv'],
            "lifetime_days": int(row['lifetime_days'])
        })

    # Statistiques par catégorie
    cat_stats = clients_clv.groupby('categorie_clv').agg({
        'customer_id': 'count',
        'clv_3_ans': 'sum',
        'profit_clv_3_ans': 'sum'
    }).reset_index()
    cat_stats.columns = ['categorie', 'nb_clients', 'clv_total', 'profit_total']

    return {
        "top_clients": result,
        "statistiques": {
            "clv_moyenne": round(clients_clv['clv_3_ans'].mean(), 2),
            "clv_mediane": round(clv_median, 2),
            "ca_annuel_moyen": round(clients_clv['ca_annuel'].mean(), 2)
        },
        "par_categorie": cat_stats.to_dict('records')
    }

@app.get("/kpi/clients/retention", tags=["KPI Avancés - Clients"])
def get_taux_retention():
    """
    📈 TAUX DE RÉTENTION (COHORT)

    Analyse de la rétention client par cohorte (mois de première commande)
    """
    # Préparation des données
    df_cohort = df.copy()
    df_cohort['order_month'] = df_cohort['Order Date'].dt.to_period('M')

    # Première commande par client (cohorte)
    first_purchase = df_cohort.groupby('Customer ID')['order_month'].min().reset_index()
    first_purchase.columns = ['Customer ID', 'cohort_month']

    # Merge avec les données
    df_cohort = df_cohort.merge(first_purchase, on='Customer ID')

    # Calcul de l'ancienneté (en mois depuis première commande)
    df_cohort['months_since_first'] = (df_cohort['order_month'] - df_cohort['cohort_month']).apply(lambda x: x.n)

    # Matrice de cohorte
    cohort_data = df_cohort.groupby(['cohort_month', 'months_since_first']).agg({
        'Customer ID': 'nunique'
    }).reset_index()

    cohort_data.columns = ['cohort', 'period', 'nb_clients']

    # Pivot pour avoir les périodes en colonnes
    cohort_pivot = cohort_data.pivot_table(
        index='cohort',
        columns='period',
        values='nb_clients',
        fill_value=0
    )

    # Calcul des taux de rétention (% par rapport à la période 0)
    cohort_size = cohort_pivot.iloc[:, 0]
    retention_matrix = cohort_pivot.divide(cohort_size, axis=0) * 100

    # Prendre les 12 dernières cohortes pour lisibilité
    retention_matrix_recent = retention_matrix.tail(12)

    # Conversion en format pour le frontend
    retention_data = []
    for idx, row in retention_matrix_recent.iterrows():
        cohort_row = {"cohort": str(idx)}
        for col in row.index[:12]:  # Limiter à 12 périodes
            if col in row.index:
                cohort_row[f"month_{col}"] = round(row[col], 1)
        retention_data.append(cohort_row)

    # Statistiques globales
    # Taux de rétention à 1 mois, 3 mois, 6 mois
    retention_1m = retention_matrix[1].mean() if 1 in retention_matrix.columns else 0
    retention_3m = retention_matrix[3].mean() if 3 in retention_matrix.columns else 0
    retention_6m = retention_matrix[6].mean() if 6 in retention_matrix.columns else 0

    return {
        "cohort_data": retention_data,
        "statistiques": {
            "retention_1_mois": round(retention_1m, 2),
            "retention_3_mois": round(retention_3m, 2),
            "retention_6_mois": round(retention_6m, 2),
            "nb_cohortes": len(cohort_pivot)
        }
    }

# === ENDPOINT CLIENTS (EXISTANT) ===

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

# === ENDPOINT ANALYSE ABC (PARETO) ===

@app.get("/kpi/analyse-abc", tags=["KPI Avancés - Analyse ABC"])
def get_analyse_abc(niveau: str = Query("produit", regex="^(produit|categorie|client)$")):
    """
    📊 ANALYSE ABC (PARETO)

    Segmentation selon le principe 80/20 (Pareto):
    - Classe A : 80% du CA (produits/clients les plus importants)
    - Classe B : 15% du CA (importance moyenne)
    - Classe C : 5% du CA (faible importance)

    Niveaux d'analyse : produit, categorie, client
    """

    if niveau == "produit":
        # Analyse par produit
        data = df.groupby(['Product Name', 'Category']).agg({
            'Sales': 'sum',
            'Profit': 'sum',
            'Quantity': 'sum'
        }).reset_index()

        data.columns = ['nom', 'categorie', 'ca', 'profit', 'quantite']
        data = data.sort_values('ca', ascending=False).reset_index(drop=True)

        # Calcul cumulatif
        data['ca_cumul'] = data['ca'].cumsum()
        ca_total = data['ca'].sum()
        data['pct_cumul'] = (data['ca_cumul'] / ca_total * 100).round(2)
        data['pct_ca'] = (data['ca'] / ca_total * 100).round(2)

        # Classification ABC
        def classify_abc(pct):
            if pct <= 80:
                return "A 🌟"
            elif pct <= 95:
                return "B 📊"
            else:
                return "C 📉"

        data['classe'] = data['pct_cumul'].apply(classify_abc)

    elif niveau == "categorie":
        # Analyse par catégorie
        data = df.groupby('Category').agg({
            'Sales': 'sum',
            'Profit': 'sum',
            'Quantity': 'sum'
        }).reset_index()

        data.columns = ['nom', 'ca', 'profit', 'quantite']
        data = data.sort_values('ca', ascending=False).reset_index(drop=True)
        data['categorie'] = data['nom']  # Pour cohérence

        # Calcul cumulatif
        data['ca_cumul'] = data['ca'].cumsum()
        ca_total = data['ca'].sum()
        data['pct_cumul'] = (data['ca_cumul'] / ca_total * 100).round(2)
        data['pct_ca'] = (data['ca'] / ca_total * 100).round(2)

        def classify_abc(pct):
            if pct <= 80:
                return "A 🌟"
            elif pct <= 95:
                return "B 📊"
            else:
                return "C 📉"

        data['classe'] = data['pct_cumul'].apply(classify_abc)

    else:  # client
        # Analyse par client
        data = df.groupby(['Customer ID', 'Customer Name']).agg({
            'Sales': 'sum',
            'Profit': 'sum',
            'Order ID': 'nunique'
        }).reset_index()

        data.columns = ['customer_id', 'nom', 'ca', 'profit', 'nb_commandes']
        data = data.sort_values('ca', ascending=False).reset_index(drop=True)
        data['categorie'] = 'Client'  # Pour cohérence

        # Calcul cumulatif
        data['ca_cumul'] = data['ca'].cumsum()
        ca_total = data['ca'].sum()
        data['pct_cumul'] = (data['ca_cumul'] / ca_total * 100).round(2)
        data['pct_ca'] = (data['ca'] / ca_total * 100).round(2)

        def classify_abc(pct):
            if pct <= 80:
                return "A 🌟"
            elif pct <= 95:
                return "B 📊"
            else:
                return "C 📉"

        data['classe'] = data['pct_cumul'].apply(classify_abc)

    # Statistiques par classe
    stats_classes = data.groupby('classe').agg({
        'nom': 'count',
        'ca': 'sum',
        'profit': 'sum'
    }).reset_index()

    stats_classes.columns = ['classe', 'nombre', 'ca_total', 'profit_total']
    stats_classes['pct_nombre'] = (stats_classes['nombre'] / len(data) * 100).round(2)
    stats_classes['pct_ca'] = (stats_classes['ca_total'] / ca_total * 100).round(2)

    # Préparer les données pour le retour
    result = []
    for _, row in data.iterrows():
        result.append({
            "nom": row['nom'],
            "categorie": row.get('categorie', ''),
            "ca": round(row['ca'], 2),
            "profit": round(row['profit'], 2),
            "pct_ca": row['pct_ca'],
            "pct_cumul": row['pct_cumul'],
            "classe": row['classe']
        })

    return {
        "data": result,
        "niveau": niveau,
        "statistiques": {
            "total_elements": len(data),
            "ca_total": round(ca_total, 2)
        },
        "par_classe": stats_classes.to_dict('records')
    }

# === ENDPOINTS ANALYSE DÉTAILLÉE ===

@app.get("/kpi/commandes/deficitaires", tags=["KPI Avancés - Analyse Détaillée"])
def get_commandes_deficitaires(limite: int = Query(50, ge=10, le=200)):
    """
    🔴 COMMANDES DÉFICITAIRES

    Liste des commandes ayant généré une perte
    """
    # Agrégation par commande
    commandes = df.groupby('Order ID').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Quantity': 'sum',
        'Discount': 'mean',
        'Order Date': 'first',
        'Customer Name': 'first',
        'Category': lambda x: ', '.join(x.unique())
    }).reset_index()

    commandes['marge_pct'] = (commandes['Profit'] / commandes['Sales'] * 100).replace([np.inf, -np.inf], 0).fillna(0)

    # Filtrer les commandes déficitaires (profit négatif)
    deficitaires = commandes[commandes['Profit'] < 0].copy()
    deficitaires = deficitaires.sort_values('Profit', ascending=True).head(limite)

    result = []
    for _, row in deficitaires.iterrows():
        result.append({
            "order_id": row['Order ID'],
            "date": row['Order Date'].strftime('%Y-%m-%d'),
            "client": row['Customer Name'],
            "categories": row['Category'],
            "ca": round(row['Sales'], 2),
            "profit": round(row['Profit'], 2),
            "perte_abs": round(abs(row['Profit']), 2),
            "marge_pct": round(row['marge_pct'], 2),
            "quantite": int(row['Quantity']),
            "discount_moyen": round(row['Discount'] * 100, 2)
        })

    # Statistiques
    total_perte = abs(deficitaires['Profit'].sum())
    nb_total_deficitaires = len(commandes[commandes['Profit'] < 0])

    return {
        "data": result,
        "statistiques": {
            "nb_commandes_deficitaires": nb_total_deficitaires,
            "perte_totale": round(total_perte, 2),
            "perte_moyenne": round(total_perte / nb_total_deficitaires, 2) if nb_total_deficitaires > 0 else 0,
            "pct_commandes_deficitaires": round(nb_total_deficitaires / len(commandes) * 100, 2)
        }
    }

@app.get("/kpi/remises/impact", tags=["KPI Avancés - Analyse Détaillée"])
def get_impact_remises():
    """
    💸 IMPACT DES REMISES (DISCOUNT)

    Analyse de l'impact des remises sur la rentabilité
    """
    # Créer des tranches de remise
    df_discount = df.copy()
    df_discount['tranche_discount'] = pd.cut(
        df_discount['Discount'] * 100,
        bins=[0, 5, 10, 15, 20, 100],
        labels=['0-5%', '5-10%', '10-15%', '15-20%', '>20%'],
        include_lowest=True
    )

    # Agrégation par tranche
    impact = df_discount.groupby('tranche_discount', observed=True).agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Order ID': 'nunique',
        'Quantity': 'sum'
    }).reset_index()

    impact['marge_pct'] = (impact['Profit'] / impact['Sales'] * 100).replace([np.inf, -np.inf], 0).fillna(0)
    impact['ca_moyen'] = impact['Sales'] / impact['Order ID']

    result = []
    for _, row in impact.iterrows():
        result.append({
            "tranche_discount": str(row['tranche_discount']),
            "nb_commandes": int(row['Order ID']),
            "ca_total": round(row['Sales'], 2),
            "profit_total": round(row['Profit'], 2),
            "marge_pct": round(row['marge_pct'], 2),
            "ca_moyen": round(row['ca_moyen'], 2),
            "quantite": int(row['Quantity'])
        })

    # Statistiques globales
    ca_total = df['Sales'].sum()
    profit_total = df['Profit'].sum()
    ca_avec_discount = df[df['Discount'] > 0]['Sales'].sum()
    profit_avec_discount = df[df['Discount'] > 0]['Profit'].sum()
    ca_sans_discount = df[df['Discount'] == 0]['Sales'].sum()
    profit_sans_discount = df[df['Discount'] == 0]['Profit'].sum()

    return {
        "data": result,
        "statistiques": {
            "ca_avec_discount": round(ca_avec_discount, 2),
            "profit_avec_discount": round(profit_avec_discount, 2),
            "marge_avec_discount": round(profit_avec_discount / ca_avec_discount * 100, 2) if ca_avec_discount > 0 else 0,
            "ca_sans_discount": round(ca_sans_discount, 2),
            "profit_sans_discount": round(profit_sans_discount, 2),
            "marge_sans_discount": round(profit_sans_discount / ca_sans_discount * 100, 2) if ca_sans_discount > 0 else 0,
            "pct_ca_avec_discount": round(ca_avec_discount / ca_total * 100, 2)
        }
    }

@app.get("/kpi/produits/cout-prix", tags=["KPI Avancés - Analyse Détaillée"])
def get_cout_prix_unitaire(limite: int = Query(30, ge=10, le=100)):
    """
    💰 COÛT & PRIX UNITAIRE

    Analyse du coût et prix unitaire par produit
    """
    produits = df.groupby(['Product Name', 'Category']).agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Quantity': 'sum'
    }).reset_index()

    # Calculs
    produits['prix_unitaire'] = produits['Sales'] / produits['Quantity']
    produits['marge_unitaire'] = produits['Profit'] / produits['Quantity']
    produits['cout_unitaire'] = produits['prix_unitaire'] - produits['marge_unitaire']
    produits['marge_pct'] = (produits['Profit'] / produits['Sales'] * 100).replace([np.inf, -np.inf], 0).fillna(0)

    # Tri par CA décroissant
    produits = produits.sort_values('Sales', ascending=False).head(limite)

    result = []
    for _, row in produits.iterrows():
        result.append({
            "produit": row['Product Name'],
            "categorie": row['Category'],
            "prix_unitaire": round(row['prix_unitaire'], 2),
            "cout_unitaire": round(row['cout_unitaire'], 2),
            "marge_unitaire": round(row['marge_unitaire'], 2),
            "marge_pct": round(row['marge_pct'], 2),
            "quantite_vendue": int(row['Quantity']),
            "ca_total": round(row['Sales'], 2)
        })

    # Statistiques
    return {
        "data": result,
        "statistiques": {
            "prix_unitaire_moyen": round(produits['prix_unitaire'].mean(), 2),
            "cout_unitaire_moyen": round(produits['cout_unitaire'].mean(), 2),
            "marge_unitaire_moyenne": round(produits['marge_unitaire'].mean(), 2)
        }
    }

# === ENDPOINTS LIVRAISONS ===

@app.get("/kpi/livraisons/delais", tags=["KPI Avancés - Livraisons"])
def get_delais_livraison():
    """
    📦 DÉLAI DE LIVRAISON RÉEL

    Analyse des délais entre commande et livraison
    """
    df_delais = df.copy()

    # Calcul du délai de livraison en jours
    df_delais['delai_livraison'] = (df_delais['Ship Date'] - df_delais['Order Date']).dt.days

    # Statistiques globales
    delai_moyen = df_delais['delai_livraison'].mean()
    delai_median = df_delais['delai_livraison'].median()
    delai_min = df_delais['delai_livraison'].min()
    delai_max = df_delais['delai_livraison'].max()

    # Par mode d'expédition
    delais_mode = df_delais.groupby('Ship Mode').agg({
        'delai_livraison': ['mean', 'median', 'min', 'max', 'count']
    }).reset_index()

    delais_mode.columns = ['mode', 'delai_moyen', 'delai_median', 'delai_min', 'delai_max', 'nb_commandes']

    # Distribution des délais
    delai_bins = pd.cut(
        df_delais['delai_livraison'],
        bins=[0, 2, 4, 7, 14, 30, 999],
        labels=['0-2j', '2-4j', '4-7j', '7-14j', '14-30j', '>30j']
    )

    distribution = delai_bins.value_counts().sort_index()

    # Par région
    delais_region = df_delais.groupby('Region').agg({
        'delai_livraison': ['mean', 'median']
    }).reset_index()

    delais_region.columns = ['region', 'delai_moyen', 'delai_median']

    return {
        "statistiques": {
            "delai_moyen_jours": round(delai_moyen, 1),
            "delai_median_jours": round(delai_median, 1),
            "delai_min_jours": int(delai_min),
            "delai_max_jours": int(delai_max)
        },
        "par_mode": delais_mode.to_dict('records'),
        "par_region": delais_region.to_dict('records'),
        "distribution": {str(k): int(v) for k, v in distribution.items()}
    }

@app.get("/kpi/livraisons/retards", tags=["KPI Avancés - Livraisons"])
def get_taux_retards():
    """
    ⏰ TAUX DE LIVRAISONS TARDIVES

    Analyse des retards de livraison (délai > 7 jours considéré comme tardif)
    """
    df_retards = df.copy()

    # Calcul du délai
    df_retards['delai_livraison'] = (df_retards['Ship Date'] - df_retards['Order Date']).dt.days

    # Définition d'un retard : selon le mode d'expédition
    seuils_retard = {
        'Standard Class': 7,
        'Second Class': 5,
        'First Class': 3,
        'Same Day': 1
    }

    def est_en_retard(row):
        seuil = seuils_retard.get(row['Ship Mode'], 7)
        return row['delai_livraison'] > seuil

    df_retards['est_retard'] = df_retards.apply(est_en_retard, axis=1)

    # Statistiques globales
    nb_total = len(df_retards)
    nb_retards = df_retards['est_retard'].sum()
    taux_retard = (nb_retards / nb_total * 100) if nb_total > 0 else 0

    # Par mode d'expédition
    retards_mode = df_retards.groupby('Ship Mode').agg({
        'est_retard': ['sum', 'count']
    }).reset_index()

    retards_mode.columns = ['mode', 'nb_retards', 'nb_total']
    retards_mode['taux_retard'] = (retards_mode['nb_retards'] / retards_mode['nb_total'] * 100).round(2)

    # Par région
    retards_region = df_retards.groupby('Region').agg({
        'est_retard': ['sum', 'count']
    }).reset_index()

    retards_region.columns = ['region', 'nb_retards', 'nb_total']
    retards_region['taux_retard'] = (retards_region['nb_retards'] / retards_region['nb_total'] * 100).round(2)

    # Par catégorie
    retards_categorie = df_retards.groupby('Category').agg({
        'est_retard': ['sum', 'count']
    }).reset_index()

    retards_categorie.columns = ['categorie', 'nb_retards', 'nb_total']
    retards_categorie['taux_retard'] = (retards_categorie['nb_retards'] / retards_categorie['nb_total'] * 100).round(2)

    return {
        "statistiques": {
            "nb_total_livraisons": nb_total,
            "nb_retards": int(nb_retards),
            "taux_retard_global": round(taux_retard, 2)
        },
        "par_mode": retards_mode.to_dict('records'),
        "par_region": retards_region.to_dict('records'),
        "par_categorie": retards_categorie.to_dict('records'),
        "seuils_utilises": seuils_retard
    }

@app.get("/kpi/livraisons/performance-mode", tags=["KPI Avancés - Livraisons"])
def get_performance_par_mode():
    """
    🚚 PERFORMANCE PAR MODE D'EXPÉDITION

    Analyse complète de chaque mode d'expédition
    """
    df_mode = df.copy()

    # Calcul du délai
    df_mode['delai_livraison'] = (df_mode['Ship Date'] - df_mode['Order Date']).dt.days

    # Agrégation par mode
    perf_mode = df_mode.groupby('Ship Mode').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Order ID': 'nunique',
        'delai_livraison': ['mean', 'median'],
        'Quantity': 'sum'
    }).reset_index()

    perf_mode.columns = ['mode', 'ca', 'profit', 'nb_commandes', 'delai_moyen', 'delai_median', 'quantite']

    # Calculs supplémentaires
    perf_mode['marge_pct'] = (perf_mode['profit'] / perf_mode['ca'] * 100).replace([np.inf, -np.inf], 0).fillna(0)
    perf_mode['ca_moyen'] = perf_mode['ca'] / perf_mode['nb_commandes']
    perf_mode['pct_commandes'] = (perf_mode['nb_commandes'] / perf_mode['nb_commandes'].sum() * 100).round(2)

    # Tri par nombre de commandes
    perf_mode = perf_mode.sort_values('nb_commandes', ascending=False)

    result = []
    for _, row in perf_mode.iterrows():
        result.append({
            "mode": row['mode'],
            "ca": round(row['ca'], 2),
            "profit": round(row['profit'], 2),
            "marge_pct": round(row['marge_pct'], 2),
            "nb_commandes": int(row['nb_commandes']),
            "pct_commandes": row['pct_commandes'],
            "ca_moyen": round(row['ca_moyen'], 2),
            "delai_moyen": round(row['delai_moyen'], 1),
            "delai_median": round(row['delai_median'], 1),
            "quantite": int(row['quantite'])
        })

    # Mode le plus rentable
    mode_plus_rentable = perf_mode.loc[perf_mode['profit'].idxmax(), 'mode']

    # Mode le plus rapide
    mode_plus_rapide = perf_mode.loc[perf_mode['delai_moyen'].idxmin(), 'mode']

    # Mode le plus utilisé
    mode_plus_utilise = perf_mode.loc[perf_mode['nb_commandes'].idxmax(), 'mode']

    return {
        "data": result,
        "insights": {
            "mode_plus_rentable": mode_plus_rentable,
            "mode_plus_rapide": mode_plus_rapide,
            "mode_plus_utilise": mode_plus_utilise
        }
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
