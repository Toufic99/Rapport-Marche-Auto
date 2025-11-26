#!/usr/bin/env python3
"""
LeBonCoin PRODUCTION Scraper - Extraction complète avec NEXT.JS JSON
Utilise les données inlinées dans le HTML Next.js pour éviter les API blockées
"""

import requests
import json
import re
import sqlite3
import os
import hashlib
import subprocess
import time
import random
from datetime import datetime
from itertools import cycle

class AntiDetectionManager:
    """Gère les stratégies anti-détection avec comportement humain"""
    
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0',
        ]
        self.ua_pool = cycle(self.user_agents)
        self.session = self._create_session()
        self.request_count = 0
        self.last_error_time = None
    
    def _create_session(self):
        """Crée une session avec headers réalistes"""
        session = requests.Session()
        session.headers.update(self.get_realistic_headers())
        return session
    
    def get_realistic_headers(self):
        """Retourne des headers réalistes"""
        return {
            'User-Agent': next(self.ua_pool),
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.leboncoin.fr/',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
    
    def human_like_delay(self):
        """Simule un délai humain réaliste entre pages"""
        # Humains lisent pendant 10-25 secondes par page (plus de pages = plus de temps)
        delay = random.uniform(10, 25)
        print(f"  [HUMAN BEHAVIOR] Pause de {delay:.1f}s (lecture)...")
        time.sleep(delay)
    
    def random_delay(self, min_sec=3, max_sec=7):
        """Pause aléatoire court entre requêtes"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
    
    def item_reading_delay(self):
        """Simule la lecture d'un annonce (1-3 secondes)"""
        time.sleep(random.uniform(1, 3))
    
    def break_after_pages(self, page_num):
        """Simule une pause plus longue après chaque X pages"""
        if page_num % 2 == 0:  # Toutes les 2 pages
            # Pause plus longue (comme une vraie pause café)
            long_break = random.uniform(120, 180)  # 2-3 minutes
            print(f"  [BREAK] Pause naturelle de {long_break:.0f}s (comportement humain)...")
            time.sleep(long_break)
    
    def simulate_page_scroll(self):
        """Simule un scroll de page (2-4s)"""
        scroll_time = random.uniform(2, 4)
        time.sleep(scroll_time)
    
    def rotate_user_agent(self):
        """Change le User-Agent pour la prochaine requête"""
        self.session.headers['User-Agent'] = next(self.ua_pool)
    
    def random_mouse_movements(self):
        """Pause variable pour imiter des mouvements souris"""
        time.sleep(random.uniform(0.5, 1.5))
    
    def handle_rate_limit(self):
        """Gère les erreurs 403 - pause longue"""
        print("\n⚠️  [RATE LIMITED] Détecté! Pause longue de 5-10 minutes...")
        long_wait = random.uniform(300, 600)  # 5-10 min
        for i in range(int(long_wait)):
            if i % 60 == 0:
                print(f"  ⏳ Attente: {int(long_wait - i)}s restants...")
            time.sleep(1)
        self.session = self._create_session()  # Recrée la session
        print("✅ Session réinitialisée, on recommence...\n")
    
    def get_session(self):
        """Retourne la session persistante"""
        return self.session

class DatabaseManager:
    """Gère la base de données SQLite"""
    
    def __init__(self, db_name='leboncoin_vehicles.db'):
        self.db_name = db_name
        self.init_db()
    
    def init_db(self):
        """Crée les tables si elles n'existent pas"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY,
                unique_hash TEXT UNIQUE,
                titre TEXT,
                prix_initial REAL,
                prix_current REAL,
                lien TEXT,
                date_annonce TEXT,
                date_first_seen TEXT,
                date_last_seen TEXT,
                statut TEXT DEFAULT 'ACTIVE',
                date_vendu TEXT,
                jours_en_vente INTEGER,
                photo_principale TEXT,
                photos_list TEXT,
                description TEXT,
                marque TEXT,
                modele TEXT,
                annee INTEGER,
                km INTEGER,
                ville TEXT,
                priorite INTEGER DEFAULT 0,
                energie TEXT DEFAULT 'N/A',
                boite_vitesse TEXT DEFAULT 'N/A',
                prix_baisse REAL DEFAULT 0,
                est_pro INTEGER DEFAULT 0,
                seller_name TEXT,
                nb_annonces_vendeur INTEGER DEFAULT 1
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY,
                vehicle_id INTEGER,
                prix REAL,
                date_check TEXT,
                statut TEXT,
                FOREIGN KEY(vehicle_id) REFERENCES vehicles(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS photos (
                id INTEGER PRIMARY KEY,
                vehicle_id INTEGER,
                photo_url TEXT,
                local_path TEXT,
                FOREIGN KEY(vehicle_id) REFERENCES vehicles(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS seller_stats (
                id INTEGER PRIMARY KEY,
                seller_name TEXT UNIQUE,
                nb_annonces INTEGER DEFAULT 1,
                est_pro INTEGER DEFAULT 0,
                avg_price REAL,
                last_updated TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS energy_stats (
                id INTEGER PRIMARY KEY,
                energie TEXT UNIQUE,
                total_count INTEGER DEFAULT 0,
                avg_price REAL DEFAULT 0,
                avg_days_to_sell REAL DEFAULT 0,
                avg_km INTEGER DEFAULT 0,
                last_updated TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def insert_vehicle(self, vehicle_info):
        """Insère un nouveau véhicule"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO vehicles (
                    unique_hash, titre, prix_initial, prix_current, lien,
                    date_annonce, date_first_seen, date_last_seen, ville, 
                    marque, modele, description, annee, km, photo_principale,
                    energie, boite_vitesse
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                vehicle_info['unique_hash'],
                vehicle_info['titre'][:200],
                vehicle_info['prix'],
                vehicle_info['prix'],
                vehicle_info['lien'],
                datetime.now().strftime('%Y-%m-%d'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                vehicle_info.get('ville', 'N/A'),
                vehicle_info.get('marque', 'N/A'),
                vehicle_info.get('modele', 'N/A'),
                vehicle_info.get('description', '')[:500],
                vehicle_info.get('annee', None),
                vehicle_info.get('km', None),
                vehicle_info.get('photo', ''),
                vehicle_info.get('energie', 'N/A'),
                vehicle_info.get('boite_vitesse', 'N/A')
            ))
            
            vehicle_id = cursor.lastrowid
            
            # Marquer Poitiers comme prioritaire
            if 'poitiers' in vehicle_info.get('ville', '').lower():
                cursor.execute('UPDATE vehicles SET priorite = 1 WHERE id = ?', (vehicle_id,))
            
            conn.commit()
            conn.close()
            return vehicle_id
        except Exception as e:
            conn.close()
            return None
    
    def get_vehicle_by_hash(self, unique_hash):
        """Récupère un véhicule par son hash"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM vehicles WHERE unique_hash = ?', (unique_hash,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def add_price_history(self, vehicle_id, prix, statut):
        """Ajoute un historique de prix"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO price_history (vehicle_id, prix, date_check, statut) VALUES (?, ?, ?, ?)',
            (vehicle_id, prix, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), statut)
        )
        conn.commit()
        conn.close()
    
    def add_photo(self, vehicle_id, photo_url, local_path):
        """Ajoute une photo a un vehicule"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO photos (vehicle_id, photo_url, local_path) VALUES (?, ?, ?)',
                (vehicle_id, photo_url, local_path)
            )
            conn.commit()
        except:
            pass
        finally:
            conn.close()


class PhotoDownloader:
    """Gere le telechargement et la sauvegarde des photos"""
    
    def __init__(self, base_dir='voitures_photos'):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
    
    def download_photo(self, photo_url, vehicle_id, index=0):
        """Telecharge une photo et la sauvegarde localement"""
        if not photo_url or not photo_url.strip():
            return None
        
        try:
            # Creer un dossier pour le vehicule
            vehicle_dir = os.path.join(self.base_dir, f'vehicle_{vehicle_id}')
            os.makedirs(vehicle_dir, exist_ok=True)
            
            # Telecharger la photo
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Referer': 'https://www.leboncoin.fr/'}
            response = requests.get(photo_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Determiner l'extension
            ext = '.jpg'
            if 'content-type' in response.headers:
                ct = response.headers['content-type'].lower()
                if 'png' in ct:
                    ext = '.png'
                elif 'webp' in ct:
                    ext = '.webp'
                elif 'jpeg' not in ct and 'jpg' not in ct:
                    # Pas une image standard, garder .jpg
                    pass
            
            # Sauvegarder
            filename = f'photo_{index}{ext}'
            filepath = os.path.join(vehicle_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            return filepath
        except Exception as e:
            return None
    
    def download_all_photos(self, listing_data, vehicle_id):
        """Telecharge toutes les photos d'une annonce"""
        photos = []
        
        try:
            images = listing_data.get('images', {})
            
            # Les URLs peuvent être dans différents formats
            urls = images.get('urls', [])  # Format standard
            if not urls:
                urls = images.get('images', [])  # Autre format possible
            if not urls:
                # Chercher thumb_url ou image_url
                if 'thumb_url' in images:
                    urls = [images['thumb_url']]
                elif 'image_url' in images:
                    urls = [images['image_url']]
            
            for idx, url in enumerate(urls[:5]):  # Max 5 photos
                if isinstance(url, dict) and 'url' in url:
                    url = url['url']
                local_path = self.download_photo(url, vehicle_id, idx)
                if local_path:
                    photos.append(local_path)
        except Exception as e:
            pass
        
        return photos


