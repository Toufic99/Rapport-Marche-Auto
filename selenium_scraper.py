"""
LEBONCOIN SCRAPER avec SELENIUM
================================
Récupère TOUTES les données y compris ville et code postal
"""

import time
import json
import re
import sqlite3
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class SeleniumScraper:
    """Scraper LeBonCoin avec Selenium pour récupérer ville/code postal"""
    
    def __init__(self, db_path='data/leboncoin.db', headless=True):
        self.db_path = db_path
        self.headless = headless
        self.driver = None
        self.init_database()
    
    def init_database(self):
        """Initialise la base de données"""
        os.makedirs('data', exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                leboncoin_id TEXT UNIQUE,
                titre TEXT,
                prix REAL,
                lien TEXT,
                marque TEXT,
                modele TEXT,
                annee INTEGER,
                km INTEGER,
                energie TEXT,
                boite_vitesse TEXT,
                couleur TEXT,
                ville TEXT,
                code_postal TEXT,
                departement TEXT,
                type_vendeur TEXT,
                description TEXT,
                nb_photos INTEGER,
                date_scrape TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
        print("[DB] Base initialisée")
    
    def start_browser(self):
        """Démarre le navigateur Chrome"""
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.implicitly_wait(10)
        print("[BROWSER] Chrome démarré")
    
    def stop_browser(self):
        """Ferme le navigateur"""
        if self.driver:
            self.driver.quit()
            print("[BROWSER] Chrome fermé")
    
    def close(self):
        """Alias pour stop_browser"""
        self.stop_browser()
    
    def get_listing_urls(self, max_pages=1):
        """Récupère les URLs des annonces depuis la page de liste"""
        urls = []
        
        for page in range(1, max_pages + 1):
            # URL sans numéro de page pour la page 1
            if page == 1:
                url = "https://www.leboncoin.fr/c/voitures"
            else:
                url = f"https://www.leboncoin.fr/c/voitures/p-{page}"
            
            print(f"[SCRAPE] Page {page}...")
            
            self.driver.get(url)
            time.sleep(6)
            
            # Scroll pour charger le contenu
            self.driver.execute_script("window.scrollTo(0, 500);")
            time.sleep(2)
            self.driver.execute_script("window.scrollTo(0, 1000);")
            time.sleep(2)
            
            # Accepter les cookies si présent
            try:
                cookie_btn = self.driver.find_element(By.ID, "didomi-notice-agree-button")
                cookie_btn.click()
                print("  Cookies acceptés")
                time.sleep(3)
            except:
                pass
            
            # Trouver les liens des annonces dans le HTML
            try:
                # Méthode principale: chercher dans le HTML source (plus fiable)
                page_source = self.driver.page_source
                found = re.findall(r'https://www\.leboncoin\.fr/ad/voitures/\d+', page_source)
                for u in found:
                    if u not in urls:
                        urls.append(u)
                
                print(f"  → {len(urls)} annonces trouvées")
            except Exception as e:
                print(f"  ⚠ Erreur: {e}")
            
            time.sleep(2)
        
        print(f"[TOTAL] {len(urls)} URLs")
        return urls
    
    def scrape_detail(self, url):
        """Scrape une annonce détaillée"""
        try:
            self.driver.get(url)
            time.sleep(4)
            
            # Accepter cookies si besoin
            try:
                cookie_btn = self.driver.find_element(By.ID, "didomi-notice-agree-button")
                cookie_btn.click()
                time.sleep(2)
            except:
                pass
            
            data = {
                'lien': url,
                'leboncoin_id': url.split('/')[-1],
                'date_scrape': datetime.now().isoformat()
            }
            
            # Récupérer tout le texte de la page
            body = self.driver.find_element(By.TAG_NAME, 'body')
            page_text = body.text
            lines = [l.strip() for l in page_text.split('\n') if l.strip()]
            
            # 🎯 VILLE ET CODE POSTAL - Chercher le pattern "Ville 12345"
            for line in lines[:30]:
                match = re.match(r'^([A-Za-zÀ-ÿ\s\-\']+)\s+(\d{5})\s*', line)
                if match:
                    data['ville'] = match.group(1).strip()
                    data['code_postal'] = match.group(2)
                    data['departement'] = match.group(2)[:2]
                    break
            
            # Titre - chercher après la localisation
            for i, line in enumerate(lines):
                if data.get('code_postal') and i > 0:
                    # Le titre est souvent la ligne après la localisation
                    if len(line) > 10 and not line.startswith('Annonces'):
                        data['titre'] = line
                        break
            
            # Prix - chercher "XX XXX €" avec différents formats
            for line in lines:
                # Nettoyer la ligne des caractères spéciaux
                clean_line = line.replace('\xa0', ' ').replace('\u202f', ' ')
                price_match = re.search(r'(\d[\d\s]*)\s*€', clean_line)
                if price_match:
                    price_str = re.sub(r'\s+', '', price_match.group(1))
                    try:
                        price = int(price_str)
                        if 500 < price < 10000000:  # Prix raisonnable
                            data['prix'] = float(price)
                            break
                    except:
                        pass
            
            # Si prix non trouvé, essayer avec aria-label ou data-*
            if 'prix' not in data:
                try:
                    price_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '€')]")
                    for elem in price_elements[:10]:
                        text = elem.text.replace('\xa0', ' ').replace('\u202f', ' ')
                        match = re.search(r'(\d[\d\s]*)\s*€', text)
                        if match:
                            price_str = re.sub(r'\s+', '', match.group(1))
                            price = int(price_str)
                            if 500 < price < 10000000:
                                data['prix'] = float(price)
                                break
                except:
                    pass
            
            # Caractéristiques - chercher les mots clés
            for i, line in enumerate(lines):
                line_lower = line.lower()
                next_line = lines[i+1] if i+1 < len(lines) else ''
                
                if line_lower == 'marque':
                    data['marque'] = next_line.upper()
                elif line_lower == 'modèle' or line_lower == 'modele':
                    data['modele'] = next_line
                elif 'année' in line_lower or 'annee' in line_lower:
                    match = re.search(r'(\d{4})', next_line)
                    if match:
                        data['annee'] = int(match.group(1))
                elif 'kilométrage' in line_lower:
                    match = re.search(r'(\d[\d\s]*)', next_line)
                    if match:
                        data['km'] = int(match.group(1).replace(' ', ''))
                elif line_lower == 'énergie' or line_lower == 'energie':
                    data['energie'] = next_line
                elif 'boîte' in line_lower or 'boite' in line_lower:
                    data['boite_vitesse'] = next_line
                elif line_lower == 'couleur':
                    data['couleur'] = next_line
            
            # Nombre de photos
            for line in lines:
                match = re.search(r'Voir les (\d+) photos', line)
                if match:
                    data['nb_photos'] = int(match.group(1))
                    break
            
            return data
            
        except Exception as e:
            print(f"  ⚠ Erreur scrape: {e}")
            return None
    
    def save_to_db(self, data):
        """Sauvegarde dans la base de données"""
        if not data:
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO vehicles 
                (leboncoin_id, titre, prix, lien, marque, modele, annee, km,
                 energie, boite_vitesse, couleur, ville, code_postal, departement,
                 type_vendeur, description, nb_photos)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('leboncoin_id'),
                data.get('titre'),
                data.get('prix'),
                data.get('lien'),
                data.get('marque'),
                data.get('modele'),
                data.get('annee'),
                data.get('km'),
                data.get('energie'),
                data.get('boite_vitesse'),
                data.get('couleur'),
                data.get('ville'),
                data.get('code_postal'),
                data.get('departement'),
                data.get('type_vendeur'),
                data.get('description'),
                data.get('nb_photos')
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"  ⚠ Erreur DB: {e}")
            return False
        finally:
            conn.close()
    
    def scrape(self, max_pages=1, max_annonces=10):
        """Lance le scraping complet"""
        print("=" * 50)
        print("🚗 LEBONCOIN SCRAPER (Selenium)")
        print("=" * 50)
        
        self.start_browser()
        
        try:
            # Récupérer les URLs
            urls = self.get_listing_urls(max_pages)
            
            # Limiter le nombre d'annonces
            urls = urls[:max_annonces]
            print(f"\n[SCRAPE] {len(urls)} annonces à scraper...")
            
            # Scraper chaque annonce
            success = 0
            for i, url in enumerate(urls, 1):
                print(f"\n[{i}/{len(urls)}] {url[:60]}...")
                
                data = self.scrape_detail(url)
                
                if data and data.get('titre'):
                    if self.save_to_db(data):
                        ville = data.get('ville', '-')
                        cp = data.get('code_postal', '-')
                        print(f"  ✅ {data.get('marque', '?')} | {data.get('prix', 0):.0f}€ | {ville} ({cp})")
                        success += 1
                    else:
                        print("  ❌ Erreur sauvegarde")
                else:
                    print("  ❌ Données invalides")
                
                time.sleep(2)  # Pause entre les annonces
            
            print("\n" + "=" * 50)
            print(f"✅ TERMINÉ: {success}/{len(urls)} véhicules scrapés")
            print("=" * 50)
            
        finally:
            self.stop_browser()
        
        return success


def main():
    """Point d'entrée principal"""
    scraper = SeleniumScraper(headless=True)
    scraper.scrape(max_pages=1, max_annonces=10)


if __name__ == "__main__":
    main()
