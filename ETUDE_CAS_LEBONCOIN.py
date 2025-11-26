"""
🔍 ÉTUDE DE CAS - LeBonCoin Scraper
Tous les problèmes rencontrés et leurs solutions
"""

# ========================================
# PROBLÈME #1 - IP BLOQUÉE (403 FORBIDDEN)
# ========================================

print("=" * 60)
print("PROBLÈME #1 - IP BLOQUÉE (403 FORBIDDEN)")
print("=" * 60)

PROBLEM = """
SYMPTÔMES:
- requests.exceptions.HTTPError: 403 Client Error: Forbidden
- Le scraper fonctionne 5 minutes puis s'arrête
- Après plusieurs pages, plus rien

CAUSE:
- LeBonCoin rate-limite après ~10-15 requêtes rapides
- Leur serveur bloque l'IP temporairement
- Typique des sites e-commerce (protection anti-bot)

CHRONOLOGIE DU BUG:
1. Scraper tourne bien (2-3 pages OK)
2. À la 4ème page → 403 Forbidden
3. Attendre 30 minutes → ça refonctionne
4. Mais on perd du temps!

SOLUTION FINALE:
✅ Détecter le 403 → Pause 5-10 minutes → Réessayer
✅ Ajouter User-Agent réaliste
✅ Ajouter délai entre chaque requête (2-5 sec)
✅ Utiliser une session pour partager les cookies
"""

SOLUTION_CODE = """
def scrape_leboncoin(url, max_retries=3):
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0'
    })
    
    for attempt in range(max_retries):
        try:
            print(f"📡 Tentative {attempt+1}/{max_retries}: {url}")
            response = session.get(url, timeout=15)
            response.raise_for_status()
            return response
        
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                if attempt < max_retries - 1:
                    print(f"⏸️ 403 Forbidden - Pause 5 minutes...")
                    time.sleep(300)  # 5 minutes
                else:
                    print("❌ Trop de tentatives échouées")
                    raise
            else:
                raise
"""

print(PROBLEM)
print("\nCODE SOLUTION:")
print(SOLUTION_CODE)

# ========================================
# PROBLÈME #2 - NEXT.JS ET JSON DANS SCRIPT TAG
# ========================================

print("\n" + "=" * 60)
print("PROBLÈME #2 - NEXT.JS ET JSON DANS SCRIPT TAG")
print("=" * 60)

PROBLEM2 = """
SYMPTÔMES:
- BeautifulSoup trouve l'HTML mais pas les annonces
- soup.find_all('article') retourne [] (vide)
- Les données ne sont PAS dans le HTML brut

CAUSE:
- LeBonCoin utilise Next.js (framework React)
- Les données sont chargées en JavaScript côté client
- L'HTML brut est vide, les annonces arrivent via AJAX

CHRONOLOGIE DU BUG:
1. Première approche: Parser directement le HTML
   → Trouve rien ❌
2. Deuxième approche: Utiliser Selenium/Playwright
   → Marche mais très lent (30 sec par page) ❌
3. Troisième approche: Chercher une API privée
   → LeBonCoin la bloque ❌
4. SOLUTION: Extraire le JSON du script tag __NEXT_DATA__
   → Marche parfaitement! ✅

L'APP NEXT.JS FAIT:
1. Charge le HTML vide
2. Dans le <head>, inclut <script id="__NEXT_DATA__">
3. Ce script contient TOUT le JSON des annonces
4. Le navigateur exécute le JS et affiche les annonces

NOTRE APPROCHE:
1. Récupérer l'HTML
2. Extraire le script tag __NEXT_DATA__
3. Parser le JSON
4. Extraire les annonces du JSON
"""

SOLUTION_CODE2 = """
import json
from bs4 import BeautifulSoup

response = requests.get(url, headers=headers, timeout=15)
soup = BeautifulSoup(response.text, 'html.parser')

# Chercher le script Next.js
script = soup.find('script', {'id': '__NEXT_DATA__'})

if not script:
    print("❌ Script __NEXT_DATA__ not found")
    return []

try:
    # Parser le JSON
    data = json.loads(script.string)
    
    # Naviguer jusqu'aux annonces
    # Structure: data['props']['pageProps']['ads']
    ads = data['props']['pageProps']['ads']
    
    print(f"✅ {len(ads)} annonces trouvées")
    
    for ad in ads:
        print(f"  - {ad['title']}: {ad['price']}€")
    
    return ads

except (json.JSONDecodeError, KeyError, TypeError) as e:
    print(f"❌ Erreur parsing JSON: {e}")
    return []
"""

print(PROBLEM2)
print("\nCODE SOLUTION:")
print(SOLUTION_CODE2)

# ========================================
# PROBLÈME #3 - MAUVAIS ENCODAGE UTF-8
# ========================================

print("\n" + "=" * 60)
print("PROBLÈME #3 - MAUVAIS ENCODAGE UTF-8")
print("=" * 60)