def extract_next_data(html_content):
    """Extrait le JSON depuis __NEXT_DATA__"""
    try:
        # Trouver le script __NEXT_DATA__
        start = html_content.find('<script id="__NEXT_DATA__"')
        if start == -1:
            return None
        
        # Trouver le début du JSON
        json_start = html_content.find('{', start)
        json_end = html_content.find('</script>', json_start)
        
        json_str = html_content[json_start:json_end]
        
        # Parser le JSON
        data = json.loads(json_str)
        
        # Naviguer jusqu'aux annonces (ads)
        # Structure: props.pageProps.searchData.ads
        props = data.get('props', {})
        page_props = props.get('pageProps', {})
        search_data = page_props.get('searchData', {})
        ads = search_data.get('ads', [])
        
        return ads
    except Exception as e:
        return None


def parse_listing(listing):
    """Parse une annonce JSON"""
    
    # Mapping des valeurs d'attributs
    fuel_map = {
        '1': 'Essence', '2': 'Diesel', '3': 'Électrique', '4': 'Hybride',
        '5': 'GPL', '6': 'Éthanol', '7': 'Hydrogène', '8': 'Essence/GPL'
    }
    gearbox_map = {
        '1': 'Manuelle', '2': 'Automatique', '3': 'Robotisée', '4': 'Variateur',
        '5': 'Boîte très courte', '6': 'Semi-automatique'
    }
    
    try:
        list_id = listing.get('list_id')
        subject = listing.get('subject', '')
        body = listing.get('body', '')
        price_list = listing.get('price', [])
        
        if not price_list or len(price_list) == 0:
            return None
        
        prix = float(price_list[0])
        
        # Extraire marque du subject
        parts = subject.split()
        marque = parts[0] if parts else 'N/A'
        modele = parts[1] if len(parts) > 1 else 'N/A'
        
        # Chercher la ville
        ville = 'N/A'
        km = None
        annee = None
        energie = 'N/A'
        boite_vitesse = 'N/A'
        
        # Extraire du location JSON
        location_data = listing.get('location', {})
        if location_data:
            ville = location_data.get('city', 'N/A')
        
        # Chercher l'année, KM, energie et boite vitesse dans les attributes
        attributes = listing.get('attributes', [])
        for attr in attributes:
            key = attr.get('key', '')
            value = str(attr.get('value', 'N/A'))
            
            if key == 'regdate':
                try:
                    annee = int(value)
                except:
                    pass
            elif key == 'mileage':
                try:
                    km = int(value)
                except:
                    pass
            elif key == 'fuel':  # Énergie
                energie = fuel_map.get(value, value)
            elif key == 'gearbox':  # Boîte de vitesse
                boite_vitesse = gearbox_map.get(value, value)
        
        # Créer l'URL
        lien = listing.get('url', f"https://www.leboncoin.fr/ad/voitures/{list_id}")
        
        # Photo
        images = listing.get('images', {})
        photo = images.get('thumb_url', '')
        
        # Extraire le nom du vendeur
        seller_name = listing.get('account', {}).get('name', 'Particulier')
        if not seller_name or seller_name == '':
            seller_name = 'Particulier'
        
        # Hash unique
        unique_hash = str(abs(hash(lien)) % (10 ** 8))
        
        return {
            'unique_hash': unique_hash,
            'titre': subject[:150],
            'prix': prix,
            'lien': lien,
            'ville': ville,
            'marque': marque,
            'modele': modele,
            'description': body[:500],
            'annee': annee,
            'km': km,
            'photo': photo,
            'energie': energie,
            'boite_vitesse': boite_vitesse,
            'seller_name': seller_name
        }
    except Exception as e:
        return None


