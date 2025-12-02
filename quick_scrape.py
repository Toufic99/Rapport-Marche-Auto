"""Script rapide de scraping avec Selenium + Anti-détection"""
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time, re, sqlite3, os, random

os.makedirs('data', exist_ok=True)

# ============================================
# 🛡️ ANTI-DÉTECTION avec undetected_chromedriver
# ============================================

def random_delay(min_sec=2, max_sec=5):
    """Délai aléatoire pour simuler un humain"""
    time.sleep(random.uniform(min_sec, max_sec))

# Chrome avec undetected_chromedriver (anti-détection automatique)
options = uc.ChromeOptions()
options.add_argument('--window-size=1920,1080')
options.add_argument('--disable-notifications')

driver = uc.Chrome(options=options)
print('[1/4] Chrome OK (undetected-chromedriver)')

# Page liste
driver.get('https://www.leboncoin.fr/c/voitures')
random_delay(5, 8)

# Cookies
try:
    driver.find_element(By.ID, 'didomi-notice-agree-button').click()
    random_delay(2, 4)
except:
    pass

# Scroll naturel
for scroll_pos in [300, 600, 1000, 1500]:
    driver.execute_script(f'window.scrollTo(0, {scroll_pos});')
    random_delay(1, 2)

driver.execute_script('window.scrollTo(0, 500);')
random_delay(1, 2)

print('[2/4] Page chargée')

# URLs
page_source = driver.page_source
urls = list(set(re.findall(r'https://www\.leboncoin\.fr/ad/voitures/\d+', page_source)))[:20]

if len(urls) == 0:
    try:
        links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/ad/voitures/"]')
        for link in links:
            href = link.get_attribute('href')
            if href and '/ad/voitures/' in href and href not in urls:
                urls.append(href)
    except:
        pass

urls = urls[:20]
print(f'[3/4] {len(urls)} annonces trouvées')

# Scraper
vehicles = []
for i, url in enumerate(urls):
    print(f'  {i+1}/{len(urls)}', end=' ')
    try:
        driver.get(url)
        random_delay(3, 6)  # Délai aléatoire entre les pages
        
        # Scroll aléatoire sur la page
        driver.execute_script(f'window.scrollTo(0, {random.randint(200, 500)});')
        random_delay(0.5, 1)
        
        text = driver.find_element(By.TAG_NAME, 'body').text
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        data = {'lien': url, 'leboncoin_id': url.split('/')[-1]}
        
        # Ville et code postal (format "Ville 12345")
        for line in lines[:30]:
            # Chercher pattern ville + 5 chiffres
            match = re.search(r'^(.+?)\s+(\d{5})\s*$', line)
            if match:
                ville = match.group(1).strip()
                cp = match.group(2)
                # Éviter les faux positifs
                if len(ville) > 2 and not any(c.isdigit() for c in ville):
                    data['ville'] = ville
                    data['code_postal'] = cp
                    break
        
        # Prix (avec espaces insécables et caractères spéciaux)
        for line in lines:
            # Nettoyer tous les types d'espaces
            clean = line.replace('\xa0', '').replace('\u202f', '').replace(' ', '')
            m = re.search(r'(\d+)€', clean)
            if m:
                try:
                    p = int(m.group(1))
                    if 500 < p < 10000000:
                        data['prix'] = p
                        break
                except:
                    pass
        
        # Marque et modèle
        for j, line in enumerate(lines):
            line_lower = line.lower()
            if line_lower == 'marque' and j+1 < len(lines):
                data['marque'] = lines[j+1].upper()
            elif line_lower in ['modèle', 'modele'] and j+1 < len(lines):
                data['modele'] = lines[j+1]
            elif 'année' in line_lower and j+1 < len(lines):
                m = re.search(r'(\d{4})', lines[j+1])
                if m:
                    data['annee'] = int(m.group(1))
            elif 'kilométrage' in line_lower and j+1 < len(lines):
                m = re.search(r'(\d[\d\s]*)', lines[j+1])
                if m:
                    data['km'] = int(m.group(1).replace(' ', ''))
            elif line_lower == 'énergie' and j+1 < len(lines):
                data['energie'] = lines[j+1]
            elif 'boîte' in line_lower and j+1 < len(lines):
                data['boite_vitesse'] = lines[j+1]
        
        vehicles.append(data)
        print(f"{data.get('marque', '?')} | {data.get('ville', '?')} | {data.get('prix', '?')}€")
    except Exception as e:
        print(f'Err: {e}')

print(f'\n[4/4] {len(vehicles)} véhicules scrapés')

# Sauvegarder
conn = sqlite3.connect('data/leboncoin.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS vehicles (
    id INTEGER PRIMARY KEY,
    leboncoin_id TEXT UNIQUE,
    titre TEXT, prix REAL, lien TEXT,
    marque TEXT, modele TEXT, annee INTEGER, km INTEGER,
    energie TEXT, boite_vitesse TEXT, couleur TEXT,
    ville TEXT, code_postal TEXT, departement TEXT,
    type_vendeur TEXT, description TEXT, nb_photos INTEGER
)''')

for v in vehicles:
    c.execute('''INSERT OR REPLACE INTO vehicles 
        (leboncoin_id, prix, lien, marque, modele, annee, km, energie, boite_vitesse, ville, code_postal)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
        (v.get('leboncoin_id'), v.get('prix'), v.get('lien'),
         v.get('marque'), v.get('modele'), v.get('annee'), v.get('km'),
         v.get('energie'), v.get('boite_vitesse'),
         v.get('ville'), v.get('code_postal')))

conn.commit()
print(f'[OK] {len(vehicles)} véhicules en base')
conn.close()

# Fermeture propre
try:
    driver.quit()
except:
    pass
