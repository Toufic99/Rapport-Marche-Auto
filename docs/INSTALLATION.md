# 🚀 Guide d'Installation Détaillé

## Prérequis Système

### Windows
- ✅ Windows 7+ ou Windows Server 2012+
- ✅ [Python 3.8+](https://www.python.org/downloads/)
- ✅ [Git for Windows](https://git-scm.com/download/win)

### macOS
- ✅ macOS 10.9+
- ✅ [Homebrew](https://brew.sh/) (optionnel)
- ✅ Python 3.8+ (via Homebrew ou python.org)

### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv git
```

---

## 📦 Installation Étape par Étape

### 1. Cloner le Repository

```bash
# Via HTTPS
git clone https://github.com/[TON_USERNAME]/leboncoin-scraper.git
cd leboncoin-scraper

# Ou via SSH (si clé SSH configurée)
git clone git@github.com:[TON_USERNAME]/leboncoin-scraper.git
cd leboncoin-scraper
```

### 2. Créer un Environnement Virtuel

L'environnement virtuel **isole** les dépendances du projet.

#### Windows (PowerShell)
```powershell
# Créer l'environnement
python -m venv env

# Activer l'environnement
.\env\Scripts\Activate.ps1

# (Si erreur de permission, lancer PowerShell en Admin)
```

#### Windows (Command Prompt)
```cmd
python -m venv env
env\Scripts\activate.bat
```

#### macOS / Linux
```bash
# Créer l'environnement
python3 -m venv env

# Activer l'environnement
source env/bin/activate
```

✅ **Vérifier l'activation** : Votre terminal doit afficher `(env)` au début

### 3. Mettre à Jour pip

```bash
# Windows
python -m pip install --upgrade pip

# macOS / Linux
python3 -m pip install --upgrade pip
```

### 4. Installer les Dépendances

```bash
# Installer depuis requirements.txt
pip install -r requirements.txt

# Ou installer manuellement
pip install requests beautifulsoup4 lxml pandas python-dotenv tqdm colorama
```

✅ **Vérifier l'installation** :
```bash
pip list
```

### 5. Configurer les Variables d'Environnement

```bash
# Créer fichier .env
cp .env.example .env  # macOS/Linux
copy .env.example .env  # Windows

# Éditer .env avec votre éditeur
# Les valeurs par défaut sont généralement OK
```

Contenu `.env` typique :
```bash
# Scraping
REQUEST_TIMEOUT=10
MAX_RETRIES=3
DELAY_BETWEEN_REQUESTS=2

# Database
DB_PATH=./leboncoin_vehicles.db

# Logging
LOG_LEVEL=INFO
```

---

## 🧪 Vérifier l'Installation

### Test Import
```bash
python -c "import requests, bs4, pandas; print('✅ Dépendances OK')"
```

### Test Base de Données
```bash
python -c "import sqlite3; print(sqlite3.version)"
```

### Lancer les Tests
```bash
# Si pytest est installé
pytest tests/

# Ou tester directement
python -c "from leboncoin_scraper import LeBonCoinScraper; print('✅ Import OK')"
```

---

## ▶️ Premier Lancement

### 1. Lancer un Scraping de Test

```bash
# Scraper 2 pages (environ 50 véhicules)
python -c "
from leboncoin_scraper import LeBonCoinScraper

scraper = LeBonCoinScraper()
scraper.scrape_vehicles(pages=2)
print('✅ Scraping terminé !')
"
```

### 2. Vérifier les Résultats

```bash
# Vérifier les fichiers créés
ls -la  # macOS/Linux
dir    # Windows

# Fichiers attendus:
# - leboncoin_vehicles.db (base de données)
# - voitures_photos/ (dossier avec images)
```

### 3. Générer le Rapport

```bash
python -c "
from leboncoin_scraper import LeBonCoinScraper
from report_generator import ReportGenerator

# Générer rapport HTML
gen = ReportGenerator('leboncoin_vehicles.db')
gen.generate_html_report()
print('✅ Rapport généré: leboncoin_rapport.html')
"
```

### 4. Ouvrir le Rapport

```bash
# Windows
start leboncoin_rapport.html

# macOS
open leboncoin_rapport.html

# Linux
xdg-open leboncoin_rapport.html
```

---

## 🐛 Dépannage

### Erreur : `ModuleNotFoundError: No module named 'requests'`
```bash
# Environnement virtuel non activé
# Solution: Relancer activation
source env/bin/activate  # macOS/Linux
.\env\Scripts\Activate.ps1  # Windows PowerShell
```

### Erreur : `ConnectionError`
```bash
# Problème de connexion réseau
# Vérifier:
1. Connexion Internet OK
2. Proxy/Firewall bloquant ?
3. Site LeBonCoin down ?

# Tester connexion
python -c "import requests; r=requests.get('https://google.com'); print('OK')"
```

### Erreur : `HTTPError 403 Forbidden`
```bash
# Site vous a bloqué temporairement
# Solution: Attendre 30 minutes et réessayer
# Ou réduire nombre de pages / ajouter délai

# Dans code:
scraper.config['delay_min'] = 3
scraper.config['delay_max'] = 8
```

### Base de Données Verrouillée
```bash
# Si erreur "database is locked"
# Solution: Fermer les processus Python
# Ou attendre 5 secondes

# Vérifier processus (Windows)
tasklist | findstr python

# Terminer processus
taskkill /IM python.exe /F
```

### Problèmes de Permissions (Linux/macOS)
```bash
# Si erreur "Permission denied"
chmod +x leboncoin_scraper.py

# Ou accorder droits au dossier
chmod -R 755 ./
```

---

## 🔧 Configuration Avancée

### Augmenter Nombre de Pages

```python
from leboncoin_scraper import LeBonCoinScraper

scraper = LeBonCoinScraper()
scraper.scrape_vehicles(pages=100)  # Au lieu de 10
```

### Ajuster Délais Anti-Détection

```python
config = {
    'delay_min': 2,      # Minimum 2 secondes
    'delay_max': 10,     # Maximum 10 secondes
    'timeout': 15,       # Timeout augmenté
}
scraper.config.update(config)
scraper.scrape_vehicles(pages=50)
```

### Télécharger Images en Qualité Haute

```python
scraper.config['image_quality'] = 'high'
scraper.scrape_vehicles(pages=10)
```

---

## 📊 Utilisation Complète

### Script Complet

```python
#!/usr/bin/env python3
"""
Script complet de scraping avec rapport
"""

from leboncoin_scraper import LeBonCoinScraper
from report_generator import ReportGenerator
from stats import StatsAnalyzer
import os

def main():
    print("🚗 LeBonCoin Auto Scraper")
    print("=" * 50)
    
    # 1. SCRAPING
    print("\n1️⃣ Scraping des annonces...")
    scraper = LeBonCoinScraper()
    scraper.scrape_vehicles(pages=10)  # 10 pages = ~250 annonces
    print("✅ Scraping terminé")
    
    # 2. ANALYSE STATISTIQUES
    print("\n2️⃣ Analyse statistiques...")
    analyzer = StatsAnalyzer('leboncoin_vehicles.db')
    stats = analyzer.get_summary()
    print(f"   Total: {stats['total']} annonces")
    print(f"   Prix moyen: {stats['avg_price']}€")
    print(f"   Kilométrage moyen: {stats['avg_km']} km")
    
    # 3. GÉNÉRATION RAPPORT
    print("\n3️⃣ Génération rapport HTML...")
    gen = ReportGenerator('leboncoin_vehicles.db')
    gen.generate_html_report()
    gen.export_to_csv()
    print("✅ Rapport généré: leboncoin_rapport.html")
    
    # 4. STATISTIQUES
    print("\n4️⃣ Statistiques par énergie:")
    for energy, count in analyzer.get_energy_distribution().items():
        print(f"   {energy}: {count} véhicules")
    
    print("\n" + "=" * 50)
    print("✅ Scraping terminé avec succès !")
    print("📊 Ouvrez leboncoin_rapport.html pour voir les résultats")

if __name__ == '__main__':
    main()
```

Lancer le script :
```bash
python main.py
```

---

## ✅ Checklist Post-Installation

- [ ] Python 3.8+ installé
- [ ] Environnement virtuel créé et activé
- [ ] Dépendances installées (`pip list` affiche requests, bs4, etc.)
- [ ] Fichier `.env` configuré
- [ ] Premier scraping testé (2 pages OK)
- [ ] Rapport HTML généré avec succès
- [ ] Images téléchargées dans `voitures_photos/`

---

## 📞 Support

Si vous rencontrez des problèmes :

1. **Vérifier la section Dépannage** ci-dessus
2. **Consulter** `docs/TROUBLESHOOTING.md`
3. **Ouvrir une Issue** sur GitHub
4. 📞 **Contacter**: [toufic.bathish123@gmail.com](mailto:toufic.bathish123@gmail.com)

---

## 🎉 Prochaines Étapes

✅ Installation réussie ? Maintenant :

1. Lire `README.md` pour aperçu général
2. Explorer `GUIDE_WEB_SCRAPING.md` pour techniques
3. Consulter `docs/ARCHITECTURE.md` pour structure du code
4. Exécuter `EXERCICES_SCRAPING.py` pour pratiquer

**Bon scraping ! 🚀**
