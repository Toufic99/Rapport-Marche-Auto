# 📊 Rapport Marché Auto

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

**Un scraper avancé pour analyser le marché automobile**

[🔗 Voir les Fonctionnalités](#-fonctionnalités) • [📊 Résultats](#-résultats) • [🚀 Démarrage](#-démarrage-rapide) • [📚 Documentation](#-documentation)

</div>

---

## 📋 À propos

Ce projet démontre des **compétences avancées en web scraping** avec extraction automatique d'annonces automobiles. Il implémente des techniques **anti-détection sophistiquées** et génère un **rapport d'analyse interactif complet**.

### Compétences Démontrées
- ✅ Web scraping avancé & gestion anti-détection
- ✅ Architecture orientée objet (OOP) en Python
- ✅ Gestion de bases de données (SQLite)
- ✅ Traitement et analyse de données
- ✅ Génération de rapports HTML/CSS interactifs
- ✅ Gestion de ressources (téléchargement d'images)
- ✅ Automatisation et optimisation

---

## 🎯 Fonctionnalités

### Core Scraping
- 🔄 **Extraction multi-pages** avec gestion intelligente des paginatons
- 🛡️ **Anti-détection avancée**
  - Rotation d'User-Agents réalistes
  - Gestion des délais entre requêtes (humain-like)
  - Headers personnalisés
  - Gestion des erreurs de connexion
  
- 📸 **Téléchargement d'images** organisé par véhicule
- 💾 **Stockage persistant** en SQLite avec schéma optimisé

### Analyse & Visualisation
- 📊 Statistiques par type d'énergie (Diesel, Essence, Électrique, etc.)
- 🗺️ Analyse géographique des prix
- 💹 Comparaison prix/kilométrage/année
- 📈 Rapport HTML interactif avec filtres dynamiques

### Données Extraites
Pour chaque annonce :
- ID unique, Titre, Marque, Modèle
- Prix, Kilométrage, Année
- Type d'énergie, Boîte de vitesses
- Localisation, Photos
- Statut (Active/Vendue)
- Infos vendeur & Date publication

---

## 📊 Résultats

### Exemple de Dataset
```
Total Annonces Scrapées: 2,955
├── Actives: 1,309 ✓
├── Vendues: 1,646 ✗
└── Prix Moyen: 12,850€

Répartition par Énergie:
├── Diesel: 1,525 annonces (51.6%)
├── Essence: 1,174 annonces (39.7%)
├── Éthanol: 149 annonces (5.0%)
├── Hybride: 63 annonces (2.1%)
└── Autres: 44 annonces (1.5%)

Plage de Prix: 400€ → 159,980€
Kilométrage Moyen: 156,200 km
```

### Visualisation
Le rapport généré (`leboncoin_rapport.html`) inclut :
- 📋 Tableau filtrable avec 2,955+ annonces
- 🔍 Recherche en temps réel
- 📊 Filtres : Prix, Année, Énergie, Type vendeur
- 🎨 Design moderne avec CSS responsive

---

## 🚀 Démarrage Rapide

### Prérequis
- Python 3.8+
- pip (gestionnaire de paquets)

### Installation

```bash
# 1. Cloner le repository
git clone https://github.com/[TON_USERNAME]/leboncoin-scraper.git
cd leboncoin-scraper

# 2. Créer un environnement virtuel
python -m venv env
source env/bin/activate  # Sur Windows: env\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt
```

### Utilisation Basique

```python
from leboncoin_scraper import LeBonCoinScraper

# Initialiser le scraper
scraper = LeBonCoinScraper()

# Lancer le scraping
scraper.scrape_vehicles(pages=10)  # Scrape 10 pages

# Générer le rapport
scraper.generate_report()
```

**Résultat :** 
- `leboncoin_vehicles.db` (base de données SQLite)
- `leboncoin_rapport.html` (rapport interactif)
- `voitures_photos/` (dossier avec images)

---

## 📁 Structure du Projet

```
LeBonCoin_Scraper/
├── 📄 README.md                      # Ce fichier
├── 📄 LICENSE                        # Licence MIT
├── 📄 .gitignore                     # Fichiers ignorés
├── 📄 requirements.txt               # Dépendances Python
│
├── 🐍 CORE SCRAPING
│   ├── leboncoin_scraper.py          # Scraper principal (853 lignes)
│   ├── report_generator.py           # Génération de rapports
│   └── stats.py                      # Analyses statistiques
│
├── 📚 DOCUMENTATION & GUIDES
│   ├── GUIDE_WEB_SCRAPING.md         # Guide complet du scraping
│   ├── ETUDE_CAS_LEBONCOIN.py        # Cas d'étude détaillé
│   └── EXERCICES_SCRAPING.py         # Exercices pratiques
│
├── 📊 DONNÉES (Générées après scraping)
│   ├── leboncoin_vehicles.db         # Base de données SQLite
│   ├── leboncoin_rapport.html        # Rapport HTML interactif
│   ├── leboncoin_rapport_complet.csv # Export CSV
│   └── voitures_photos/              # Images téléchargées
│
└── 📁 AUTRES
    ├── __pycache__/                  # Cache Python (ignoré)
    └── .env                          # Variables d'environnement (privé)
```

---

## 🔧 Configuration Avancée

### Variables d'Environnement (.env)
```bash
# Scraping
REQUEST_TIMEOUT=10
MAX_RETRIES=3
DELAY_BETWEEN_REQUESTS=2

# Base de données
DB_PATH=./leboncoin_vehicles.db
EXPORT_CSV=True

# Logging
LOG_LEVEL=INFO
```

### Paramètres de Scraping
```python
config = {
    'max_pages': 50,              # Nombre de pages à scraper
    'delay_min': 1,               # Délai min entre requêtes (sec)
    'delay_max': 5,               # Délai max entre requêtes (sec)
    'timeout': 10,                # Timeout par requête
    'download_images': True,      # Télécharger les photos
    'headless': True,             # Mode sans interface
}
```

---

## 🛡️ Technique Anti-Détection

Le scraper implémente plusieurs techniques pour éviter le blocage :

### 1. **Rotation User-Agents**
```python
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...',
    # + 3 autres
]
```

### 2. **Délais Humain-Like**
- Délais aléatoires entre requêtes (1-5 secondes)
- Pauses intelligentes après N requêtes
- Gestion des erreurs avec backoff exponentiel

### 3. **Headers Réalistes**
```python
headers = {
    'User-Agent': 'random',
    'Accept-Language': 'fr-FR,fr;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://www.leboncoin.fr/',
    'DNT': '1',
}
```

### 4. **Gestion des Erreurs**
- Retry automatique sur timeouts
- Circuit breaker après 5 erreurs consécutives
- Logs détaillés pour debugging

---

## 📊 Exemple de Rapport

Le rapport HTML généré (`leboncoin_rapport.html`) contient :

### Dashboard Statistiques
```
┌─────────────────────────────────┐
│  Total     Actives    Vendues   │
│  2,955     1,309      1,646     │
└─────────────────────────────────┘
```

### Tableau Interactif
- ✅ **2,955 annonces** affichables
- 🔍 **Recherche** : titre, marque, ville
- 📊 **Filtres** : prix, année, énergie, vendeur
- 📈 **Tri** : date, prix, kilométrage, ville

### Statistiques Détaillées
- Prix moyen par marque
- Kilométrage par année
- Distribution géographique
- Analyse vendeurs

---

## 🔄 Workflow Complet

```
1. Initialisation du Scraper
   ↓
2. Scraping des Pages LeBonCoin
   ├─ Extraction HTML → JSON
   ├─ Validation données
   └─ Sauvegarde SQLite
   ↓
3. Téléchargement Images
   ├─ Création dossiers par véhicule
   └─ Téléchargement parallèle
   ↓
4. Analyse Statistiques
   ├─ Agrégation par type d'énergie
   ├─ Analyse géographique
   └─ Calculs prix/km
   ↓
5. Génération Rapports
   ├─ Export CSV
   ├─ Génération HTML interactif
   └─ Graphiques
```

---

## 📚 Documentation

### Fichiers Inclus
- **`GUIDE_WEB_SCRAPING.md`** : Guide complet du web scraping (566 lignes)
  - Fondamentaux du scraping
  - Problèmes rencontrés & solutions
  - Bonnes pratiques
  - Cas d'étude complet

- **`ETUDE_CAS_LEBONCOIN.py`** : Analyse détaillée du projet
  - Architecture système
  - Choix techniques justifiés
  - Optimisations appliquées

- **`EXERCICES_SCRAPING.py`** : Exercices pratiques avec solutions
  - Niveau débutant → Avancé
  - Tests unitaires inclus

### Apprendre & Contribuer
1. Lire `GUIDE_WEB_SCRAPING.md` pour comprendre les concepts
2. Explorer `leboncoin_scraper.py` pour la mise en œuvre
3. Tester avec `EXERCICES_SCRAPING.py`
4. Consulter `ETUDE_CAS_LEBONCOIN.py` pour l'architecture

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

### Idées d'Amélioration
- [ ] Ajouter support Selenium pour JavaScript dynamique
- [ ] Intégrer base de données PostgreSQL
- [ ] Créer API Flask pour données temps réel
- [ ] Ajouter dashboard Streamlit
- [ ] Support multi-site (Automobile Classique, etc.)

---

## ⚖️ Licence

Ce projet est sous licence **MIT** - voir le fichier `LICENSE` pour détails.

**Important** : Si vous utilisez ce code dans vos projets, veuillez inclure l'attribution.

---

## ⚠️ Avertissements Légaux

- **Respectez les conditions d'utilisation** de LeBonCoin.fr
- Utilisez un délai approprié entre les requêtes
- Ne surchargez pas les serveurs
- **À usage éducatif/personnel uniquement**

---

## 📧 Contact & Support

- 📧 Email: [toufic.bathish123@gmail.com](mailto:toufic.bathish123@gmail.com)
- 💼 LinkedIn: [Toufic Bathich](https://www.linkedin.com/in/toufic-bathich-b73081233)
- 🐙 GitHub: [@Toufic99](https://github.com/Toufic99)

---

## 🎓 Concepts Clés Démontrés

| Concept | Niveau | Implémentation |
|---------|--------|---|
| Web Scraping | 🟥 Avancé | BeautifulSoup + Regex |
| Anti-Détection | 🟥 Avancé | Rotation UA + Délais |
| OOP | 🟨 Intermédiaire | Classes + Design Patterns |
| SQLite | 🟨 Intermédiaire | Schéma optimisé + Requêtes |
| HTML/CSS | 🟩 Débutant | Rapport interactif |
| Python | 🟥 Avancé | Asyncio, Context Manager |

---

<div align="center">

### ⭐ Si ce projet t'a été utile, n'hésite pas à laisser une star !

**Fait avec ❤️ par [Toufic Bathich](https://github.com/Toufic99)**

</div>