PROBLEM3 = """
SYMPTÔMES:
- é, è, ê, à, ç deviennent des caractères bizarres
- Exemple: "Peugeot" devient "PeuÂ«eot"
- Impossible de chercher les données en base

CAUSE:
- Encoding not set to UTF-8 quand on parse
- BeautifulSoup utilise un encoding par défaut (latin-1)

CHRONOLOGIE:
1. Scraper les annonces
2. Les sauvegarder en DB
3. Regarder le rapport CSV
4. Voir "Renault" écrit en charabia ❌

SOLUTION:
✅ Définir l'encoding UTF-8 dès le départ
"""

SOLUTION_CODE3 = """
import requests
from bs4 import BeautifulSoup

response = requests.get(url, headers=headers, timeout=15)

# IMPORTANT: Définir l'encoding
response.encoding = 'utf-8'

# Ou avec BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')

# Vérifier
title = soup.find('h1').text
print(f"Titre: {title}")  # ✅ Affichera correctement: "Renault Clio"
"""

print(PROBLEM3)
print("\nCODE SOLUTION:")
print(SOLUTION_CODE3)

# ========================================
# PROBLÈME #4 - STRUCTURE HTML CHANGE
# ========================================

print("\n" + "=" * 60)
print("PROBLÈME #4 - STRUCTURE HTML CHANGE")
print("=" * 60)

PROBLEM4 = """
SYMPTÔMES:
- Attributeerror ou IndexError aléatoire
- Le scraper crash sans raison
- Fonctionne un jour, pas le lendemain

CAUSE:
- LeBonCoin change sa structure HTML/JSON régulièrement
- Les sélecteurs CSS qu'on utilise deviennent invalides
- Ou l'API JSON ajoute/supprime des champs

EXEMPLE:
Jour 1: price = data['ads'][0]['price']  ✅ Marche
Jour 2: Ils changent la structure... IndexError ❌

SOLUTION:
✅ JAMAIS faire soup.find(...).text directement
✅ TOUJOURS vérifier que l'élément existe
✅ TOUJOURS utiliser try/except
✅ TOUJOURS utiliser des valeurs par défaut
"""

SOLUTION_CODE4 = """
# ❌ MAUVAIS - Crash si pas trouvé
price = soup.find('span', class_='price').text

# ✅ BON - Vérification
price_elem = soup.find('span', class_='price')
price = price_elem.text if price_elem else 'N/A'

# ✅ MEILLEUR - Try/except et log
try:
    price = soup.find('span', class_='price').text
    if not price:
        price = 'N/A'
except (AttributeError, TypeError):
    price = 'N/A'

# ✅ POUR JSON
price = data.get('price', 'N/A')  # Retourne 'N/A' si pas trouvé
price = data.get('price') or 'N/A'  # Si vide ou None
"""

print(PROBLEM4)
print("\nCODE SOLUTION:")
print(SOLUTION_CODE4)

# ========================================
# PROBLÈME #5 - TÉLÉCHARGER LES PHOTOS ÉCHOUE
# ========================================

print("\n" + "=" * 60)
print("PROBLÈME #5 - TÉLÉCHARGER LES PHOTOS ÉCHOUE")
print("=" * 60)

PROBLEM5 = """
SYMPTÔMES:
- Photos ne se téléchargent pas
- Erreurs 404 ou timeout
- Fichiers corrompus
- Noms de fichiers bizarres

CAUSES POSSIBLES:
1. URL d'image cassée ou protégée (require auth)
2. Image servie en base64 (pas une URL HTTP)
3. Timeout lors du téléchargement
4. Dossier de destination n'existe pas
5. Permissions insuffisantes

CHRONOLOGIE:
1. Parser les URLs de photos
2. Télécharger les images
3. 50% réussies, 50% échouées ❌
4. Comprendre qu'il faut être robuste

SOLUTION:
✅ Vérifier que l'URL est valide avant de télécharger
✅ Utiliser try/except pour chaque image
✅ Créer le dossier s'il n'existe pas
✅ Gérer les timeouts
✅ Utiliser un nom de fichier unique
"""

SOLUTION_CODE5 = """
import os
import requests
from urllib.parse import urlparse

def download_photo(photo_url, folder='photos'):
    try:
        # 1. Vérifier l'URL
        if not photo_url or not isinstance(photo_url, str):
            return None
        
        if not photo_url.startswith('http'):
            # C'est peut-être du base64 ou data URI
            return None
        
        # 2. Créer le dossier
        os.makedirs(folder, exist_ok=True)
        
        # 3. Générer un nom unique
        filename = os.path.basename(urlparse(photo_url).path)
        if not filename:
            filename = f"photo_{int(time.time())}.jpg"
        
        filepath = os.path.join(folder, filename)
        
        # 4. Télécharger avec timeout
        response = requests.get(photo_url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0...'
        })
        response.raise_for_status()
        
        # 5. Vérifier que c'est bien une image
        if 'image' not in response.headers.get('content-type', ''):
            print(f"⚠️ Pas une image: {photo_url}")
            return None
        
        # 6. Sauvegarder
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        return filepath
    
    except requests.exceptions.Timeout:
        print(f"⏱️ Timeout: {photo_url}")
        return None
    
    except requests.exceptions.HTTPError as e:
        print(f"❌ Erreur HTTP {e.response.status_code}: {photo_url}")
        return None
    
    except Exception as e:
        print(f"⚠️ Erreur: {e}")
        return None

# Utilisation
for ad in ads:
    for photo_url in ad.get('photos', []):
        path = download_photo(photo_url)
        if path:
            print(f"✅ Sauvegardée: {path}")
"""

