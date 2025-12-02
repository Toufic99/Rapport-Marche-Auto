# GUIDE COMPLET: WEB SCRAPING & MISES A JOUR QUOTIDIENNES

## 1. COMPARAISON: SELENIUM vs PLAYWRIGHT vs SIMPLE

### A. SELENIUM (WebDriver)
**Utilisation:** Automatiser un navigateur complet
**Pros:**
- Ouvre un vrai navigateur (Chrome, Firefox, Safari)
- Exécute le JavaScript
- Contourne certains blocages

**Cons:**
- ❌ Très lent (5-15 secondes par page)
- ❌ Instable (crashs fréquents)
- ❌ Consomme beaucoup de RAM (500-800 MB)
- ❌ Difficile à installer

**Quand l'utiliser:**
- Sites avec beaucoup de JavaScript
- Formulaires complexes
- Quand requêtes HTTP ne suffisent pas

**Exemple:**
```python
from selenium import webdriver
driver = webdriver.Chrome()
driver.get("https://example.com")
```

---

### B. PLAYWRIGHT (DevTools Protocol)
**Utilisation:** Automatiser un navigateur (version moderne de Selenium)
**Pros:**
- ✅ Plus rapide que Selenium (2-5 secondes)
- ✅ Très stable (peu de crashs)
- ✅ DevTools Protocol (meilleur support)
- ✅ Multi-navigateurs

**Cons:**
- Encore beaucoup de ressources
- Plus moderne = moins de documentation

**Quand l'utiliser:**
- Quand Selenium crash
- Sites très JavaScript-intensifs
- Besoin de stabilité

**Exemple:**
```python
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    page = p.chromium.launch().new_page()
    page.goto("https://example.com")
```

---

### C. SIMPLE (Requêtes HTTP + BeautifulSoup)
**Utilisation:** Parser du HTML statique
**Pros:**
- ✅ ULTRA RAPIDE (< 1 seconde)
- ✅ Très stable (pas de crashes)
- ✅ Léger (10 MB RAM)
- ✅ Facile à installer
- ✅ Facile à maîtriser

**Cons:**
- ❌ Ne peut pas exécuter JavaScript
- ❌ Ne contourne pas les blocages

**Quand l'utiliser:**
- ✅ LeBonCoin
- ✅ Sites statiques
- ✅ Scraping simple et fiable

**Exemple:**
```python
import requests
from bs4 import BeautifulSoup

response = requests.get("https://example.com")
soup = BeautifulSoup(response.content, 'html.parser')
elements = soup.find_all('a')
```

---

## 2. TABLEAU COMPARATIF FINAL

| Aspect | Selenium | Playwright | Simple |
|--------|----------|-----------|--------|
| Vitesse | 🐌 Lent | 🚶 Moyen | 🚀 Ultra rapide |
| Stabilité | ❌ Crashs | ✅ Stable | ✅ Stable |
| RAM | 500-800 MB | 300-500 MB | 10 MB |
| Apprentissage | 🔴 Difficile | 🟡 Moyen | 🟢 Facile |
| JS support | ✅ Oui | ✅ Oui | ❌ Non |
| Installation | 🔴 Complexe | 🟡 Moyen | 🟢 Simple |
| LeBonCoin | ❌ ❌ | ✅ OK | ✅✅✅ PERFECT |

**VERDICT POUR TON CAS:** Utilise `leboncoin_simple.py` ✅

---

## 3. SOURCES DE DONNEES ACTIVES vs PASSIVES

### Données ACTIVES (mises à jour en temps réel):
- **LeBonCoin** → Nouvelles annonces chaque heure
- **Facebook Marketplace** → Nouvelles annonces chaque heure
- **Tout site web** → Si le contenu change

### Données PASSIVES (statiques):
- **CSV local** (`voitures_poitiers_analysees.csv`) → Créé une fois, ne change pas
- **Fichiers Excel** → Sauf si mis à jour manuellement

---

## 4. MISE A JOUR QUOTIDIENNE: COMMENT FAIRE?

### OPTION 1: Windows Task Scheduler (RECOMMANDE)

**Étapes:**
1. Double-clic sur `create_task.bat` (EN TANT QU'ADMIN)
2. La tâche s'exécutera chaque jour à 14h00

**Vérifier:**
```powershell
schtasks /query /tn "LeBonCoin Scraper Daily" /v
```

**Résultat:**
- Chaque jour à 14h00: Exécution automatique de `leboncoin_simple.py`
- Nouveau CSV généré: `leboncoin_voitures.csv`
- Log sauvegardé: `scraping_logs.txt`

---

### OPTION 2: Script Python avec planification

**Installer `schedule`:**
```powershell
.\TripoEnv\Scripts\pip install schedule
```

**Créer `scheduler.py`:**
```python
import schedule
import time
import subprocess

def job():
    subprocess.run([
        r'C:\...\TripoEnv\Scripts\python.exe',
        'leboncoin_simple.py'
    ])

schedule.every().day.at("14:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(60)
```

**Exécuter:**
```powershell
.\TripoEnv\Scripts\python.exe scheduler.py
```

⚠️ Attention: Doit rester ouvert en permanence

---

### OPTION 3: Cron Job (Linux/Mac)

```bash
# Exécuter chaque jour à 14h00
0 14 * * * /usr/bin/python3 /path/to/leboncoin_simple.py
```

---

## 5. WORKFLOW COMPLET: MISE A JOUR QUOTIDIENNE

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Task Scheduler déclenche le job chaque jour à 14h00      │
├─────────────────────────────────────────────────────────────┤
│ 2. leboncoin_simple.py exécuté                              │
│    - Requête HTTP à LeBonCoin                               │
│    - Parse HTML avec BeautifulSoup                          │
│    - 15 voitures récupérées                                 │
├─────────────────────────────────────────────────────────────┤
│ 3. CSV généré: leboncoin_voitures.csv (NOUVEAU)             │
│    - Titre, Prix, Lien, Date scraping                       │
├─────────────────────────────────────────────────────────────┤
│ 4. Options suivantes:                                       │
│    a) Merger avec CSV précédent (historique)                │
│    b) Envoyer email avec les nouvelles annonces             │
│    c) Uploader sur Cloud (Drive, S3, etc.)                  │
│    d) Analyser et alerter sur les prix                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. IMPLEMENTATION RAPIDE: PROCHAINES ETAPES

1. **Utiliser `leboncoin_simple.py`** (déjà prêt ✅)
2. **Planifier avec Task Scheduler:**
   ```
   Double-clic create_task.bat (EN TANT QU'ADMIN)
   ```
3. **Résultat:** Chaque jour à 14h → nouveau CSV avec données fraîches

---

## 7. COMMANDES UTILES

### Tester maintenant:
```powershell
.\TripoEnv\Scripts\python.exe leboncoin_simple.py
```

### Planifier:
```powershell
# Exécute create_task.bat EN TANT QU'ADMIN
.\create_task.bat
```

### Voir les tâches:
```powershell
schtasks /query /tn "LeBonCoin Scraper Daily" /v
```

### Exécuter maintenant:
```powershell
schtasks /run /tn "LeBonCoin Scraper Daily"
```

### Supprimer:
```powershell
schtasks /delete /tn "LeBonCoin Scraper Daily" /f
```

---

## RÉSUMÉ FINAL

✅ **Pour scraper LeBonCoin quotidiennement:**
1. Utilise `leboncoin_simple.py` (rapide, stable)
2. Planifie avec `create_task.bat` (automatique)
3. Résultat: CSV mis à jour chaque jour

🎯 **Pas besoin de Selenium ni Playwright pour LeBonCoin!**
