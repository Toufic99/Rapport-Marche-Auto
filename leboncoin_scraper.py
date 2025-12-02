import requests
from bs4 import BeautifulSoup
import csv
import sqlite3
import os
from datetime import datetime, timedelta
import re
import json
import time
import random


# ============================================================================
# BASE DE DONNEES SQLITE
# ============================================================================

class DatabaseManager:
    """Gère la base de données des voitures"""
    
    def __init__(self, db_name='data/leboncoin.db'):
        self.db_name = db_name
        # Créer le dossier data si nécessaire
        os.makedirs(os.path.dirname(db_name), exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Crée les tables si elles n'existent pas"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Table des voitures avec TOUTES les colonnes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                annee TEXT,
                km TEXT,
                ville TEXT,
                code_postal TEXT,
                departement TEXT,
                region TEXT,
                type_vendeur TEXT,
                energie TEXT,
                boite_vitesse TEXT,
                couleur TEXT,
                nb_portes TEXT,
                nb_places TEXT,
                puissance_fiscale TEXT,
                puissance_din TEXT,
                emission_co2 TEXT,
                critair TEXT,
                premiere_main TEXT,
                non_fumeur TEXT,
                carnet_entretien TEXT,
                ct_ok TEXT,
                garantie TEXT,
                nb_photos TEXT,
                vendeur_id TEXT,
                vendeur_nom TEXT
            )
        ''')
        
        # Table de l'historique des prix
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER,
                prix REAL,
                date_check TEXT,
                statut TEXT,
                FOREIGN KEY(vehicle_id) REFERENCES vehicles(id)
            )
        ''')
        
        # Table des photos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER,
                url TEXT,
                path_local TEXT,
                date_downloaded TEXT,
                FOREIGN KEY(vehicle_id) REFERENCES vehicles(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_vehicle_by_hash(self, unique_hash):
        """Récupère une voiture par son hash unique"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM vehicles WHERE unique_hash = ?', (unique_hash,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def insert_vehicle(self, vehicle_data):
        """Insère une nouvelle voiture avec TOUTES les données"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO vehicles 
                (unique_hash, titre, prix_initial, prix_current, lien, 
                 date_annonce, date_first_seen, date_last_seen, statut,
                 photo_principale, photos_list, description, marque, modele, annee, km,
                 ville, code_postal, departement, region, type_vendeur,
                 energie, boite_vitesse, couleur, nb_portes, nb_places,
                 puissance_fiscale, puissance_din, emission_co2, critair,
                 premiere_main, non_fumeur, carnet_entretien, ct_ok, garantie, nb_photos,
                 vendeur_id, vendeur_nom)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                vehicle_data.get('unique_hash'),
                vehicle_data.get('titre'),
                vehicle_data.get('prix'),
                vehicle_data.get('prix'),
                vehicle_data.get('lien'),
                vehicle_data.get('date_annonce'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'ACTIVE',
                vehicle_data.get('photo_principale'),
                json.dumps(vehicle_data.get('photos', [])),
                vehicle_data.get('description'),
                vehicle_data.get('marque'),
                vehicle_data.get('modele'),
                vehicle_data.get('annee'),
                vehicle_data.get('km'),
                vehicle_data.get('ville'),
                vehicle_data.get('code_postal'),
                vehicle_data.get('departement'),
                vehicle_data.get('region'),
                vehicle_data.get('type_vendeur'),
                vehicle_data.get('energie'),
                vehicle_data.get('boite_vitesse'),
                vehicle_data.get('couleur'),
                vehicle_data.get('nb_portes'),
                vehicle_data.get('nb_places'),
                vehicle_data.get('puissance_fiscale'),
                vehicle_data.get('puissance_din'),
                vehicle_data.get('emission_co2'),
                vehicle_data.get('critair'),
                vehicle_data.get('premiere_main'),
                vehicle_data.get('non_fumeur'),
                vehicle_data.get('carnet_entretien'),
                vehicle_data.get('ct_ok'),
                vehicle_data.get('garantie'),
                vehicle_data.get('nb_photos'),
                vehicle_data.get('vendeur_id'),
                vehicle_data.get('vendeur_nom')
            ))
            
            vehicle_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return vehicle_id
        except sqlite3.IntegrityError:
            conn.close()
            return None
    
    def update_vehicle_status(self, vehicle_id, statut, date_vendu=None):
        """Met à jour le statut d'une voiture"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE vehicles 
            SET statut = ?, date_vendu = ?, date_last_seen = ?
            WHERE id = ?
        ''', (statut, date_vendu, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), vehicle_id))
        
        conn.commit()
        conn.close()
    
    def update_price(self, vehicle_id, prix):
        """Met à jour le prix d'une voiture"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE vehicles SET prix_current = ? WHERE id = ?', (prix, vehicle_id))
        conn.commit()
        conn.close()
    
    def add_price_history(self, vehicle_id, prix, statut):
        """Ajoute un historique de prix"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO price_history (vehicle_id, prix, date_check, statut)
            VALUES (?, ?, ?, ?)
        ''', (vehicle_id, prix, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), statut))
        
        conn.commit()
        conn.close()
    
    def get_all_active_vehicles(self):
        """Récupère toutes les voitures actives"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM vehicles WHERE statut = "ACTIVE" ORDER BY id DESC')
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_all_vehicles(self):
        """Récupère toutes les voitures (actives + vendues)"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM vehicles ORDER BY id DESC')
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_vehicles_without_details(self, limit=50):
        """Récupère les voitures qui n'ont pas encore de détails (ville NULL)"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, lien FROM vehicles 
            WHERE ville IS NULL AND lien IS NOT NULL AND lien != 'N/A' AND lien != '#'
            ORDER BY id DESC
            LIMIT ?
        ''', (limit,))
        results = cursor.fetchall()
        conn.close()
        return results
    
    def update_vehicle_details(self, vehicle_id, details):
        """Met à jour les détails d'une voiture"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Construire la requête de mise à jour dynamique
        updates = []
        values = []
        
        fields = ['ville', 'code_postal', 'departement', 'region', 'type_vendeur',
                  'energie', 'boite_vitesse', 'couleur', 'nb_portes', 'nb_places',
                  'puissance_fiscale', 'puissance_din', 'emission_co2', 'critair',
                  'premiere_main', 'non_fumeur', 'carnet_entretien', 'ct_ok', 
                  'garantie', 'nb_photos', 'marque', 'modele', 'annee', 'km', 'description']
        
        for field in fields:
            if details.get(field):
                updates.append(f"{field} = ?")
                values.append(details[field])
        
        if updates:
            values.append(vehicle_id)
            query = f"UPDATE vehicles SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
        
        conn.close()
        return len(updates) > 0


# ============================================================================
# SCRAPER LEBONCOIN
# ============================================================================

class LeBonCoinScraper:
    """Scraper LeBonCoin avec suivi des voitures et ANTI-DETECTION"""
    
    # Liste de User-Agents pour rotation
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0',
    ]
    
    def __init__(self):
        self.db = DatabaseManager()
        self.session = requests.Session()  # Session pour cookies persistants
        self.request_count = 0
        self.photos_dir = 'voitures_photos'
        os.makedirs(self.photos_dir, exist_ok=True)
        
        # Configuration anti-détection RENFORCÉE
        self.min_delay = 3  # Délai minimum entre requêtes (secondes)
        self.max_delay = 7  # Délai maximum entre requêtes (secondes)
        self.max_retries = 3  # Nombre de tentatives en cas d'échec
        self.blocked = False  # Flag si on est bloqué
        
        print("[ANTI-DETECTION] Configuration activee:")
        print(f"  - Rotation User-Agent: {len(self.USER_AGENTS)} agents")
        print(f"  - Delai aleatoire: {self.min_delay}-{self.max_delay} sec")
        print(f"  - Session avec cookies: OUI")
        print(f"  - Retry automatique: {self.max_retries} tentatives")
        print("")
    
    def get_random_headers(self):
        """Génère des headers aléatoires pour chaque requête"""
        user_agent = random.choice(self.USER_AGENTS)
        return {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',  # Do Not Track
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.leboncoin.fr/',
        }
    
    def smart_delay(self):
        """Applique un délai aléatoire entre les requêtes"""
        delay = random.uniform(self.min_delay, self.max_delay)
        print(f"[DELAY] Attente {delay:.1f}s...")
        time.sleep(delay)
    
    def safe_request(self, url, retries=None):
        """Effectue une requête avec anti-détection et retry automatique"""
        if retries is None:
            retries = self.max_retries
        
        for attempt in range(retries):
            try:
                self.request_count += 1
                headers = self.get_random_headers()
                
                # Délai avant chaque requête (sauf la première)
                if self.request_count > 1:
                    self.smart_delay()
                
                print(f"[REQ #{self.request_count}] {url[:60]}...")
                response = self.session.get(url, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 403:
                    print(f"[WARN] Accès refusé (403) - Tentative {attempt+1}/{retries}")
                    print(f"[ANTI-DETECT] Pause longue de 60 secondes...")
                    time.sleep(60)  # Attendre 1 minute si bloqué
                    self.session = requests.Session()  # Nouvelle session
                    self.blocked = True
                elif response.status_code == 429:
                    print(f"[WARN] Trop de requêtes (429) - Pause très longue...")
                    time.sleep(120)  # Pause de 2 min si rate limit
                    self.session = requests.Session()
                else:
                    print(f"[WARN] Code {response.status_code} - Tentative {attempt+1}/{retries}")
                    
            except requests.exceptions.Timeout:
                print(f"[WARN] Timeout - Tentative {attempt+1}/{retries}")
            except requests.exceptions.RequestException as e:
                print(f"[ERROR] Requête échouée: {e}")
        
        print(f"[FAIL] Échec après {retries} tentatives")
        return None
    
    def download_photo(self, photo_url, vehicle_id, index=0):
        """Télécharge une photo de voiture avec anti-détection"""
        try:
            # Créer dossier pour ce véhicule
            vehicle_dir = f"{self.photos_dir}/vehicle_{vehicle_id}"
            os.makedirs(vehicle_dir, exist_ok=True)
            
            filename = f"{vehicle_dir}/photo_{index}.jpg"
            
            # Vérifier si déjà téléchargée
            if os.path.exists(filename):
                return filename
            
            # Utiliser requests avec headers au lieu de urllib
            headers = self.get_random_headers()
            response = self.session.get(photo_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(response.content)
                return filename
            else:
                return None
        except Exception as e:
            return None
    
    def download_all_photos(self, vehicle_id, photo_urls):
        """Télécharge toutes les photos d'un véhicule"""
        downloaded = []
        for i, url in enumerate(photo_urls[:10]):  # Max 10 photos par véhicule
            if url:
                path = self.download_photo(url, vehicle_id, i)
                if path:
                    downloaded.append(path)
                    # Sauvegarder dans la table photos
                    self.save_photo_to_db(vehicle_id, url, path)
                time.sleep(0.5)  # Petit délai entre photos
        return downloaded
    
    def save_photo_to_db(self, vehicle_id, url, path):
        """Sauvegarde une photo dans la base de données"""
        try:
            conn = sqlite3.connect(self.db.db_name)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO photos (vehicle_id, url, path_local, date_downloaded)
                VALUES (?, ?, ?, ?)
            ''', (vehicle_id, url, path, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            conn.commit()
            conn.close()
        except Exception as e:
            pass
    
    def extract_vehicle_info(self, annonce):
        """Extrait les infos détaillées d'une voiture depuis la liste"""
        try:
            texte = annonce.get_text(strip=True)
            
            # Extraire le prix
            prix_match = re.search(r'(\d+[\s\u202f\xa0]*)+\s*€', texte)
            prix = prix_match.group(0).strip() if prix_match else "N/A"
            
            # Extraire l'année (4 chiffres commençant par 19 ou 20)
            annee_match = re.search(r'\b(19|20)\d{2}\b', texte)
            annee = annee_match.group(0) if annee_match else None
            
            # Extraire les km (nombre suivi de km)
            km_match = re.search(r'(\d+[\s\u202f\xa0]*)+\s*km', texte, re.IGNORECASE)
            km = km_match.group(0).strip() if km_match else None
            
            # Extraire la ville/localisation (souvent à la fin, format "Ville (XX)")
            ville_match = re.search(r'([A-Za-zÀ-ÿ\s\-]+)\s*\((\d{2})\)', texte)
            ville = ville_match.group(1).strip() if ville_match else None
            code_postal = ville_match.group(2) if ville_match else None
            
            # Chercher type vendeur (Particulier ou Pro)
            type_vendeur = 'Particulier' if 'particulier' in texte.lower() else ('Pro' if 'pro' in texte.lower() else None)
            
            # Chercher énergie
            energie = None
            for e in ['Diesel', 'Essence', 'Électrique', 'Hybride', 'GPL', 'Electrique']:
                if e.lower() in texte.lower():
                    energie = e
                    break
            
            # Chercher boîte de vitesse
            boite = None
            if 'automatique' in texte.lower() or 'auto' in texte.lower():
                boite = 'Automatique'
            elif 'manuelle' in texte.lower() or 'manuel' in texte.lower():
                boite = 'Manuelle'
            
            # Extraire la marque et modele (premiers mots du titre)
            # Nettoyer le texte pour avoir le titre
            titre_clean = texte[:200]
            parties = titre_clean.split()
            marque = parties[0] if len(parties) > 0 else "N/A"
            modele = parties[1] if len(parties) > 1 else "N/A"
            
            # Créer un hash unique basé sur le lien ou le titre
            lien = annonce.get('href', '')
            unique_str = lien if lien else texte[:100]
            unique_hash = abs(hash(unique_str)) % (10 ** 10)
            
            # Compter les images si disponible
            images = annonce.find_all('img')
            nb_photos = len(images) if images else 0
            
            # Extraire l'image principale
            img = annonce.find('img')
            photo_principale = img.get('src') if img else None
            
            return {
                'unique_hash': str(unique_hash),
                'titre': titre_clean[:150],
                'prix': prix,
                'marque': marque,
                'modele': modele,
                'annee': annee,
                'km': km,
                'ville': ville,
                'code_postal': code_postal,
                'type_vendeur': type_vendeur,
                'energie': energie,
                'boite_vitesse': boite,
                'photo_principale': photo_principale,
                'nb_photos': str(nb_photos) if nb_photos else None,
                'description': texte[:500]
            }
        except Exception as e:
            print("[ERROR] Info extraction: " + str(e))
            return None
    
    def scrape_annonce_detail(self, url):
        """Scrape les détails complets d'une annonce individuelle"""
        try:
            response = self.safe_request(url)
            if not response:
                return {}
            
            soup = BeautifulSoup(response.content, 'html.parser')
            details = {}
            texte_page = soup.get_text(separator=' ')
            
            # ===== 1. DONNÉES JSON-LD (structured data) =====
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        if data.get('@type') in ['Car', 'Vehicle', 'Product']:
                            # Marque et modèle
                            if isinstance(data.get('brand'), dict):
                                details['marque'] = data['brand'].get('name')
                            elif data.get('brand'):
                                details['marque'] = data.get('brand')
                            details['modele'] = data.get('model')
                            
                            # Année
                            details['annee'] = data.get('vehicleModelDate') or data.get('productionDate')
                            
                            # Kilométrage
                            if isinstance(data.get('mileageFromOdometer'), dict):
                                details['km'] = str(data['mileageFromOdometer'].get('value', ''))
                            
                            # Couleur
                            details['couleur'] = data.get('color')
                            
                            # Énergie
                            details['energie'] = data.get('fuelType')
                            
                            # Transmission
                            details['boite_vitesse'] = data.get('vehicleTransmission')
                            
                            # Prix
                            if isinstance(data.get('offers'), dict):
                                details['prix'] = data['offers'].get('price')
                            
                            # Description
                            details['description'] = data.get('description', '')[:500]
                            
                            # Titre
                            details['titre'] = data.get('name', '')
                except Exception as e:
                    pass
            
            # ===== 2. LOCALISATION (AMELIOREE) =====
            ville_found = None
            code_postal_found = None
            
            # Méthode 1: Chercher dans le JSON-LD les données de localisation
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        # Chercher dans offers.availableAtOrFrom ou location
                        location = data.get('availableAtOrFrom') or data.get('contentLocation') or {}
                        if isinstance(location, dict):
                            address = location.get('address') or {}
                            if isinstance(address, dict):
                                ville_found = address.get('addressLocality') or address.get('addressRegion')
                                code_postal_found = address.get('postalCode')
                            elif isinstance(address, str):
                                # Extraire code postal de l'adresse
                                cp_match = re.search(r'(\d{5})', address)
                                if cp_match:
                                    code_postal_found = cp_match.group(1)
                                # Le reste est la ville
                                ville_match = re.search(r'([A-Za-zÀ-ÿ\-\s]+)', address)
                                if ville_match:
                                    ville_found = ville_match.group(1).strip()
                except:
                    pass
            
            # Méthode 2: Chercher les balises HTML avec data-qa-id de localisation
            if not ville_found:
                location_div = soup.find(['div', 'span', 'p'], {'data-qa-id': re.compile(r'adview.*location|location|city|address', re.I)})
                if location_div:
                    loc_text = location_div.get_text(strip=True)
                    # Extraire code postal
                    cp_match = re.search(r'(\d{5})', loc_text)
                    if cp_match:
                        code_postal_found = cp_match.group(1)
                    # Extraire ville (texte avant ou après le code postal)
                    if code_postal_found:
                        # Chercher la ville autour du code postal
                        ville_match = re.search(rf'([A-Za-zÀ-ÿ\-\s]{{2,30}})\s*{code_postal_found}|{code_postal_found}\s*([A-Za-zÀ-ÿ\-\s]{{2,30}})', loc_text)
                        if ville_match:
                            ville_found = (ville_match.group(1) or ville_match.group(2)).strip()
            
            # Méthode 3: Chercher un pattern spécifique pour la localisation LeBonCoin
            if not ville_found:
                # LeBonCoin affiche souvent "Ville (XXXXX)" ou dans un format spécifique
                # Chercher après des mots-clés comme "Localisation", "Lieu", etc.
                loc_patterns = [
                    r'(?:Localisation|Lieu|Adresse|Location)[:\s]+([A-Za-zÀ-ÿ\-\s]{2,30})\s*\(?(\d{5})?\)?',
                    r'(\d{5})\s+([A-Za-zÀ-ÿ\-]{2,25})\b',  # 87000 Limoges
                    r'\b([A-Za-zÀ-ÿ\-]{3,25})\s*\((\d{5})\)',  # Limoges (87000)
                ]
                for pattern in loc_patterns:
                    match = re.search(pattern, texte_page, re.IGNORECASE)
                    if match:
                        groups = match.groups()
                        # Déterminer quel groupe est la ville et quel est le code postal
                        for g in groups:
                            if g:
                                if re.match(r'^\d{5}$', g):
                                    code_postal_found = g
                                elif len(g) > 2 and not g.isdigit():
                                    # Vérifier que ce n'est pas une marque de voiture
                                    marques = ['RENAULT', 'PEUGEOT', 'CITROEN', 'MERCEDES', 'BMW', 'AUDI', 'VOLKSWAGEN', 
                                               'TOYOTA', 'FIAT', 'OPEL', 'FORD', 'SEAT', 'MINI', 'PORSCHE', 'DS', 
                                               'DACIA', 'HYUNDAI', 'KIA', 'NISSAN', 'HONDA', 'MAZDA', 'VOLVO', 'SKODA']
                                    if g.upper().strip() not in marques and not any(m in g.upper() for m in marques):
                                        ville_found = g.strip()
                        if ville_found:
                            break
            
            # Méthode 4: Chercher dans les scripts JS les données de localisation
            if not ville_found:
                for script in soup.find_all('script'):
                    script_text = script.string or ''
                    # Chercher city, location, zipcode dans le JS
                    city_match = re.search(r'["\'](?:city|ville|city_name)["\']:\s*["\']([^"\']+)["\']', script_text, re.I)
                    if city_match:
                        ville_found = city_match.group(1)
                    zipcode_match = re.search(r'["\'](?:zipcode|postal_code|code_postal)["\']:\s*["\']?(\d{5})["\']?', script_text, re.I)
                    if zipcode_match:
                        code_postal_found = zipcode_match.group(1)
                    if ville_found:
                        break
            
            # Sauvegarder les résultats
            if ville_found:
                # Nettoyer la ville
                ville_found = re.sub(r'[0-9]', '', ville_found).strip()
                # Liste de textes parasites à exclure
                textes_parasites = [
                    'en ligne', 'votre espace', 'bailleur', 'annonce', 'favori',
                    'voir plus', 'contacter', 'message', 'téléphone', 'appeler',
                    'prix', 'euro', 'paiement', 'sécurisé', 'livraison'
                ]
                est_parasite = any(t in ville_found.lower() for t in textes_parasites)
                if len(ville_found) > 2 and len(ville_found) < 40 and not est_parasite:
                    details['ville'] = ville_found[:50]
            if code_postal_found:
                details['code_postal'] = code_postal_found
            
            # Département depuis code postal
            if details.get('code_postal'):
                details['departement'] = details['code_postal'][:2]
            
            # ===== 3. TYPE VENDEUR (détection améliorée) =====
            # Chercher dans le HTML les indices du type de vendeur
            type_vendeur_found = None
            
            # Pattern 1: Texte direct "Particulier" ou "Professionnel"
            if re.search(r'\bParticulier\b', texte_page, re.IGNORECASE):
                type_vendeur_found = 'Particulier'
            elif re.search(r'\bProfessionnel\b', texte_page, re.IGNORECASE):
                type_vendeur_found = 'Professionnel'
            
            # Pattern 2: Indices de pro (garage, concessionnaire, SIRET, etc.)
            if not type_vendeur_found:
                pro_patterns = [
                    r'garage', r'concessionnaire', r'automobiles?', r'auto\s+center',
                    r'siret', r'siren', r'tva\s+intra', r'ste\s+', r'sarl', r'sas\b',
                    r'groupe\s+\w+', r'motors?', r'car\s+center', r'auto\s+\w+\s+\w+',
                    r'financement', r'reprise', r'garantie\s+\d+\s*(mois|an)'
                ]
                for pattern in pro_patterns:
                    if re.search(pattern, texte_page, re.IGNORECASE):
                        type_vendeur_found = 'Professionnel'
                        break
            
            # Pattern 3: Si toujours pas trouvé, chercher dans les balises HTML spécifiques
            if not type_vendeur_found:
                # Chercher les éléments qui indiquent le type
                seller_div = soup.find('div', {'data-qa-id': 'adview_seller_info'})
                if seller_div:
                    seller_text = seller_div.get_text()
                    if 'pro' in seller_text.lower():
                        type_vendeur_found = 'Professionnel'
                    else:
                        type_vendeur_found = 'Particulier'
            
            # Par défaut, si on a un numéro de téléphone affiché directement = souvent particulier
            if not type_vendeur_found:
                if re.search(r'06\s*\d{2}\s*\d{2}\s*\d{2}\s*\d{2}|07\s*\d{2}\s*\d{2}\s*\d{2}\s*\d{2}', texte_page):
                    type_vendeur_found = 'Particulier'
            
            if type_vendeur_found:
                details['type_vendeur'] = type_vendeur_found
            
            # ===== 3B. EXTRACTION ID/NOM DU VENDEUR (AMELIOREE) =====
            vendeur_id = None
            vendeur_nom = None
            
            # Méthode 1: Chercher dans TOUS les scripts (pas seulement JSON-LD)
            for script in soup.find_all('script'):
                script_text = script.string or ''
                
                # Chercher user_id, store_id, owner_id dans le JS
                id_patterns = [
                    r'["\']user_id["\']\s*[:"]\s*["\']?(\d+)["\']?',
                    r'["\']store_id["\']\s*[:"]\s*["\']?(\d+)["\']?',
                    r'["\']owner_id["\']\s*[:"]\s*["\']?(\d+)["\']?',
                    r'["\']seller_id["\']\s*[:"]\s*["\']?(\d+)["\']?',
                    r'["\']author_id["\']\s*[:"]\s*["\']?(\d+)["\']?',
                    r'userId["\']?\s*[:"]\s*["\']?(\d+)',
                    r'storeId["\']?\s*[:"]\s*["\']?(\d+)',
                ]
                for pattern in id_patterns:
                    match = re.search(pattern, script_text, re.IGNORECASE)
                    if match and not vendeur_id:
                        vendeur_id = match.group(1)
                        break
                
                # Chercher le nom dans le JSON
                name_patterns = [
                    r'["\'](?:seller_name|store_name|user_name|owner_name|name)["\']\s*:\s*["\']([^"\']+)["\']',
                    r'"name"\s*:\s*"([^"]+)".*?(?:seller|store|owner)',
                ]
                for pattern in name_patterns:
                    match = re.search(pattern, script_text, re.IGNORECASE)
                    if match and not vendeur_nom:
                        vendeur_nom = match.group(1).strip()
                        break
            
            # Méthode 2: JSON-LD structured data
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        seller = data.get('seller') or data.get('author') or data.get('offers', {}).get('seller') or {}
                        if isinstance(seller, dict):
                            if not vendeur_id:
                                vendeur_id = seller.get('identifier') or seller.get('@id') or seller.get('id') or seller.get('url', '').split('/')[-1]
                            if not vendeur_nom:
                                vendeur_nom = seller.get('name') or seller.get('legalName')
                except:
                    pass
            
            # Méthode 3: Liens vers le profil vendeur
            if not vendeur_id:
                profile_patterns = [r'/profile/', r'/store/', r'/pro/', r'/user/', r'store_id=', r'user_id=']
                for pattern in profile_patterns:
                    profile_link = soup.find('a', href=re.compile(pattern))
                    if profile_link:
                        href = profile_link.get('href', '')
                        id_match = re.search(r'(?:profile|store|pro|user|store_id|user_id)[=/](\w+)', href)
                        if id_match:
                            vendeur_id = id_match.group(1)
                        if not vendeur_nom:
                            vendeur_nom = profile_link.get_text(strip=True)
                        break
            
            # Méthode 4: Attributs data-* des éléments vendeur
            seller_elements = soup.find_all(['div', 'span', 'a', 'section'], 
                {'data-qa-id': re.compile(r'seller|store|owner|user|adview_contact', re.I)})
            for elem in seller_elements:
                if not vendeur_nom:
                    text = elem.get_text(strip=True)
                    if text and len(text) > 2 and len(text) < 100:
                        vendeur_nom = text
                # Chercher l'ID dans les attributs
                for attr in ['data-user-id', 'data-store-id', 'data-seller-id', 'data-owner-id']:
                    if elem.get(attr) and not vendeur_id:
                        vendeur_id = elem.get(attr)
            
            # Méthode 5: Pattern textuel dans la page
            if not vendeur_nom:
                patterns = [
                    r'(?:vendeur|vendu par|contact|par)\s*[:\s]\s*([A-Za-zÀ-ÿ0-9\s\-\']{3,50}?)(?:\s*\(|\s*-|\s*Voir|$)',
                    r'(?:Garage|Auto|Automobiles?)\s+([A-Za-zÀ-ÿ\s\-\']+)',
                ]
                for pattern in patterns:
                    match = re.search(pattern, texte_page, re.IGNORECASE)
                    if match:
                        vendeur_nom = match.group(1).strip()[:80]
                        break
            
            # Méthode 6: Pour les pros, chercher SIRET/nom société
            if not vendeur_nom and type_vendeur_found == 'Professionnel':
                societe_patterns = [
                    r'\b((?:SARL|SAS|EURL|SA|SCI)\s+[A-Za-zÀ-ÿ\s\-\']+)',
                    r'\b([A-Z][A-Za-z]+\s+(?:AUTO|AUTOMOBILES?|MOTORS?|GARAGE|CAR))\b',
                    r'\b((?:AUTO|GARAGE|MOTORS?)\s+[A-Za-zÀ-ÿ\s\-\']+)\b',
                ]
                for pattern in societe_patterns:
                    match = re.search(pattern, texte_page)
                    if match:
                        vendeur_nom = match.group(1).strip()[:80]
                        break
            
            # Nettoyer et sauvegarder
            if vendeur_id:
                details['vendeur_id'] = str(vendeur_id)[:50]
            if vendeur_nom:
                # Nettoyer le nom (enlever caractères spéciaux)
                vendeur_nom = re.sub(r'[\n\r\t]+', ' ', vendeur_nom).strip()
                details['vendeur_nom'] = vendeur_nom[:100]
            
            # ===== 4. CARACTÉRISTIQUES TECHNIQUES =====
            # Énergie (si pas trouvé dans JSON)
            if not details.get('energie'):
                energies = ['Diesel', 'Essence', 'Électrique', 'Electrique', 'Hybride', 'GPL', 'Hybride rechargeable']
                for e in energies:
                    if e.lower() in texte_page.lower():
                        details['energie'] = e
                        break
            
            # Boîte de vitesse (si pas trouvé dans JSON)
            if not details.get('boite_vitesse'):
                if re.search(r'\bautomatique\b|\bauto\b', texte_page, re.IGNORECASE):
                    details['boite_vitesse'] = 'Automatique'
                elif re.search(r'\bmanuelle?\b|\bmanuel\b', texte_page, re.IGNORECASE):
                    details['boite_vitesse'] = 'Manuelle'
            
            # Puissance fiscale
            cv_match = re.search(r'(\d+)\s*cv\s*fiscaux?', texte_page, re.IGNORECASE)
            if cv_match:
                details['puissance_fiscale'] = cv_match.group(1)
            
            # Puissance DIN
            din_match = re.search(r'(\d+)\s*ch\b', texte_page, re.IGNORECASE)
            if din_match:
                details['puissance_din'] = din_match.group(1)
            
            # Nombre de portes
            portes_match = re.search(r'(\d)\s*portes?', texte_page, re.IGNORECASE)
            if portes_match:
                details['nb_portes'] = portes_match.group(1)
            
            # Nombre de places
            places_match = re.search(r'(\d)\s*places?', texte_page, re.IGNORECASE)
            if places_match:
                details['nb_places'] = places_match.group(1)
            
            # Émission CO2
            co2_match = re.search(r'(\d+)\s*g?\/?km', texte_page, re.IGNORECASE)
            if co2_match:
                details['emission_co2'] = co2_match.group(1)
            
            # Crit'Air
            critair_match = re.search(r"crit'?air\s*(\d)", texte_page, re.IGNORECASE)
            if critair_match:
                details['critair'] = critair_match.group(1)
            
            # ===== 5. CRITÈRES QUALITATIFS =====
            criteres = {
                'premiere_main': [r'première?\s*main', r"1[èe]re?\s*main"],
                'non_fumeur': [r'non[\s\-]?fumeur'],
                'carnet_entretien': [r"carnet\s*d'?entretien"],
                'ct_ok': [r'contrôle\s*technique\s*(ok|valide)', r'ct\s*(ok|valide)'],
                'garantie': [r'garantie\s*(\d+\s*(mois|an))?']
            }
            
            for key, patterns in criteres.items():
                for pattern in patterns:
                    if re.search(pattern, texte_page, re.IGNORECASE):
                        details[key] = 'Oui'
                        break
            
            # ===== 6. PHOTOS (EXTRACTION COMPLETE) =====
            photo_urls = []
            
            # Méthode 1: Images dans les balises img avec URL LeBonCoin
            images = soup.find_all('img', src=re.compile(r'leboncoin|lbc|img\d+\.leboncoin'))
            for img in images:
                src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                if src and 'leboncoin' in src and src not in photo_urls:
                    # Convertir en URL haute qualité
                    src = src.replace('ad-thumb', 'ad-large').replace('ad-small', 'ad-large')
                    photo_urls.append(src)
            
            # Méthode 2: Chercher dans les scripts JSON
            for script in soup.find_all('script'):
                script_text = script.string or ''
                # Chercher les URLs d'images dans le JSON
                img_matches = re.findall(r'https://img\.leboncoin\.fr[^"\s]+\.jpg', script_text)
                for match in img_matches:
                    if match not in photo_urls:
                        photo_urls.append(match)
            
            # Méthode 3: Attributs data-* des conteneurs d'images
            for container in soup.find_all(['div', 'figure', 'picture'], {'data-qa-id': re.compile(r'image|photo|gallery', re.I)}):
                for img in container.find_all('img'):
                    src = img.get('src') or img.get('data-src')
                    if src and 'leboncoin' in src and src not in photo_urls:
                        photo_urls.append(src)
            
            details['nb_photos'] = str(len(photo_urls)) if photo_urls else '0'
            details['photos'] = photo_urls[:20]  # Max 20 photos
            
            # Photo principale = première photo haute qualité
            if photo_urls:
                details['photo_principale'] = photo_urls[0]
            
            return details
            
        except Exception as e:
            print(f"[WARN] Detail scraping failed: {e}")
            return {}
    
    def scrape_page(self, url):
        """Scrape une seule page et retourne les annonces avec leurs liens"""
        response = self.safe_request(url)
        if not response:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Chercher tous les liens vers des annonces
        annonces_data = []
        
        # Méthode 1: Liens directs avec classe contenant "ad" ou "listing"
        links = soup.find_all('a', href=re.compile(r'/ad/voitures/|/voitures/\d+'))
        
        # Méthode 2: Chercher dans les articles
        if not links:
            articles = soup.find_all('article')
            for article in articles:
                link = article.find('a', href=True)
                if link and '/ad/' in link.get('href', ''):
                    links.append(link)
        
        # Méthode 3: Tous les liens contenant /ad/
        if not links:
            links = soup.find_all('a', href=re.compile(r'/ad/'))
        
        seen_hrefs = set()
        for link in links:
            href = link.get('href', '')
            if href and '/ad/' in href and href not in seen_hrefs:
                seen_hrefs.add(href)
                full_url = href if href.startswith('http') else 'https://www.leboncoin.fr' + href
                annonces_data.append({
                    'element': link,
                    'url': full_url
                })
        
        print(f"[DEBUG] {len(annonces_data)} liens d'annonces trouvés")
        return annonces_data
    
    def scrape(self, url="https://www.leboncoin.fr/voitures/offres/", max_pages=10):
        """Scrape LeBonCoin sur PLUSIEURS PAGES avec anti-détection avancée"""
        print("\n" + "=" * 70)
        print("[LEBONCOIN SCRAPER MULTI-PAGES] - Scraping en cours")
        print("[ANTI-DETECTION] Mode activé - Session intelligente")
        print("[CONFIG] Pages max: " + str(max_pages))
        print("[TIME] " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print("=" * 70 + "\n")
        
        try:
            nouvelles_voitures = 0
            voitures_vendues = 0
            voitures_maj = 0
            total_annonces = 0
            all_annonces_hashes = set()  # Pour éviter les doublons
            
            # ====== SCRAPING MULTI-PAGES ======
            for page_num in range(1, max_pages + 1):
                # Construire l'URL avec pagination
                if page_num == 1:
                    page_url = url
                else:
                    # LeBonCoin utilise ?page=X pour la pagination
                    separator = '&' if '?' in url else '?'
                    page_url = f"{url}{separator}page={page_num}"
                
                print(f"\n[PAGE {page_num}/{max_pages}] {page_url[:70]}...")
                
                # Vérifier si on a été bloqué précédemment
                if self.blocked:
                    print("[ANTI-DETECT] Détection de blocage - Pause de 2 minutes...")
                    time.sleep(120)
                    self.blocked = False
                    self.session = requests.Session()
                
                # Pause LONGUE entre les pages pour éviter détection
                if page_num > 1:
                    pause = random.uniform(10, 20)  # 10-20 sec entre pages
                    print(f"[ANTI-DETECT] Pause inter-page: {pause:.1f}s")
                    time.sleep(pause)
                
                # Nouvelle session tous les 2 pages pour éviter le tracking
                if page_num % 2 == 0:
                    print("[ANTI-DETECT] Rotation de session...")
                    self.session = requests.Session()
                    time.sleep(3)
                
                annonces = self.scrape_page(page_url)
                
                if not annonces:
                    print(f"[INFO] Aucune annonce trouvée sur page {page_num} - Fin du scraping")
                    break
                
                print(f"[STAT] {len(annonces)} annonces sur cette page")
                total_annonces += len(annonces)
                
                # Traiter chaque annonce
                for i, annonce_data in enumerate(annonces):
                    try:
                        annonce = annonce_data['element']
                        lien = annonce_data['url']
                        
                        # Utiliser le lien comme hash unique (plus fiable)
                        unique_hash = abs(hash(lien)) % (10 ** 10)
                        
                        # Éviter les doublons inter-pages
                        if str(unique_hash) in all_annonces_hashes:
                            continue
                        all_annonces_hashes.add(str(unique_hash))
                        
                        # Chercher si la voiture existe déjà
                        existing = self.db.get_vehicle_by_hash(str(unique_hash))
                        
                        if existing:
                            # Voiture existante - juste mettre à jour
                            vehicle_id = existing[0]
                            if existing[8] == 'ACTIVE':  # statut
                                voitures_maj += 1
                            continue
                        
                        # ====== SCRAPER TOUS LES DÉTAILS DE LA PAGE INDIVIDUELLE ======
                        print(f"  [{i+1}/{len(annonces)}] Scraping détails: {lien[:50]}...")
                        
                        # Pause anti-détection entre chaque annonce
                        if i > 0:
                            pause = random.uniform(8, 15)  # 8-15 sec entre chaque
                            print(f"    [WAIT] Pause {pause:.1f}s...")
                            time.sleep(pause)
                        
                        # Rotation de session tous les 5 véhicules
                        if i > 0 and i % 5 == 0:
                            print("    [ANTI-DETECT] Rotation de session...")
                            self.session = requests.Session()
                            time.sleep(3)
                        
                        # Scraper les détails complets de la page
                        details = self.scrape_annonce_detail(lien)
                        
                        if not details:
                            print(f"    [SKIP] Impossible de récupérer les détails")
                            continue
                        
                        # Préparer les données complètes
                        vehicle_info = {
                            'unique_hash': str(unique_hash),
                            'lien': lien,
                            'date_annonce': datetime.now().strftime('%Y-%m-%d'),
                            'titre': details.get('titre', ''),
                            'prix': details.get('prix'),
                            'marque': details.get('marque'),
                            'modele': details.get('modele'),
                            'annee': details.get('annee'),
                            'km': details.get('km'),
                            'ville': details.get('ville'),
                            'code_postal': details.get('code_postal'),
                            'departement': details.get('departement'),
                            'region': details.get('region'),
                            'type_vendeur': details.get('type_vendeur'),
                            'energie': details.get('energie'),
                            'boite_vitesse': details.get('boite_vitesse'),
                            'couleur': details.get('couleur'),
                            'nb_portes': details.get('nb_portes'),
                            'nb_places': details.get('nb_places'),
                            'puissance_fiscale': details.get('puissance_fiscale'),
                            'puissance_din': details.get('puissance_din'),
                            'emission_co2': details.get('emission_co2'),
                            'critair': details.get('critair'),
                            'premiere_main': details.get('premiere_main'),
                            'non_fumeur': details.get('non_fumeur'),
                            'carnet_entretien': details.get('carnet_entretien'),
                            'ct_ok': details.get('ct_ok'),
                            'garantie': details.get('garantie'),
                            'nb_photos': details.get('nb_photos'),
                            'photo_principale': details.get('photo_principale'),
                            'description': details.get('description'),
                        }
                        
                        # Ajouter vendeur_id et vendeur_nom
                        vehicle_info['vendeur_id'] = details.get('vendeur_id')
                        vehicle_info['vendeur_nom'] = details.get('vendeur_nom')
                        vehicle_info['photos'] = details.get('photos', [])
                        
                        # Nouvelle voiture avec TOUS les détails
                        vehicle_id = self.db.insert_vehicle(vehicle_info)
                        if vehicle_id:
                            nouvelles_voitures += 1
                            self.db.add_price_history(vehicle_id, vehicle_info['prix'], 'ACTIVE')
                            
                            # Télécharger les photos
                            photo_urls = details.get('photos', [])
                            if photo_urls:
                                downloaded = self.download_all_photos(vehicle_id, photo_urls)
                                print(f"    [PHOTOS] {len(downloaded)} photos téléchargées")
                            
                            marque = vehicle_info.get('marque', 'N/A')
                            energie = vehicle_info.get('energie', 'N/A')
                            ville = vehicle_info.get('ville', 'N/A')
                            vendeur = vehicle_info.get('vendeur_nom', 'N/A')
                            print(f"    [NEW #{vehicle_id}] {marque} | {energie} | {ville} | Vendeur: {vendeur}")
                        
                    except Exception as e:
                        continue
                
                # Arrêter si on a assez de données
                if nouvelles_voitures >= 500:
                    print("[INFO] 500+ nouvelles voitures - Arrêt préventif")
                    break
            
            # ====== DÉTECTION VOITURES VENDUES ======
            print("\n[CHECK] Vérification des voitures vendues...")
            anciennes = self.db.get_all_active_vehicles()
            
            for ancien in anciennes:
                if ancien['unique_hash'] not in all_annonces_hashes:
                    # Voiture n'est plus dans les annonces
                    jours_depuis = 0
                    try:
                        date_vue = datetime.strptime(ancien['date_last_seen'], '%Y-%m-%d %H:%M:%S')
                        jours_depuis = (datetime.now() - date_vue).days
                    except:
                        pass
                    
                    # Marquer comme vendue seulement si absente depuis 2+ jours
                    if jours_depuis >= 2:
                        voitures_vendues += 1
                        date_vendu = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        self.db.update_vehicle_status(ancien['id'], 'VENDUE', date_vendu)
                        print(f"[SOLD] Voiture #{ancien['id']} vendue après {jours_depuis} jours!")
            
            # ====== RÉSUMÉ ======
            print("\n" + "=" * 50)
            print("[SUMMARY] Résultats du scraping multi-pages")
            print("=" * 50)
            print(f"  Pages scrapées: {min(page_num, max_pages)}")
            print(f"  Total annonces vues: {total_annonces}")
            print(f"  Annonces uniques: {len(all_annonces_hashes)}")
            print(f"  Nouvelles voitures: {nouvelles_voitures}")
            print(f"  Voitures mises à jour: {voitures_maj}")
            print(f"  Voitures vendues détectées: {voitures_vendues}")
            print(f"  Requêtes HTTP effectuées: {self.request_count}")
            print("=" * 50)
            
            return True
        
        except Exception as e:
            print("[ERROR] " + str(e))
            return False
    
    def scrape_details(self, limit=20):
        """Scrape les détails des pages individuelles pour les véhicules sans détails"""
        print("\n" + "=" * 70)
        print("[DETAIL SCRAPER] - Scraping des pages individuelles")
        print("[ANTI-DETECTION] Mode activé - Délais longs entre requêtes")
        print(f"[CONFIG] Limite: {limit} véhicules")
        print("[TIME] " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print("=" * 70 + "\n")
        
        vehicles = self.db.get_vehicles_without_details(limit)
        
        if not vehicles:
            print("[INFO] Aucun véhicule sans détails trouvé")
            return 0
        
        print(f"[INFO] {len(vehicles)} véhicules à enrichir")
        
        enriched = 0
        failed = 0
        
        for i, vehicle in enumerate(vehicles):
            vehicle_id = vehicle['id']
            lien = vehicle['lien']
            
            print(f"\n[{i+1}/{len(vehicles)}] Véhicule #{vehicle_id}")
            print(f"  URL: {lien[:60]}...")
            
            # Pause TRÈS longue entre les requêtes (anti-détection renforcée)
            if i > 0:
                pause = random.uniform(15, 30)  # 15-30 secondes entre chaque
                print(f"  [WAIT] Pause {pause:.1f}s...")
                time.sleep(pause)
            
            # Rotation de session tous les 3 véhicules
            if i > 0 and i % 3 == 0:
                print("  [ANTI-DETECT] Rotation de session...")
                self.session = requests.Session()
                time.sleep(5)
            
            # Scraper les détails
            details = self.scrape_annonce_detail(lien)
            
            if details:
                # Mettre à jour en base
                if self.db.update_vehicle_details(vehicle_id, details):
                    enriched += 1
                    ville = details.get('ville', 'N/A')
                    energie = details.get('energie', 'N/A')
                    vendeur = details.get('type_vendeur', 'N/A')
                    print(f"  [OK] Enrichi: {ville} | {energie} | {vendeur}")
                else:
                    print(f"  [SKIP] Pas de nouvelles données")
            else:
                failed += 1
                print(f"  [FAIL] Impossible de récupérer les détails")
            
            # Vérifier si on est bloqué
            if self.blocked:
                print("\n[WARN] Blocage détecté - Arrêt du scraping détail")
                break
        
        print("\n" + "=" * 50)
        print("[SUMMARY] Résultats du scraping détail")
        print("=" * 50)
        print(f"  Véhicules traités: {len(vehicles)}")
        print(f"  Véhicules enrichis: {enriched}")
        print(f"  Échecs: {failed}")
        print(f"  Requêtes HTTP: {self.request_count}")
        print("=" * 50)
        
        return enriched
    
    def generate_report(self):
        """Génère un rapport CSV"""
        vehicles = self.db.get_all_vehicles()
        
        filename = 'leboncoin_rapport_complet.csv'
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'ID', 'Titre', 'Marque', 'Modele', 'Prix Initial', 
                    'Prix Actuel', 'Statut', 'Date Annonce', 'Date Premiere Vue',
                    'Date Dernière Vue', 'Date Vendu', 'Jours en Vente', 'Lien'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for vehicle in vehicles:
                    # Calculer les jours en vente
                    if vehicle['date_vendu']:
                        date1 = datetime.strptime(vehicle['date_first_seen'], '%Y-%m-%d %H:%M:%S')
                        date2 = datetime.strptime(vehicle['date_vendu'], '%Y-%m-%d %H:%M:%S')
                        jours = (date2 - date1).days
                    else:
                        date1 = datetime.strptime(vehicle['date_first_seen'], '%Y-%m-%d %H:%M:%S')
                        date2 = datetime.now()
                        jours = (date2 - date1).days
                    
                    writer.writerow({
                        'ID': vehicle['id'],
                        'Titre': vehicle['titre'],
                        'Marque': vehicle['marque'],
                        'Modele': vehicle['modele'],
                        'Prix Initial': vehicle['prix_initial'],
                        'Prix Actuel': vehicle['prix_current'],
                        'Statut': vehicle['statut'],
                        'Date Annonce': vehicle['date_annonce'],
                        'Date Premiere Vue': vehicle['date_first_seen'],
                        'Date Dernière Vue': vehicle['date_last_seen'],
                        'Date Vendu': vehicle['date_vendu'] if vehicle['date_vendu'] else 'N/A',
                        'Jours en Vente': jours,
                        'Lien': vehicle['lien']
                    })
            
            print("[REPORT] Rapport généré: " + filename)
            return filename
        
        except Exception as e:
            print("[ERROR] " + str(e))
            return None


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    scraper = LeBonCoinScraper()
    
    print("\n" + "=" * 70)
    print("[LEBONCOIN SCRAPER MULTI-PAGES] - WEB SCRAPING AVANCE")
    print("=" * 70)
    
    # Configuration
    MAX_PAGES = 15  # Nombre de pages à scraper (environ 35 annonces/page = 500+ voitures)
    URL_BASE = "https://www.leboncoin.fr/voitures/offres/"
    
    # Vous pouvez ajouter des filtres dans l'URL:
    # URL_BASE = "https://www.leboncoin.fr/voitures/offres/poitou_charentes/"  # Par région
    # URL_BASE = "https://www.leboncoin.fr/voitures/offres/?price_min=5000&price_max=20000"  # Par prix
    
    print(f"\n[CONFIG]")
    print(f"  - URL: {URL_BASE}")
    print(f"  - Pages max: {MAX_PAGES}")
    print(f"  - Estimation: ~{MAX_PAGES * 35} annonces potentielles")
    
    # Scraper multi-pages
    if scraper.scrape(url=URL_BASE, max_pages=MAX_PAGES):
        print("\n[SUCCESS] Scraping multi-pages réussi!")
        
        # Générer le rapport
        scraper.generate_report()
        
        print("\n[OUTPUT] Résultats:")
        print("  - Base de données: data/leboncoin.db")
        print("  - Rapport CSV: leboncoin_rapport_complet.csv")
        print("  - Photos: dossier voitures_photos/")
    else:
        print("\n[FAIL] Scraping échoué")
