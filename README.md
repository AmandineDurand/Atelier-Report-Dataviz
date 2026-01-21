# 🛒 Superstore BI - Advanced Analytics Dashboard

Système complet d'analyse Business Intelligence avancée du dataset **Sample Superstore** avec API REST FastAPI et dashboard interactif Streamlit.

## 🎯 Nouvelles Fonctionnalités (v2.0)

### 📊 Tab Produits - Analyses Stratégiques
- **Matrice BCG** (Boston Consulting Group)
  - Axe X : Part de marché (% du CA total)
  - Axe Y : Croissance YoY (année N vs N-1)
  - Quadrants : Étoiles ⭐, Vaches à lait 🐄, Dilemmes ❓, Poids morts 💀
- **Produits à faible marge**
  - Identification des produits qui vendent mais ne rapportent pas
  - Seuil de marge configurable
  - Indicateur de rotation des stocks
- **Top produits** par CA, Profit ou Quantité

### 📦 Tab Catégories - Visualisations Avancées
- **Graphique Waterfall** (Cascade)
  - Contribution de chaque catégorie au profit total
  - Détail par sous-catégorie
- **Matrice Performance/Marge** (4 quadrants)
  - Q1 🌟 : CA élevé + Marge élevée → Priorité
  - Q2 ⚙️ : CA élevé + Marge faible → À optimiser
  - Q3 📈 : CA faible + Marge élevée → À développer
  - Q4 ❌ : CA faible + Marge faible → À abandonner

### 📅 Tab Temporel - Tendances et Saisonnalité
- **Moyenne mobile** (3 mois) pour lisser les variations
- **Comparaison N/N-1** avec année précédente en transparence
- **Taux de croissance** période par période
- **Analyse de saisonnalité**
  - Graphique radar du pattern mensuel
  - Indice de saisonnalité (base 100)
  - Heatmap CA par année et mois

### 🌍 Tab Géographique - Performance Relative
- **CA par client** (performance relative)
- **Treemap/Heatmap États** avec code couleur selon la marge
- **Classement des villes** les plus performantes
  - Top par CA
  - Top par Marge
  - Top par CA/Client

---

## 📁 Structure du projet

```
superstore-bi/
│
├── backend/
│   ├── main.py              # API FastAPI (endpoints KPI avancés)
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── dashboard.py         # Dashboard Streamlit avancé
│   ├── Dockerfile
│   └── requirements.txt
│
├── tests/
│   └── test_api.py          # Tests unitaires
│
├── docker-compose.yml       # Orchestration des services
├── .dockerignore
└── README.md
```

---

## 🚀 Installation et démarrage

### Option 1 : Docker Compose (Recommandé)

```bash
# Cloner le projet
git clone <repository>
cd superstore-bi

# Lancer les services
docker-compose up --build

# Ou en arrière-plan
docker-compose up -d --build
```

✅ API : **http://localhost:8000**
✅ Dashboard : **http://localhost:8501**
📚 Documentation API : **http://localhost:8000/docs**

### Option 2 : Installation locale

```bash
# Backend
cd backend
pip install -r requirements.txt
python main.py

# Frontend (nouveau terminal)
cd frontend
pip install -r requirements.txt
streamlit run dashboard.py
```

---

## 📖 Nouveaux Endpoints API

### KPI Produits Avancés

```bash
# Matrice BCG
curl "http://localhost:8000/kpi/produits/bcg?limite=50"

# Produits à faible marge
curl "http://localhost:8000/kpi/produits/faible-marge?seuil_marge=5&limite=20"
```

### KPI Catégories Avancés

```bash
# Waterfall profit
curl http://localhost:8000/kpi/categories/waterfall

# Matrice performance/marge
curl http://localhost:8000/kpi/categories/matrix
```

### KPI Temporels Avancés

```bash
# Analyse avancée (MM, N-1, croissance)
curl http://localhost:8000/kpi/temporel/avance

# Saisonnalité
curl http://localhost:8000/kpi/temporel/saisonnalite
```

### KPI Géographiques Avancés

```bash
# Performance par État
curl http://localhost:8000/kpi/geographique/etats

# Top villes
curl "http://localhost:8000/kpi/geographique/villes?limite=20"
```

