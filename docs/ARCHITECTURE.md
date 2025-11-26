# 🏗️ Architecture du Projet

## Vue d'Ensemble

```
┌─────────────────────────────────────────────────────────┐
│                  APPLICATION PRINCIPALE                 │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │      LEBONCOIN_SCRAPER (Classe Principale)       │  │
│  │  - Gère le flux principal de scraping             │  │
│  │  - Orchestre les différents modules               │  │
│  └──────────────────────────────────────────────────┘  │
│                          │                               │
│         ┌────────────────┼────────────────┐             │
│         │                │                │             │
│    ┌────▼────┐     ┌─────▼──────┐   ┌────▼────┐       │
│    │AntiDetec-│    │ HTML Parser │   │Database │       │
│    │tionMgr  │    │             │   │Manager  │       │
│    └─────────┘    └─────────────┘   └────────┘       │
│         │                │                │             │
│    ┌────▼────────┐  ┌────▼─────────┐ ┌──▼──────────┐   │
│    │• User-Agent │  │• BeautifulSoup│ │• SQLite    │   │
│    │• Rotation   │  │• Regex Parser │ │• Schema    │   │
│    │• Headers    │  │• JSON Extract │ │• Queries   │   │
│    │• Delays     │  │• Validation   │ │            │   │
│    └────────────┘  └───────────────┘ └────────────┘   │
│                                                          │
└─────────────────────────────────────────────────────────┘
                          │
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
    ┌───▼────┐       ┌───▼────┐       ┌───▼────┐
    │RAPPORT │       │IMAGES  │       │STATS   │
    │HTML    │       │TELECHG │       │ANALYSIS│
    └────────┘       └────────┘       └────────┘
```

## Modules Principaux

### 1. **LeBonCoinScraper** (Classe Principale)
**Fichier**: `leboncoin_scraper.py` (853 lignes)

**Responsabilités**:
- Orchestration du workflow de scraping
- Gestion de la session HTTP
- Coordination des autres modules
- Logging et error handling

**Méthodes clés**:
```python
__init__()              # Initialisation
scrape_vehicles()       # Scraper principal
extract_vehicle_data()  # Extraction d'une annonce
save_to_database()      # Sauvegarde SQLite
generate_report()       # Génération rapports
```

### 2. **AntiDetectionManager**
**Responsabilités**:
- Rotation des User-Agents
- Gestion des délais (1-5 secondes aléatoires)
- Headers personnalisés réalistes
- Gestion des erreurs (retry, backoff)

**Implémentation**:
```python
class AntiDetectionManager:
    - user_agents: List[str]        # Pool d'UA
    - session: requests.Session      # Session persistent
    - request_count: int             # Compteur requêtes
    - last_error_time: datetime      # Timestamp erreur
```

### 3. **Parser HTML/JSON**
**Méthode**: `_parse_vehicle_data(html)`

**Extraction**:
- Titre, marque, modèle
- Prix, kilométrage, année
- Type énergie, boîte vitesses
- Localisation, photos
- Info vendeur

**Technologies**:
- BeautifulSoup : Parsing HTML
- Regex : Extraction valeurs numériques
- JSON : Données inlinées Next.js

### 4. **Database Manager**
**Tech**: SQLite 3

**Schéma**:
```sql
CREATE TABLE vehicles (
    id INTEGER PRIMARY KEY,
    listing_id INTEGER UNIQUE,
    title TEXT,
    brand TEXT,
    price INTEGER,
    mileage INTEGER,
    year INTEGER,
    energy TEXT,
    transmission TEXT,
    city TEXT,
    date_posted DATETIME,
    status TEXT,
    seller_type TEXT,
    photo_urls TEXT,  -- JSON array
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_price ON vehicles(price);
CREATE INDEX idx_status ON vehicles(status);
CREATE INDEX idx_energy ON vehicles(energy);
```

### 5. **Report Generator**
**Fichier**: `report_generator.py`

**Outputs**:
- Rapport HTML interactif
- Export CSV
- Statistiques JSON
- Graphiques (optionnel)

**Fonctionnalités HTML**:
- Tableau filtrable 2,955+ annonces
- Recherche en temps réel
- Filtres : prix, année, énergie, etc.
- Tri dynamique
- Design responsive CSS

### 6. **Stats Analyzer**
**Fichier**: `stats.py`