print(PROBLEM5)
print("\nCODE SOLUTION:")
print(SOLUTION_CODE5)

# ========================================
# PROBLÈME #6 - BASE DE DONNÉES CORROMPUE
# ========================================

print("\n" + "=" * 60)
print("PROBLÈME #6 - BASE DE DONNÉES CORROMPUE")
print("=" * 60)

PROBLEM6 = """
SYMPTÔMES:
- Toutes les voitures sont marquées comme VENDUE
- Les prix sont tous à 0
- Données incomplètes ou NULL

CAUSE:
- Logique de détection des ventes incorrecte
- Pas de vérification avant d'update
- Doublons dans la DB

EXEMPLE RÉEL:
On a écrit une fonction detect_sales() qui:
- Cherche les annonces disparues
- Les marque comme VENDUE

MAIS:
- On l'a appelée alors qu'il n'y avait QUE les anciennes annonces
- Résultat: TOUTES marquées comme VENDUE! ❌

SOLUTION:
✅ Faire un backup avant d'exécuter un script de fix
✅ Ajouter des logs pour voir ce qui se passe
✅ Vérifier la logique sur un petit subset d'abord
"""

SOLUTION_CODE6 = """
import sqlite3
import shutil
import datetime

# 1. BACKUP avant de faire un fix
backup_path = f"leboncoin_vehicles_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
shutil.copy('leboncoin_vehicles.db', backup_path)
print(f"✅ Backup créé: {backup_path}")

# 2. Vérifier les données AVANT
conn = sqlite3.connect('leboncoin_vehicles.db')
c = conn.cursor()

c.execute("SELECT COUNT(*) FROM vehicles WHERE statut='ACTIVE'")
active_before = c.fetchone()[0]

c.execute("SELECT COUNT(*) FROM vehicles WHERE statut='VENDUE'")
sold_before = c.fetchone()[0]

print(f"AVANT: {active_before} ACTIVE, {sold_before} VENDUE")

# 3. Faire le fix avec vérifications
for vehicle_id, prix, added_date in vehicles_to_update:
    try:
        # Vérifier avant d'update
        if prix > 0 and added_date:
            c.execute(
                "UPDATE vehicles SET statut=? WHERE id=?",
                ('ACTIVE', vehicle_id)
            )
    except Exception as e:
        print(f"Erreur update {vehicle_id}: {e}")
        conn.rollback()
        break

conn.commit()

# 4. Vérifier APRÈS
c.execute("SELECT COUNT(*) FROM vehicles WHERE statut='ACTIVE'")
active_after = c.fetchone()[0]

c.execute("SELECT COUNT(*) FROM vehicles WHERE statut='VENDUE'")
sold_after = c.fetchone()[0]

print(f"APRÈS: {active_after} ACTIVE, {sold_after} VENDUE")

if active_after > 0:
    print("✅ Fix successful!")
else:
    print("❌ Quelque chose ne va pas - Restaurer le backup!")
    # Restaurer le backup
    shutil.copy(backup_path, 'leboncoin_vehicles.db')

conn.close()
"""

print(PROBLEM6)
print("\nCODE SOLUTION:")
print(SOLUTION_CODE6)

# ========================================
# RÉSUMÉ DES SOLUTIONS
# ========================================

print("\n" + "=" * 60)
print("RÉSUMÉ - CHECKLIST POUR ÉVITER CES PROBLÈMES")
print("=" * 60)

CHECKLIST = """
AVANT DE SCRAPER:
✅ Faire un backup de la DB si elle existe
✅ Vérifier robots.txt du site
✅ Vérifier les conditions d'utilisation

PENDANT LE SCRAPING:
✅ Ajouter User-Agent réaliste
✅ Ajouter délai entre requêtes (2-5 sec minimum)
✅ Utiliser une session requests
✅ Ajouter timeout (10-15 secondes)
✅ Try/except autour de chaque parse
✅ Vérifier que les éléments existent
✅ Gérer le 403 (pause longue)
✅ Gérer le timeout (retry)
✅ Garder les logs

APRÈS LE SCRAPING:
✅ Vérifier le nombre d'éléments scrappés
✅ Vérifier les données en DB (SELECT COUNT, SELECT TOP 5)
✅ Vérifier l'encodage UTF-8 dans le rapport
✅ Faire un backup régulier

POUR L'ENTRETIEN:
✅ Connaître tous ces problèmes
✅ Pouvoir les expliquer rapidement
✅ Montrer qu'on peut les résoudre
✅ Avoir une solution "robuste par défaut"
"""

print(CHECKLIST)
