# 🎓 GUIDE COMPLET - WEB SCRAPING (LeBonCoin)

## Table des matières
1. [Fondamentaux](#fondamentaux)
2. [Problèmes rencontrés & Solutions](#problèmes-rencontrés--solutions)
3. [Architecture du Scraper](#architecture-du-scraper)
4. [Code de base](#code-de-base)
5. [Anti-détection](#anti-détection)
6. [Gestion des erreurs](#gestion-des-erreurs)
7. [Bonnes pratiques](#bonnes-pratiques)

---

## FONDAMENTAUX

### Qu'est-ce que le web scraping ?
**Extraire des données d'un site web en automatisant la récupération HTML/JSON.**

### 3 étapes simples :
```
1. Envoyer une requête HTTP (GET/POST)
2. Récupérer la réponse (HTML/JSON)
3. Parser les données (BeautifulSoup, regex, JSON)
```

### Outils principaux :
- **requests** : Envoyer des requêtes HTTP
- **BeautifulSoup** : Parser du HTML
- **sqlite3** : Stocker les données
- **json** : Parser du JSON

---

## PROBLÈMES RENCONTRÉS & SOLUTIONS

### 🔴 PROBLÈME 1 : IP Bloquée (403 Forbidden)

**Symptôme :** 
```
requests.exceptions.HTTPError: 403 Client Error: Forbidden
```

**Cause :**
- Le serveur détecte plusieurs requêtes du même IP
- LeBonCoin rate-limite après ~10 requêtes rapides

**Solution 1 - Attendre ✅**
```python
import time
time.sleep(5)  # Attendre 5 secondes entre requêtes
```

**Solution 2 - User-Agent rotation ✅**
```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0'
}
response = requests.get(url, headers=headers)
```

**Solution 3 - VPN/Proxy (facultatif)**
```python
proxies = {
    'http': 'http://proxy:port',
    'https': 'http://proxy:port'
}
response = requests.get(url, proxies=proxies)
```

**Solution 4 - Pause longue si 403 ✅ (NOTRE APPROCHE)**
```python
try:
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 403:
        print("⏸️ 403 Forbidden - Pause 5 minutes...")
        time.sleep(300)  # 5 minutes
        return scrape_leboncoin()  # Réessayer
```

---

### 🔴 PROBLÈME 2 : Site utilise Next.js (JavaScript client-side rendering)

**Symptôme :**
```
- HTML vide ou incomplet
- Pas de données dans les balises
- Données chargées en JavaScript
```

**Cause :**
- LeBonCoin utilise Next.js (rendu côté client)
- Les annonces sont chargées en AJAX/JSON, pas en HTML statique

**Mauvaise approche ❌ :**
```python
soup = BeautifulSoup(response.text, 'html.parser')
# Trouve rien car les données ne sont pas dans l'HTML brut
```

**Bonne approche ✅ :**
1. **Inspecter le code source** (F12 → Network → XHR)
2. **Chercher l'API JSON**
3. **Extraire depuis `__NEXT_DATA__` script tag**

```python
# Extraction du JSON depuis script tag
soup = BeautifulSoup(response.text, 'html.parser')
script = soup.find('script', {'id': '__NEXT_DATA__'})
if script:
    data = json.loads(script.string)
    # Accéder aux annonces
    ads = data['props']['pageProps']['ads']
```

**Alternative : Utiliser API directement**
```python
# LeBonCoin expose une API
api_url = "https://api.leboncoin.fr/api/v1/search"
params = {'limit': 20, 'offset': 0}
response = requests.get(api_url, params=params, headers=headers)
data = response.json()
```

---

### 🔴 PROBLÈME 3 : Structure HTML change

**Symptôme :**
```
IndexError ou KeyError lors du parsing
Les sélecteurs CSS/XPath ne trouvent rien
```

**Cause :**
- Le site change sa structure HTML
- Nos sélecteurs ne correspondent plus

**Solution :**
```python
# JAMAIS faire ça ❌
price = soup.find('div', class_='price').text

# TOUJOURS ajouter des vérifications ✅
price_div = soup.find('div', class_='price')
price = price_div.text if price_div else 'N/A'

# Ou avec try/except
try:
    price = soup.find('div', class_='price').text
except (AttributeError, IndexError):
    price = 'N/A'
```

---

### 🔴 PROBLÈME 4 : Connexion timeout

**Symptôme :**
```
requests.exceptions.Timeout: Connection timeout
```

**Cause :**
- Serveur lent
- Connexion réseau instable

**Solution :**
```python
try:
    response = requests.get(url, timeout=10)  # 10 secondes max
except requests.exceptions.Timeout:
    print("Timeout - Réessayer...")
    time.sleep(5)
    return requests.get(url, timeout=15)  # Réessayer avec plus de temps
```

---

### 🔴 PROBLÈME 5 : Encodage des caractères (UTF-8)

**Symptôme :**
```
é, à, ç deviennent des caractères bizarres
```

**Cause :**
- Mauvais encodage lors du parsing

**Solution :**
```python
# Définir l'encodage dès le début
response = requests.get(url, headers=headers)
response.encoding = 'utf-8'

# Ou avec BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser', from_encoding='utf-8')
```

---

### 🔴 PROBLÈME 6 : Télécharger les images

**Symptôme :**
```
Photos ne se téléchargent pas
Erreurs 404 sur les URLs
```

**Cause :**
- URL d'image cassée ou protégée
- Format de donnée inattendu

**Solution - Robuste ✅ :**
```python
import os
import requests
from urllib.parse import urlparse

def download_photo(photo_url, folder='photos'):
    try:
        # Créer le dossier si nécessaire
        os.makedirs(folder, exist_ok=True)
        
        # Vérifier si l'URL est valide
        if not photo_url or not photo_url.startswith('http'):
            return None
        
        # Télécharger avec timeout
        response = requests.get(photo_url, timeout=10, headers=headers)
        response.raise_for_status()
        
        # Générer le nom du fichier
        filename = os.path.join(folder, os.path.basename(urlparse(photo_url).path))
        
        # Sauvegarder
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        return filename
    
    except Exception as e:
        print(f"Erreur téléchargement photo: {e}")
        return None
```

---

## ARCHITECTURE DU SCRAPER

### Structure recommandée :
```
scraper.py
├── AntiDetectionManager       # Gère les headers, délais
├── DatabaseManager            # CRUD SQLite
├── PhotoDownloader            # Télécharge les images
└── MainScraper               # Logique principale
```

### Flow principal :
```
1. Initialiser le scraper
2. Pour chaque page :
   a. Envoyer requête
   b. Parser les données
   c. Sauvegarder en DB
   d. Télécharger les photos
   e. Attendre avant la page suivante
3. Générer un rapport
```

---

## CODE DE BASE

### Scraper minimal :
```python
import requests
from bs4 import BeautifulSoup
import sqlite3
import time

# 1. Envoyer requête
url = "https://www.leboncoin.fr/voitures/offres/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers, timeout=10)
response.raise_for_status()

# 2. Parser HTML
soup = BeautifulSoup(response.text, 'html.parser')

# 3. Extraire les données
annonces = []
for item in soup.find_all('article', class_='announce'):
    try:
        title = item.find('h2').text.strip()
        price = item.find('div', class_='price').text.strip()
        annonces.append({'title': title, 'price': price})
    except AttributeError:
        continue

# 4. Sauvegarder en DB
conn = sqlite3.connect('voitures.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS vehicles
             (id INTEGER PRIMARY KEY, title TEXT, price TEXT)''')
for annonce in annonces:
    c.execute("INSERT INTO vehicles VALUES (NULL, ?, ?)", 
              (annonce['title'], annonce['price']))
conn.commit()
conn.close()

print(f"✅ {len(annonces)} annonces sauvegardées")
```

---

## ANTI-DÉTECTION

### Headers réalistes ✅
```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'fr-FR,fr;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}
```

### Délais réalistes ✅
```python
import random
import time

# Délai aléatoire entre requêtes
def attendre():
    delay = random.uniform(2, 5)  # 2-5 secondes
    time.sleep(delay)

# Pause plus longue entre les pages
def pause_longue():
    delay = random.uniform(10, 20)  # 10-20 secondes
    time.sleep(delay)
```

### Session persistante ✅
```python
import requests

session = requests.Session()
session.headers.update(headers)

# Réutiliser la même session (garde les cookies)
response1 = session.get(url1)
time.sleep(3)
response2 = session.get(url2)
```

### Gestion du rate-limiting ✅
```python
def scrape_avec_retry(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                print(f"⏸️ 403 Forbidden - Pause 5 minutes (tentative {attempt+1}/{max_retries})")
                time.sleep(300)
            else:
                raise
    raise Exception("Trop de tentatives échouées")
```

---

## GESTION DES ERREURS

### Pattern robuste ✅
```python
try:
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    data = soup.find('div', class_='data')
    
    if not data:
        print("⚠️ Pas de données trouvées")
        return []
    
    result = data.text.strip()
    
except requests.exceptions.Timeout:
    print("❌ Timeout - Serveur ne répond pas")
    return []

except requests.exceptions.HTTPError as e:
    if e.response.status_code == 403:
        print("❌ IP bloquée (403)")
    elif e.response.status_code == 404:
        print("❌ Page non trouvée (404)")
    else:
        print(f"❌ Erreur HTTP {e.response.status_code}")
    return []

except requests.exceptions.ConnectionError:
    print("❌ Erreur connexion - Vérifier internet")
    return []

except Exception as e:
    print(f"❌ Erreur inattendue: {e}")
    return []

return result
```

---

## BONNES PRATIQUES

### ✅ À FAIRE

1. **Respecter le site**
   - Ajouter un délai entre requêtes
   - Ne pas faire 100 requêtes par minute
   - Vérifier le `robots.txt`

2. **Vérifier légalement**
   - Lire les conditions d'utilisation
   - Respecter la RGPD (données personnelles)
   - Ne pas utiliser les données à des fins malveillantes

3. **Code robuste**
   - Toujours ajouter `timeout`
   - Toujours utiliser `try/except`
   - Vérifier que les éléments existent avant d'y accéder

4. **Logging**
   ```python
   import logging
   logging.basicConfig(level=logging.INFO)
   logger = logging.getLogger(__name__)
   logger.info(f"✅ {count} annonces scrappées")
   ```

5. **Base de données**
   - Utiliser une clé unique (URL, ID)
   - Vérifier les doublons avant d'insérer
   - Faire des backups réguliers

### ❌ À ÉVITER

1. **Scraper sans délai**
   ```python
   # ❌ MAUVAIS
   for page in range(100):
       response = requests.get(f"url/page{page}")
   ```

2. **Ignorer les erreurs**
   ```python
   # ❌ MAUVAIS
   soup.find('div', class_='data').text  # Crash si pas trouvé
   ```

3. **User-Agent par défaut**
   ```python
   # ❌ MAUVAIS
   response = requests.get(url)  # Detecté facilement
   ```

4. **Pas de vérification de structure**
   ```python
   # ❌ MAUVAIS
   price = response.text.split("€")[0]  # Très fragile
   ```

---

## RECAP - CHECKLIST POUR UN ENTRETIEN

**Si tu dois faire un scraper en entretien :**

- [ ] Demander la permission (vérifier robots.txt, ToS)
- [ ] Utiliser `requests` et `BeautifulSoup`
- [ ] Ajouter des `User-Agent` réalistes
- [ ] Ajouter des délais entre requêtes
- [ ] Gérer les erreurs (try/except)
- [ ] Ajouter un `timeout` (10-15 secondes)
- [ ] Vérifier que les éléments existent
- [ ] Sauvegarder en JSON ou SQLite
- [ ] Afficher le nombre d'éléments scrappés

**Réponse type :**
> "Je commencerais par inspecter le site (F12), identifier la source des données (HTML ou API), puis utiliser BeautifulSoup pour parser. J'ajouterais des délais pour ne pas surcharger le serveur, je gèrerais les erreurs (403, timeout), et je sauvegarderais les données de manière fiable en base de données."

---

## EXEMPLES CONCRETS

### Scraper une liste de produits
```python
import requests
from bs4 import BeautifulSoup
import time

def scrape_products(url):
    headers = {'User-Agent': 'Mozilla/5.0...'}
    products = []
    
    for page in range(1, 4):  # 3 pages
        try:
            # Requête
            response = requests.get(
                f"{url}?page={page}",
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            # Parse
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for item in soup.find_all('div', class_='product'):
                name = item.find('h2').text.strip() if item.find('h2') else 'N/A'
                price = item.find('span', class_='price').text.strip() if item.find('span', class_='price') else 'N/A'
                products.append({'name': name, 'price': price})
            
            print(f"✅ Page {page}: {len(soup.find_all('div', class_='product'))} produits")
            
            # Délai
            time.sleep(random.uniform(2, 5))
        
        except Exception as e:
            print(f"❌ Erreur page {page}: {e}")
            continue
    
    return products

# Utilisation
products = scrape_products("https://example.com/products")
print(f"Total: {len(products)} produits")
```

---

## RESSOURCES UTILES

- **Inspecter un site :** F12 (DevTools)
- **Parser HTML :** BeautifulSoup4
- **Parser JSON :** `json` module
- **Faire requêtes :** `requests` library
- **Base de données :** SQLite3
- **Planifier :** Windows Task Scheduler (ou cron sur Linux)

