# ⚡ Quick Start Guide

## 🚀 Démarrage en 5 Minutes

### 1️⃣ Installation (2 min)
```bash
git clone https://github.com/[TON_USERNAME]/leboncoin-scraper.git
cd leboncoin-scraper
python -m venv env
source env/bin/activate          # macOS/Linux
.\env\Scripts\Activate.ps1       # Windows
pip install -r requirements.txt
```

### 2️⃣ Premier Scraping (2 min)
```bash
python -c "
from leboncoin_scraper import LeBonCoinScraper
scraper = LeBonCoinScraper()
scraper.scrape_vehicles(pages=2)
"
```

### 3️⃣ Voir les Résultats (1 min)
```bash
# Générer et ouvrir rapport
open leboncoin_rapport.html  # macOS
start leboncoin_rapport.html # Windows
xdg-open leboncoin_rapport.html # Linux
```

✅ **Fait !** Vous avez 50+ annonces dans votre base de données.

---

## 🎯 Cas d'Usage Courants

### Scraper 10 Pages (250 annonces)
```python
from leboncoin_scraper import LeBonCoinScraper

scraper = LeBonCoinScraper()
scraper.scrape_vehicles(pages=10)
```

### Scraper TOUTES les Pages
```python
scraper.scrape_vehicles(pages=1000)  # Peut prendre 24h
```

### Augmenter Délais (si bloqué)
```python
scraper.config['delay_min'] = 5
scraper.config['delay_max'] = 15
scraper.scrape_vehicles(pages=5)
```

### Analyser Prix
```python
from stats import StatsAnalyzer

analyzer = StatsAnalyzer('leboncoin_vehicles.db')
avg_price = analyzer.get_average_price()
print(f"Prix moyen: {avg_price}€")
```

### Exporter en CSV
```python
from report_generator import ReportGenerator

gen = ReportGenerator('leboncoin_vehicles.db')
gen.export_to_csv('export.csv')
```

---

## 📁 Fichiers Importants

| Fichier | Utilité |
|---------|---------|
| `leboncoin_scraper.py` | Scraper principal |
| `report_generator.py` | Génération rapports |
| `stats.py` | Analyses statistiques |
| `leboncoin_vehicles.db` | Base de données |
| `leboncoin_rapport.html` | Rapport interactif |
| `.env` | Configuration |

---

## 🔗 Ressources Utiles

### Documentation Complète
- 📖 [README.md](README.md) - Vue d'ensemble
- 🏗️ [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Architecture système
- 📚 [docs/INSTALLATION.md](docs/INSTALLATION.md) - Installation détaillée
- 🌐 [GUIDE_WEB_SCRAPING.md](GUIDE_WEB_SCRAPING.md) - Guide scraping

### Contribution
- 🤝 [CONTRIBUTING.md](CONTRIBUTING.md) - Comment contribuer
- 📋 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) - Code de conduite
- 📝 [CHANGELOG.md](CHANGELOG.md) - Historique versions

---

## 🆘 Besoin d'Aide ?

### Problèmes Courants

**Erreur : `ModuleNotFoundError`**
```bash
# Environnement virtuel non activé
source env/bin/activate  # macOS/Linux
.\env\Scripts\Activate.ps1  # Windows
```

**Erreur : `403 Forbidden`**
```python
# Augmenter délai entre requêtes
scraper.config['delay_min'] = 10
scraper.config['delay_max'] = 20
```

**Arrêt du scraping**
```python
# Vérifier internet, réessayer
# Consulter scraper.log pour détails
```

### Plus d'Aide
- 📖 Lire [docs/INSTALLATION.md](docs/INSTALLATION.md) section Dépannage
- 🐛 Ouvrir une Issue sur GitHub
- 📧 Contacter [ton.email@example.com](mailto:ton.email@example.com)

---

## 💡 Astuces Pro

### 1. Utiliser des Logs Détaillés
```python
import logging
logging.basicConfig(level=logging.DEBUG)
scraper = LeBonCoinScraper()
scraper.scrape_vehicles(pages=2)
```

### 2. Scraper Progressivement
```python
# Jour 1: 5 pages
scraper.scrape_vehicles(pages=5)

# Jour 2: 5 pages de plus
scraper.scrape_vehicles(pages=5)

# Données s'accumulent dans la même DB
```

### 3. Monitorer la Base de Données
```bash
# Voir nombre de lignes
sqlite3 leboncoin_vehicles.db "SELECT COUNT(*) FROM vehicles;"

# Voir dernière annonce
sqlite3 leboncoin_vehicles.db "SELECT * FROM vehicles ORDER BY created_at DESC LIMIT 1;"
```

### 4. Exporter Périodiquement
```bash
# Backup au format CSV tous les jours
sqlite3 leboncoin_vehicles.db ".mode csv" ".output leboncoin_backup.csv" "SELECT * FROM vehicles;"
```

---

## 📊 Statistiques Rapides

```bash
# Nombre total annonces
sqlite3 leboncoin_vehicles.db "SELECT COUNT(*) FROM vehicles;"

# Prix moyen
sqlite3 leboncoin_vehicles.db "SELECT AVG(price) FROM vehicles;"

# Répartition énergie
sqlite3 leboncoin_vehicles.db "SELECT energy, COUNT(*) FROM vehicles GROUP BY energy;"

# Prix par marque
sqlite3 leboncoin_vehicles.db "SELECT brand, AVG(price) FROM vehicles GROUP BY brand ORDER BY AVG(price) DESC LIMIT 10;"
```

---

## ⚙️ Configuration Minimale vs Maximale

### Scraping Léger (Quick Test)
```python
config = {
    'pages': 2,              # 2 pages = 50 annonces
    'delay_min': 1,
    'delay_max': 3,
    'download_images': False,  # Pas de photos
}
# Durée: ~2 minutes
```

### Scraping Complet (Full Analysis)
```python
config = {
    'pages': 100,            # 100 pages = 2500 annonces
    'delay_min': 5,
    'delay_max': 10,
    'download_images': True,   # Télécharger photos
    'image_quality': 'high',
}
# Durée: ~24 heures
```

---

## 🎓 Apprentissage

### Débutant
1. Lire README.md
2. Lancer première installation
3. Faire scraping de 2 pages
4. Consulter rapport HTML

### Intermédiaire
1. Lire GUIDE_WEB_SCRAPING.md
2. Étudier leboncoin_scraper.py
3. Modifier configuration .env
4. Analyser statistiques

### Avancé
1. Consulter docs/ARCHITECTURE.md
2. Comprendre AntiDetectionManager
3. Implémenter modifications
4. Contribuer au projet

---

## 🚀 Prochaines Étapes

- ✅ Installation réussie
- ✅ Scraping de test fait
- ✅ Rapport HTML consultable

Maintenant :
1. **Scraper plus de pages** pour plus de données
2. **Analyser les tendances** prix/marque
3. **Contribuer** avec des améliorations
4. **Partager** vos découvertes !

---

## 📱 Version Mobile

Pour utiliser sur mobile/VPS :
```bash
# Installer screen pour laisser running
sudo apt-get install screen

# Lancer scraper en arrière-plan
screen -S leboncoin
python leboncoin_scraper.py
# Ctrl+A puis D pour detach

# Retrouver session
screen -r leboncoin
```

---

## 🎉 Bonne Chance !

**Besoin de plus d'aide ?** Consultez la documentation complète 📚
