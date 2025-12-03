# 🚗 Car Analytics - Pipeline ETL & API REST

## 📋 Description

**Car Analytics** est un système complet d'analyse du marché automobile français. Il collecte, traite et expose des données de véhicules via une API REST déployée dans le cloud.

### 🎯 Fonctionnalités principales

- **Pipeline ETL** : Scraping → Validation → Transformation → Stockage
- **API REST** : Endpoints pour interroger les données
- **Anti-détection** : Contourne les protections des sites web
- **Déploiement Cloud** : API accessible 24/7
- **Rapports HTML** : Visualisation interactive des données

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     PIPELINE ETL                            │
├─────────────────────────────────────────────────────────────┤
│  1. SCRAPE    →  Collecte des annonces (Selenium)           │
│  2. VALIDATE  →  Vérification qualité des données           │
│  3. TRANSFORM →  Nettoyage et normalisation                 │
│  4. LOAD      →  Stockage SQLite + Rapport HTML             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      API REST                               │
├─────────────────────────────────────────────────────────────┤
│  GET /vehicles      →  Liste des véhicules                  │
│  GET /search        →  Recherche avec filtres               │
│  GET /stats         →  Statistiques du marché               │
│  GET /docs          →  Documentation Swagger                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   CLOUD (Render)                            │
│           https://car-analytics-api.onrender.com            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technologies utilisées

| Catégorie | Technologies |
|-----------|--------------|
| **Langage** | Python 3.13 |
| **Scraping** | Selenium, undetected-chromedriver |
| **API** | FastAPI, Uvicorn |
| **Base de données** | SQLite |
| **Containerisation** | Docker |
| **Cloud** | Render |
| **CI/CD** | GitHub (auto-deploy) |

---

## 📁 Structure du projet

```
Car-Analytics/
├── pipeline.py          # 🔄 Pipeline ETL principal
├── api.py               # 🚀 API FastAPI
├── run.py               # 🎮 Menu interactif
├── gen_rapport.py       # 📊 Générateur de rapport HTML
├── data/
│   └── vehicles.db      # 💾 Base de données SQLite
├── Dockerfile.api       # 🐳 Config Docker
├── requirements.txt     # 📦 Dépendances Python
└── README.md            # 📖 Documentation
```

---

## 🚀 Installation & Utilisation

### 1. Cloner le repo
```bash
git clone https://github.com/Toufic99/Rapport-Marche-Auto.git
cd Rapport-Marche-Auto
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Lancer le menu interactif
```bash
python run.py
```

### 4. Ou lancer directement le pipeline
```bash
python pipeline.py --pages 5
```

---

## 🌐 API en ligne

**URL** : https://car-analytics-api.onrender.com

### Endpoints disponibles

| Endpoint | Description | Exemple |
|----------|-------------|---------|
| `GET /` | Page d'accueil | - |
| `GET /vehicles` | Liste tous les véhicules | `/vehicles?limit=10` |
| `GET /vehicles/{id}` | Détails d'un véhicule | `/vehicles/1` |
| `GET /search` | Recherche avec filtres | `/search?marque=BMW&prix_max=15000` |
| `GET /stats` | Statistiques du marché | - |
| `GET /docs` | Documentation Swagger | - |

### Paramètres de recherche

- `marque` : Filtrer par marque (BMW, PEUGEOT, RENAULT...)
- `modele` : Filtrer par modèle
- `prix_min` / `prix_max` : Fourchette de prix
- `km_max` : Kilométrage maximum
- `annee_min` : Année minimum
- `energie` : Type de carburant (Diesel, Essence, Électrique)
- `ville` : Ville
- `departement` : Département (ex: 75, 86)

---

## 📊 Données collectées

Pour chaque véhicule :

| Champ | Description |
|-------|-------------|
| `marque` | Marque du véhicule |
| `modele` | Modèle |
| `annee` | Année de mise en circulation |
| `prix` | Prix en euros |
| `km` | Kilométrage |
| `energie` | Type de carburant |
| `boite_vitesse` | Manuelle / Automatique |
| `ville` | Ville de l'annonce |
| `departement` | Département |
| `lien` | Lien vers l'annonce originale |

---

## 🎮 Menu interactif (run.py)

```
╔══════════════════════════════════════════════════════════════╗
║                  🚗 CAR ANALYTICS                            ║
╠══════════════════════════════════════════════════════════════╣
║   [1] 🔄 Scraper MAINTENANT                                  ║
║   [2] ⏰ Programmer scraping AUTOMATIQUE                      ║
║   [3] 📊 Voir les STATISTIQUES                               ║
║   [4] 📄 Générer RAPPORT HTML                                ║
║   [5] 🌐 Ouvrir l'API en ligne                               ║
║   [6] 📤 Pousser vers GitHub                                 ║
║   [0] ❌ Quitter                                             ║
╚══════════════════════════════════════════════════════════════╝
```

---

## 🐳 Docker

### Build l'image
```bash
docker build -f Dockerfile.api -t car-analytics-api .
```

### Lancer le container
```bash
docker run -p 8000:8000 car-analytics-api
```

---

## 📈 Compétences démontrées

- ✅ **Web Scraping** avancé avec anti-détection
- ✅ **Pipeline ETL** (Extract, Transform, Load)
- ✅ **API REST** avec FastAPI
- ✅ **Base de données** SQLite
- ✅ **Containerisation** Docker
- ✅ **Déploiement Cloud** (Render)
- ✅ **Git/GitHub** & CI/CD

---

## 👤 Auteur

**Toufic BATHICH**

- GitHub: [@Toufic99](https://github.com/Toufic99)

---

## 📝 License

MIT License - Libre d'utilisation