**Analyses**:
- Moyenne/min/max par critère
- Répartition par énergie
- Distribution géographique
- Tendances prix/année
- Stats vendeur

---

## Flux de Données

```
1. INITIALIZATION
   ├─ Load config
   ├─ Init database
   └─ Setup anti-detection

2. SCRAPING LOOP (pour chaque page)
   ├─ Get random delay (1-5s)
   ├─ Rotate User-Agent
   ├─ Make HTTP request
   ├─ Parse response (HTML/JSON)
   ├─ Extract 25 vehicles par page
   ├─ Download images
   └─ Save to database

3. ERROR HANDLING
   ├─ If 403 → Backoff 5 minutes
   ├─ If timeout → Retry 3x
   └─ If parse error → Log + continue

4. POST-PROCESSING
   ├─ Calculate statistics
   ├─ Generate HTML report
   ├─ Export CSV
   └─ Save metadata

5. OUTPUT
   ├─ leboncoin_vehicles.db
   ├─ leboncoin_rapport.html
   ├─ leboncoin_rapport_complet.csv
   └─ voitures_photos/
```

---

## Configuration & Variables

### Environment Variables (.env)
```bash
# Scraping
REQUEST_TIMEOUT=10          # Timeout requête (sec)
MAX_RETRIES=3               # Nombre de retries
DELAY_BETWEEN_REQUESTS=2    # Délai par défaut
MAX_CONSECUTIVE_ERRORS=5    # Circuit breaker

# Database
DB_PATH=./leboncoin_vehicles.db
BACKUP_DB=True

# Images
DOWNLOAD_IMAGES=True
IMAGE_QUALITY=medium        # low, medium, high
MAX_IMAGES_PER_VEHICLE=10

# Logging
LOG_LEVEL=INFO
LOG_FILE=./scraper.log
```

### Paramètres Scraping (config.py)
```python
SCRAPING_CONFIG = {
    'start_page': 1,
    'max_pages': 50,
    'vehicles_per_page': 25,
    'delay_min': 1,           # Delai min (sec)
    'delay_max': 5,           # Délai max (sec)
    'timeout': 10,            # Timeout
    'max_retries': 3,
    'backoff_factor': 2,      # Exponential backoff
    'headless': True,
    'verify_ssl': True,
}
```

---

## Optimisations Appliquées

### Performance
✅ **Session HTTP Persistent**: Réutilise connexions TCP
✅ **Lazy Loading**: Images téléchargées asynchrone
✅ **Database Indexing**: Index sur price, status, energy
✅ **Batch Inserts**: Insert 25 vehicles à la fois

### Anti-Détection
✅ **User-Agent Rotation**: 5 UAs différents
✅ **Délais Humain-Like**: 1-5 secondes aléatoires
✅ **Headers Réalistes**: Referer, DNT, Accept-Language
✅ **Backoff Exponentiel**: 5 min après 403

### Sécurité
✅ **SSL Verification**: Vérifie certificats HTTPS
✅ **Timeout Protection**: Pas de freeze infini
✅ **Error Logging**: Trace complète des erreurs
✅ **Resource Cleanup**: Close properly sessions

---

## Extensibilité

### Ajouter Nouveau Site
1. Créer classe héritant `BaseScraper`
2. Implémenter `parse_vehicle_data()`
3. Configurer selectors CSS/XPath
4. Ajouter dans orchestrateur principal

### Ajouter Nouvelle Analyse
```python
def custom_analysis(db_path):
    conn = sqlite3.connect(db_path)
    # Queries personnalisées
    return results
```

### Intégrer API externe
```python
def enrich_vehicle_data(vehicle_dict):
    # Appel API (valeurs de marché, etc.)
    vehicle_dict['market_value'] = get_market_value(...)
    return vehicle_dict
```

---

## Métriques de Qualité

| Métrique | Valeur |
|----------|--------|
| Lignes de code principal | 853 |
| Couverture des tests | ~80% |
| Complexité cyclomatique | 7 (acceptable) |
| Anti-détection techniques | 4+ |
| Base de données optimisée | Oui (indexes) |

---

## Points d'Amélioration Futurs

- [ ] Async I/O (aiohttp) pour speed 3x
- [ ] Selenium pour sites JavaScript
- [ ] API REST (Flask/FastAPI)
- [ ] Dashboard temps réel (Streamlit)
- [ ] Machine Learning (prédiction prix)
- [ ] Multi-site support
