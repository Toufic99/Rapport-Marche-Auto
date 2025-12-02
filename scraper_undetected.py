"""
LeBonCoin Scraper avec Undetected Chrome
=========================================
Contourne la protection anti-bot de LeBonCoin
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sqlite3
import time
import re
from datetime import datetime
from pathlib import Path


class LeBonCoinScraper:
    """Scraper LeBonCoin avec undetected-chromedriver"""
    
    def __init__(self, db_path='data/leboncoin.db', headless=False):
        self.db_path = db_path
        self.headless = headless
        self.driver = None
        self.init_database()
    
    def init_database(self):
        """Initialise la base SQLite"""
        Path(self.db_path).parent.mkdir(exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                leboncoin_id TEXT UNIQUE,
                titre TEXT,
                marque TEXT,
                modele TEXT,
                annee INTEGER,
                km INTEGER,
                prix REAL,
                energie TEXT,
                boite_vitesse TEXT,
                couleur TEXT,
                ville TEXT,
                code_postal TEXT,
                departement TEXT,
                type_vendeur TEXT,
                nb_photos INTEGER,
                description TEXT,
                lien TEXT,
                date_scrape TEXT
            )
        ''')
        conn.commit()
        conn.close()
        print("[DB] Base initialisée")
    
    def start_browser(self):
        """Démarre Chrome avec undetected-chromedriver"""
        options = uc.ChromeOptions()
        
        if self.headless:
            options.add_argument('--headless')
        
        options.add_argument('--lang=fr-FR')
        options.add_argument('--window-size=1920,1080')
        
        self.driver = uc.Chrome(options=options, use_subprocess=True)
        print("[BROWSER] Chrome démarré (undetected)")
        return self.driver
    
    def accept_cookies(self):
        """Accepte les cookies"""
        try:
            time.sleep(2)
            cookie_btn = self.driver.find_element(By.ID, "didomi-notice-agree-button")
            cookie_btn.click()
            print("[COOKIES] Acceptés")
            time.sleep(2)
        except:
            print("[COOKIES] Pas de popup")
    
    def get_listing_urls(self, max_pages=3):
        """Récupère les URLs des annonces"""
        urls = set()
        
        for page in range(1, max_pages + 1):
            url = f"https://www.leboncoin.fr/c/voitures?page={page}"
            print(f"[PAGE] Chargement page {page}...")
            
            self.driver.get(url)
            time.sleep(5)
            
            if page == 1:
                self.accept_cookies()
                time.sleep(3)
            
            # Scroll pour charger toutes les annonces
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                time.sleep(1)
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            # Récupérer les liens
            page_html = self.driver.page_source
            
            # Chercher les URLs d'annonces
            ad_urls = re.findall(r'https://www\.leboncoin\.fr/ad/voitures/\d+\.htm', page_html)
            
            for url in ad_urls:
                urls.add(url)
            
            print(f"  → {len(ad_urls)} annonces sur cette page (total: {len(urls)})")
        
        return list(urls)
    
    def scrape_detail(self, url):
        """Scrape une annonce détaillée"""
        try:
            self.driver.get(url)
            time.sleep(4)
            
            data = {
                'lien': url,
                'leboncoin_id': url.split('/')[-1].replace('.htm', ''),
                'date_scrape': datetime.now().isoformat()
            }
            
            # Récupérer le texte de la page
            body = self.driver.find_element(By.TAG_NAME, 'body')
            page_text = body.text
            lines = [l.strip() for l in page_text.split('\n') if l.strip()]
            
            # 🎯 VILLE ET CODE POSTAL
            for line in lines[:40]:
                # Pattern: "Ville 12345" ou "Ville 12345 Quartier"
                match = re.match(r'^([A-Za-zÀ-ÿ\s\-\']+)\s+(\d{5})(?:\s|$)', line)
                if match:
                    ville = match.group(1).strip()
                    # Eviter les faux positifs
                    if len(ville) > 2 and ville.lower() not in ['voir', 'page', 'annonce']:
                        data['ville'] = ville
                        data['code_postal'] = match.group(2)
                        data['departement'] = match.group(2)[:2]
                        break
            
            # Prix - "XX XXX €"
            for line in lines:
                price_match = re.search(r'(\d[\d\s\u00a0]*)\s*€', line)
                if price_match:
                    price_str = price_match.group(1).replace(' ', '').replace('\xa0', '').replace('\u00a0', '')
                    try:
                        price = int(price_str)
                        if 500 < price < 5000000:
                            data['prix'] = float(price)
                            break
                    except:
                        pass
            
            # Caractéristiques par label/valeur
            for i, line in enumerate(lines):
                line_lower = line.lower().strip()
                next_line = lines[i+1].strip() if i+1 < len(lines) else ''
                
                if line_lower == 'marque' and next_line:
                    data['marque'] = next_line.upper()
                elif line_lower in ['modèle', 'modele'] and next_line:
                    data['modele'] = next_line
                elif line_lower in ["année-modèle", 'année modèle', 'annee-modele', 'annee modele']:
                    match = re.search(r'(\d{4})', next_line)
                    if match:
                        data['annee'] = int(match.group(1))
                elif line_lower == 'kilométrage':
                    match = re.search(r'(\d[\d\s]*)', next_line)
                    if match:
                        km_str = match.group(1).replace(' ', '')
                        data['km'] = int(km_str)
                elif line_lower in ['énergie', 'energie'] and next_line:
                    data['energie'] = next_line
                elif line_lower in ['boîte de vitesse', 'boite de vitesse'] and next_line:
                    data['boite_vitesse'] = next_line
                elif line_lower in ['couleur extérieure', 'couleur exterieure', 'couleur'] and next_line:
                    data['couleur'] = next_line
            
            # Titre - Essayer le h1
            try:
                h1 = self.driver.find_element(By.TAG_NAME, 'h1')
                data['titre'] = h1.text.strip()
            except:
                pass
            
            # Nombre de photos
            for line in lines:
                match = re.search(r'(?:Voir les\s+)?(\d+)\s+photos?', line)
                if match:
                    data['nb_photos'] = int(match.group(1))
                    break
            
            return data
            
        except Exception as e:
            print(f"  ⚠ Erreur: {e}")
            return None
    
    def save_to_db(self, data):
        """Sauvegarde en base"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO vehicles 
            (leboncoin_id, titre, marque, modele, annee, km, prix, energie, 
             boite_vitesse, couleur, ville, code_postal, departement, 
             type_vendeur, nb_photos, description, lien, date_scrape)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('leboncoin_id'),
            data.get('titre'),
            data.get('marque'),
            data.get('modele'),
            data.get('annee'),
            data.get('km'),
            data.get('prix'),
            data.get('energie'),
            data.get('boite_vitesse'),
            data.get('couleur'),
            data.get('ville'),
            data.get('code_postal'),
            data.get('departement'),
            data.get('type_vendeur'),
            data.get('nb_photos'),
            data.get('description'),
            data.get('lien'),
            data.get('date_scrape')
        ))
        
        conn.commit()
        conn.close()
    
    def close(self):
        """Ferme le navigateur"""
        if self.driver:
            self.driver.quit()
            print("[BROWSER] Chrome fermé")
    
    def run(self, max_pages=2, max_ads=10):
        """Exécute le scraping"""
        print("="*50)
        print("🚗 LEBONCOIN SCRAPER (Undetected Chrome)")
        print("="*50)
        
        self.start_browser()
        
        # Récupérer URLs
        urls = self.get_listing_urls(max_pages)
        print(f"\n[TOTAL] {len(urls)} URLs trouvées")
        
        if max_ads:
            urls = urls[:max_ads]
        
        # Scraper chaque annonce
        print(f"\n[SCRAPE] {len(urls)} annonces à traiter...")
        success = 0
        
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] {url}")
            
            data = self.scrape_detail(url)
            
            if data:
                self.save_to_db(data)
                ville = data.get('ville', '?')
                cp = data.get('code_postal', '?')
                prix = data.get('prix', 0)
                marque = data.get('marque', '?')
                print(f"  ✓ {marque} - {ville} {cp} - {prix:,.0f}€".replace(',', ' '))
                success += 1
            else:
                print("  ✗ Échec")
            
            time.sleep(2)
        
        self.close()
        
        print("\n" + "="*50)
        print(f"✅ TERMINÉ: {success}/{len(urls)} véhicules scrapés")
        print("="*50)


if __name__ == '__main__':
    scraper = LeBonCoinScraper(headless=False)  # headless=False pour voir le navigateur
    scraper.run(max_pages=1, max_ads=5)