---

## 📊 Réponses API Exemples

### Matrice BCG
```json
{
  "data": [
    {
      "produit": "Canon imageCLASS...",
      "categorie": "Technology",
      "ca_actuel": 61599.82,
      "croissance": 25.4,
      "part_marche": 2.15,
      "marge_pct": 18.5,
      "quadrant": "Étoile ⭐"
    }
  ],
  "seuils": {
    "part_marche_mediane": 0.12,
    "croissance_mediane": 8.5
  },
  "repartition": {
    "etoiles": 12,
    "vaches": 18,
    "dilemmes": 8,
    "poids_morts": 62
  }
}
```

### Waterfall Catégories
```json
{
  "waterfall": [
    {"label": "Technology", "value": 145454.95, "type": "category"},
    {"label": "Office Supplies", "value": 122490.80, "type": "category"},
    {"label": "Furniture", "value": 18451.27, "type": "category"}
  ],
  "profit_total": 286397.02
}
```

### Saisonnalité
```json
{
  "data": [
    {
      "month": 1,
      "month_name": "January",
      "ca_moyen": 45230.50,
      "indice_saisonnalite": 78.5,
      "volatilite": 12.3
    }
  ],
  "statistiques": {
    "mois_pic": "November",
    "indice_pic": 142.5,
    "mois_creux": "February",
    "indice_creux": 65.2
  }
}
```

---

## 🎨 Fonctionnalités Dashboard

### Visualisations Interactives
- 📊 Scatter plots zoomables (Matrice BCG)
- 📈 Graphiques en cascade (Waterfall)
- 🎯 Matrices à quadrants
- 📅 Radar de saisonnalité
- 🗺️ Treemaps géographiques
- 📉 Courbes avec moyenne mobile

### Filtres Dynamiques
- 📅 Plage de dates
- 📦 Catégorie
- 🌍 Région
- 👥 Segment client

### KPI Cards
- Affichage en temps réel
- Mise en forme automatique (€, %, nombres)
- Comparaisons et variations

---

## 🔧 Configuration

### Variables d'environnement

| Variable | Description | Défaut |
|----------|-------------|--------|
| `API_URL` | URL de l'API backend | `http://localhost:8000` |
| `PYTHONUNBUFFERED` | Output Python non bufferisé | `1` |

### Seuils configurables

- **BCG** : Part marché > 0.5%, Croissance > 10%
- **Faible marge** : Marge < 5% (configurable)
- **Matrice catégories** : Médianes CA et Marge

---

## 📚 Technologies utilisées

- **Backend** : FastAPI, Pandas, NumPy, Pydantic
- **Frontend** : Streamlit, Plotly, Requests
- **Infrastructure** : Docker, Docker Compose
- **Dataset** : Sample Superstore (GitHub)

---

## 🗃️ Dataset

**Source** : [Sample Superstore](https://github.com/leonism/sample-superstore)

| Colonne | Description |
|---------|-------------|
| Order ID | Identifiant commande |
| Order Date | Date commande |
| Customer ID | Identifiant client |
| Product Name | Nom produit |
| Category | Catégorie |
| Sub-Category | Sous-catégorie |
| Sales | CA |
| Quantity | Quantité |
| Discount | Remise |
| Profit | Profit |
| Region | Région |
| State | État |
| City | Ville |

**Période** : 2014-2017
**Taille** : ~10 000 lignes

---

## 📝 Changelog

### v2.0.0
- ✅ Matrice BCG avec classification automatique
- ✅ Analyse produits faible marge
- ✅ Waterfall profit catégories
- ✅ Matrice performance/marge
- ✅ Moyenne mobile et comparaison N-1
- ✅ Analyse saisonnalité (radar + heatmap)
- ✅ Performance CA/client par zone
- ✅ Heatmap États par marge
- ✅ Classement villes multi-critères

### v1.0.0
- ✅ KPI globaux
- ✅ Top produits
- ✅ Performance catégories
- ✅ Évolution temporelle
- ✅ Performance géographique
- ✅ Analyse clients

---

## 📄 Licence

MIT License - Projet pédagogique