def scrape_page(url, anti_detect):
    """Scrape une page LeBonCoin avec protections anti-détection"""
    
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Rotate User-Agent à chaque requête
            anti_detect.rotate_user_agent()
            
            # Simule mouvements souris avant requête
            anti_detect.random_mouse_movements()
            
            # Utilise la session persistante avec headers réalistes
            response = anti_detect.get_session().get(url, timeout=15)
            
            if response.status_code == 403:
                retry_count += 1
                anti_detect.handle_rate_limit()
                continue
            
            response.raise_for_status()
            
            # Forcer l'encodage UTF-8
            response.encoding = 'utf-8'
            
            # Simule le scroll de page
            anti_detect.simulate_page_scroll()
            
            # Pause aléatoire entre requêtes (2-5 secondes)
            anti_detect.random_delay(2, 5)
            
            try:
                ads = extract_next_data(response.text)
                return ads
            except Exception as extract_error:
                return None
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                return None
            anti_detect.handle_rate_limit()
    
    return None


def detect_sales_and_update_dates(all_listings_raw):
    """Détecte les véhicules vendus (disparition de la liste) et met à jour date_vendu"""
    conn = sqlite3.connect('leboncoin_vehicles.db')
    cursor = conn.cursor()
    
    try:
        # Créer les hashes des listings actuels
        current_hashes = set()
        for listing in all_listings_raw:
            try:
                # Extraire le titre pour créer le hash
                titre = listing.get('attributes', {}).get('subject', '')
                prix = listing.get('attributes', {}).get('price', [''])[0]
                lien = listing.get('attributes', {}).get('url', '')
                
                if titre:
                    unique_hash = hashlib.md5(f"{titre}_{prix}_{lien}".encode()).hexdigest()
                    current_hashes.add(unique_hash)
            except:
                continue
        
        # Récupérer tous les véhicules actifs
        cursor.execute("SELECT id, unique_hash FROM vehicles WHERE statut = 'ACTIVE' OR statut IS NULL")
        active_vehicles = {row[1]: row[0] for row in cursor.fetchall()}
        
        # Identifier les véhicules vendus (dans DB mais pas dans le scraping)
        sold_hashes = set(active_vehicles.keys()) - current_hashes
        
        today = datetime.now().strftime('%Y-%m-%d')
        sales_detected = 0
        
        for hash_val in sold_hashes:
            vehicle_id = active_vehicles[hash_val]
            
            # Récupérer la date d'annonce
            cursor.execute("SELECT date_annonce FROM vehicles WHERE id = ?", (vehicle_id,))
            result = cursor.fetchone()
            
            if result and result[0]:
                date_annonce = datetime.strptime(result[0][:10], '%Y-%m-%d')
                date_vendu = datetime.strptime(today, '%Y-%m-%d')
                jours_en_vente = (date_vendu - date_annonce).days
                
                # Mettre à jour le statut et les dates
                cursor.execute("""
                    UPDATE vehicles 
                    SET statut = 'VENDUE', date_vendu = ?, jours_en_vente = ?
                    WHERE id = ?
                """, (today, jours_en_vente, vehicle_id))
                
                sales_detected += 1
        
        conn.commit()
        
        if sales_detected > 0:
            print(f"[SALES] {sales_detected} véhicule(s) vendu(s) détecté(s)")
        
        return sales_detected
        
    except Exception as e:
        print(f"[ERROR] Sales detection: {e}")
        return 0
    finally:
        conn.close()


