"""
🎓 EXERCICES WEB SCRAPING - Pour s'entraîner avant un entretien
Difficulté croissante : débutant → intermédiaire → avancé
"""

# ========================================
# EXERCICE 1 - DÉBUTANT
# ========================================
print("=" * 50)
print("EXERCICE 1 - Scraper une API publique")
print("=" * 50)

"""
OBJECTIF: Scraper les données météo d'une API publique
SITE: https://api.open-meteo.com/v1/forecast (API gratuite, pas besoin d'API key)
DONNÉES A EXTRAIRE: Température, humidité, vitesse vent

STEPS:
1. Faire une requête GET avec les bons paramètres
2. Parser la réponse JSON
3. Afficher les résultats
4. Gérer les erreurs

BONUS: Sauvegarder en CSV

HINT: Les paramètres sont: latitude, longitude, hourly
"""

# À FAIRE (solution en bas)
print("\n💡 Indice: Utilise requests.get() et response.json()")
print("Starter code:")
print("""
import requests

url = "https://api.open-meteo.com/v1/forecast"
params = {
    'latitude': 48.8566,  # Paris
    'longitude': 2.3522,
    'hourly': 'temperature_2m,relative_humidity_2m,weather_code'
}

try:
    response = requests.get(url, params=params, timeout=10)
    # À COMPLÉTER...
except Exception as e:
    print(f"Erreur: {e}")
""")

# ========================================
# EXERCICE 2 - INTERMÉDIAIRE
# ========================================
print("\n" + "=" * 50)
print("EXERCICE 2 - Scraper du HTML avec BeautifulSoup")
print("=" * 50)

"""
OBJECTIF: Scraper une liste de repos GitHub populaires
SITE: https://github.com/trending (liste des repos tendance)
DONNÉES A EXTRAIRE: Nom du repo, owner, stars, langage, description

STRUCTURE HTML (simplifié):
<article class="Box-row">
    <h2>
        <a href="/user/repo">user/repo</a>
    </h2>
    <p class="col-9">Description du repo</p>
    <span class="d-inline-block">⭐ 1.2k</span>
</article>

STEPS:
1. Envoyer une requête
2. Parser le HTML
3. Extraire tous les repos
4. Afficher dans un tableau
5. Gérer les erreurs

BONUS: Sauvegarder en SQLite
"""

print("\n💡 Indice: Utilise soup.find_all('article') et un try/except")

# ========================================
# EXERCICE 3 - AVANCÉ
# ========================================
print("\n" + "=" * 50)
print("EXERCICE 3 - Scraper avec pagination + anti-détection")
print("=" * 50)

"""
OBJECTIF: Scraper plusieurs pages d'un site avec protection
SITE: https://quotes.toscrape.com (site d'entraînement)
DONNÉES: Quotes, authors, tags

CHALLENGE:
- 10 pages à scraper
- Ajouter des délais réalistes
- Ajouter un User-Agent custom
- Gérer les timeouts
- Afficher une progress bar
- Sauvegarder en CSV

STRUCTURE:
https://quotes.toscrape.com/page/1/
https://quotes.toscrape.com/page/2/
...

HTML:
<div class="quote">
    <span class="text">"Le texte"</span>
    <small class="author">Auteur</small>
    <div class="tags">
        <a class="tag">tag1</a>
    </div>
</div>

STEPS:
1. Pour chaque page (1-10):
   a. Ajouter un délai aléatoire (2-5 sec)
   b. Envoyer requête avec User-Agent
   c. Parser les quotes
   d. Sauvegarder
   e. Afficher progress
2. Gérer les erreurs (403, timeout, etc)
3. Sauvegarder le tout en CSV

BONUS: Ajouter une session requests pour les cookies
"""

print("\n💡 Indice: Boucle for + time.sleep(random.uniform(2,5)) + csv.writer")

# ========================================
# SOLUTIONS PARTIELLES
# ========================================
print("\n" + "=" * 50)
print("SOLUTIONS (À NE REGARDER QUE SI BLOQUÉ!)")
print("=" * 50)

# Exercice 1 - Solution
print("\n📝 EXERCICE 1 - Solution:")
print("""
import requests

url = "https://api.open-meteo.com/v1/forecast"
params = {
    'latitude': 48.8566,
    'longitude': 2.3522,
    'hourly': 'temperature_2m,relative_humidity_2m'
}

try:
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    
    data = response.json()
    print(f"✅ Données reçues")
    print(f"Température: {data['hourly']['temperature_2m'][0]}°C")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
""")

# Exercice 2 - Solution
print("\n📝 EXERCICE 2 - Solution:")
print("""
import requests
from bs4 import BeautifulSoup

url = "https://github.com/trending"
headers = {'User-Agent': 'Mozilla/5.0...'}

try:
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    repos = []
    for article in soup.find_all('article', class_='Box-row'):
        try:
            link = article.find('h2').find('a')
            repo_name = link.text.strip()
            stars = article.find('span', class_='d-inline-block')
            
            repos.append({
                'name': repo_name,
                'stars': stars.text.strip() if stars else 'N/A'
            })
        except AttributeError:
            continue
    
    print(f"✅ {len(repos)} repos trouvés")
    for repo in repos[:5]:
        print(repo)
        
except Exception as e:
    print(f"❌ Erreur: {e}")
""")

# Exercice 3 - Solution
print("\n📝 EXERCICE 3 - Solution (structure):")
print("""
import requests
from bs4 import BeautifulSoup
import time
import random
import csv

quotes = []
session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0...'})

for page in range(1, 11):
    try:
        url = f"https://quotes.toscrape.com/page/{page}/"
        response = session.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for quote_div in soup.find_all('div', class_='quote'):
            try:
                text = quote_div.find('span', class_='text').text
                author = quote_div.find('small', class_='author').text
                
                quotes.append({
                    'text': text,
                    'author': author,
                    'page': page
                })
            except AttributeError:
                continue
        
        print(f"✅ Page {page} ({len(quotes)} quotes au total)")
        time.sleep(random.uniform(2, 5))
        
    except Exception as e:
        print(f"❌ Erreur page {page}: {e}")

# Sauvegarder en CSV
with open('quotes.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['text', 'author', 'page'])
    writer.writeheader()
    writer.writerows(quotes)

print(f"\\n✅ {len(quotes)} quotes sauvegardées en CSV")
""")

print("\n" + "=" * 50)
print("💪 À TOI DE JOUER!")
print("Commence par l'exercice 1, puis 2, puis 3")
print("=" * 50)
