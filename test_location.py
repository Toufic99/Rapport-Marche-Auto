import requests
import re
from bs4 import BeautifulSoup

url = 'https://www.leboncoin.fr/ad/voitures/3067504541'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
r = requests.get(url, headers=headers, timeout=15)
html = r.text

print('=== ANALYSE HTML BRUT ===')
print(f'Taille HTML: {len(html)} caracteres')

# Chercher TOUS les codes postaux dans le HTML brut
codes_postaux = re.findall(r'\d{5}', html)
print(f'Codes postaux trouves: {set(codes_postaux)}')

# Sauvegarder le HTML pour analyse
with open('debug_html.txt', 'w', encoding='utf-8') as f:
    f.write(html)
print('HTML sauvegarde dans debug_html.txt')

# Chercher des mots cles de localisation
keywords = ['Limoges', 'Paris', 'Lyon', 'Marseille', 'Toulouse', 'Bordeaux', 'France', 'departement', 'region']
for kw in keywords:
    if kw.lower() in html.lower():
        print(f'Mot-cle trouve: {kw}')