def update_energy_statistics():
    """Calcule et met à jour les statistiques par type d'énergie"""
    conn = sqlite3.connect('leboncoin_vehicles.db')
    cursor = conn.cursor()
    
    try:
        energy_types = ['Essence', 'Diesel', 'Électrique', 'Hybride', 'GPL', 'Éthanol', 'Hydrogène', 'Essence/GPL']
        
        for energie in energy_types:
            # Récupérer les statistiques pour ce type d'énergie
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    AVG(CAST(prix_current AS FLOAT)) as avg_price,
                    AVG(km) as avg_km,
                    AVG(CASE WHEN jours_en_vente > 0 THEN jours_en_vente ELSE NULL END) as avg_days
                FROM vehicles 
                WHERE energie = ?
            """, (energie,))
            
            result = cursor.fetchone()
            
            if result and result[0] > 0:
                total_count, avg_price, avg_km, avg_days = result
                today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Mettre à jour ou insérer les statistiques
                cursor.execute("""
                    INSERT INTO energy_stats (energie, total_count, avg_price, avg_km, avg_days_to_sell, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(energie) DO UPDATE SET
                        total_count = ?,
                        avg_price = ?,
                        avg_km = ?,
                        avg_days_to_sell = ?,
                        last_updated = ?
                """, (energie, total_count, avg_price, avg_km, avg_days, today,
                      total_count, avg_price, avg_km, avg_days, today))
        
        conn.commit()
        print("[STATS] Statistiques d'énergie mises à jour")
        
    except Exception as e:
        print(f"[ERROR] Energy statistics: {e}")
    finally:
        conn.close()


def get_energy_report():
    """Génère un rapport détaillé par type d'énergie"""
    conn = sqlite3.connect('leboncoin_vehicles.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                energie,
                total_count,
                ROUND(avg_price, 2) as avg_price,
                ROUND(avg_km, 0) as avg_km,
                ROUND(avg_days_to_sell, 1) as avg_days
            FROM energy_stats
            ORDER BY total_count DESC
        """)
        
        report = cursor.fetchall()
        return report
        
    except Exception as e:
        print(f"[ERROR] Energy report: {e}")
        return []
    finally:
        conn.close()


def detect_pros_and_count_sellers():
    """Détecte les vendeurs pro et compte leurs annonces"""
    conn = sqlite3.connect('leboncoin_vehicles.db')
    cursor = conn.cursor()
    
    try:
        # Récupérer tous les vendeurs
        cursor.execute("SELECT DISTINCT seller_name FROM vehicles WHERE seller_name IS NOT NULL")
        sellers = cursor.fetchall()
        
        pro_keywords = ['garage', 'auto', 'concession', 'professionnel', 'sarl', 'sas', 'eurl', 'concessionnaire', 'distributeur', 'agent']
        
        for (seller_name,) in sellers:
            if seller_name:
                # Compter les annonces
                cursor.execute("SELECT COUNT(*) FROM vehicles WHERE seller_name = ?", (seller_name,))
                count = cursor.fetchone()[0]
                
                # Détecter si pro
                est_pro = 0
                seller_lower = seller_name.lower()
                
                if any(keyword in seller_lower for keyword in pro_keywords) or count > 5:
                    est_pro = 1
                
                # Calculer prix moyen
                cursor.execute("SELECT AVG(CAST(prix_current AS FLOAT)) FROM vehicles WHERE seller_name = ?", (seller_name,))
                avg_price = cursor.fetchone()[0]
                
                today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Mettre à jour seller_stats
                cursor.execute("""
                    INSERT INTO seller_stats (seller_name, nb_annonces, est_pro, avg_price, last_updated)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(seller_name) DO UPDATE SET
                        nb_annonces = ?,
                        est_pro = ?,
                        avg_price = ?,
                        last_updated = ?
                """, (seller_name, count, est_pro, avg_price, today,
                      count, est_pro, avg_price, today))
                
                # Mettre à jour les colonnes dans vehicles
                cursor.execute("UPDATE vehicles SET est_pro = ?, nb_annonces_vendeur = ? WHERE seller_name = ?",
                              (est_pro, count, seller_name))
        
        conn.commit()
        
        cursor.execute("SELECT COUNT(*) FROM seller_stats WHERE est_pro = 1")
        pro_count = cursor.fetchone()[0]
        
        print(f"[SELLERS] {len(sellers)} vendeurs analysés, {pro_count} vendeurs pro détectés")
        
    except Exception as e:
        print(f"[ERROR] Seller detection: {e}")
    finally:
        conn.close()


def main():
    print("\n" + "="*70)
    print("[LEBONCOIN PRODUCTION SCRAPER - NEXT.JS JSON]")
    print("[TIME] " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("[MODE] Anti-Detection Avancé + 7 pages")
    print("="*70 + "\n")
    
    start_time = datetime.now()
    
    # Initialise le gestionnaire anti-détection
    anti_detect = AntiDetectionManager()
    
    db = DatabaseManager()
    photo_dl = PhotoDownloader()
    nouvelles_voitures = 0
    voitures_maj = 0
    total_found = 0
    
    # Scraper 7 pages (245 voitures)
    for page_num in range(1, 8):
        print(f"[PAGE {page_num}/7] Scraping...")
        
        url = f"https://www.leboncoin.fr/c/voitures?p={page_num}"
        
        ads = scrape_page(url, anti_detect)
        
        if not ads:
            print(f"  [ERROR] Pas de listings trouvés")
            continue
        
        print(f"  Trouvé {len(ads)} annonces")
        total_found += len(ads)
        
        for listing in ads[:120]:  # Max 120 par page
            vehicle_info = parse_listing(listing)
            
            if not vehicle_info:
                continue
            
            # Simule la lecture d'une annonce (1-3s)
            anti_detect.item_reading_delay()
            
            # Vérifier si existe
            existing = db.get_vehicle_by_hash(vehicle_info['unique_hash'])
            
            if existing:
                voitures_maj += 1
            else:
                vehicle_id = db.insert_vehicle(vehicle_info)
                if vehicle_id:
                    nouvelles_voitures += 1
                    db.add_price_history(vehicle_id, vehicle_info['prix'], 'ACTIVE')
                    
                    # Telecharger les photos
                    photos = photo_dl.download_all_photos(listing, vehicle_id)
                    for photo_path in photos:
                        db.add_photo(vehicle_id, listing.get('images', {}).get('urls', [None])[0], photo_path)
                    
                    if 'poitiers' in vehicle_info.get('ville', '').lower():
                        print(f"  [POITIERS] {vehicle_info['titre'][:50]} ({len(photos)} photos)")
        
        # Simule une pause entre pages (comportement humain)
        anti_detect.human_like_delay()
        
        # Pause plus longue toutes les 3 pages
        anti_detect.break_after_pages(page_num)
    
    elapsed_time = datetime.now() - start_time
    
    print(f"\n[SUMMARY]")
    print(f"  Total annonces trouvées: {total_found}")
    print(f"  Nouvelles voitures: {nouvelles_voitures}")
    print(f"  Voitures mises à jour: {voitures_maj}")
    print(f"  Temps écoulé: {elapsed_time.total_seconds():.0f}s ({elapsed_time.total_seconds()/60:.1f}min)")
    
    # Détecter les ventes et mettre à jour les statistiques
    print("\n[ANALYTICS]")
    all_listings = []
    for page_num in range(1, 8):
        url = f"https://www.leboncoin.fr/c/voitures?p={page_num}"
        ads = scrape_page(url, anti_detect)
        if ads:
            all_listings.extend(ads)
    
    sales = detect_sales_and_update_dates(all_listings)
    update_energy_statistics()
    detect_pros_and_count_sellers()
    
    # Afficher le rapport énergie
    energy_report = get_energy_report()
    if energy_report:
        print("\n[RAPPORT ÉNERGIE]")
        print(f"{'Type Énergie':<15} {'Nombre':<10} {'Px Moyen':<12} {'Km Moyen':<12} {'Jours Vente':<12}")
        print("-" * 60)
        for row in energy_report:
            energie, count, avg_price, avg_km, avg_days = row
            print(f"{str(energie):<15} {count:<10} {avg_price or 0:<12.0f}€ {avg_km or 0:<12.0f} {avg_days or 0:<12.1f}j")
    
    # Générer les rapports
    if total_found > 0:
        print("\n[REPORT] Génération des rapports...")
        try:
            subprocess.run(['python', 'report_generator.py'], check=True, capture_output=True)
            print("[REPORT] CSV: leboncoin_rapport_complet.csv")
            print("[REPORT] HTML: leboncoin_rapport.html")
            print("\n[SUCCESS] Scraping et rapports réussis!")
            return True
        except Exception as e:
            print(f"[ERROR] Report generation: {e}")
            return False
    else:
        print("\n[FAILED] Aucun véhicule trouvé!")
        return False


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
