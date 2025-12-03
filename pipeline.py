"""
CAR ANALYTICS PIPELINE v2.0
============================
Pipeline complet avec:
- Scraping Selenium + Anti-détection (undetected-chromedriver)
- Validation des données
- Transformations
- Génération de rapport HTML

Usage:
    python pipeline.py              → Exécution unique
    python pipeline.py --pages 3    → Scraper 3 pages
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import re
import sqlite3
import pandas as pd
import random
import logging
import requests
from datetime import datetime
from pathlib import Path
import sys

# ============================================================================
# CONFIGURATION
# ============================================================================

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
PHOTOS_DIR = Path("voitures_photos")
PHOTOS_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "vehicles.db"
REPORT_PATH = "car_analytics_rapport.html"

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M')}.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# UTILITAIRES
# ============================================================================

def random_delay(min_sec=2, max_sec=5):
    """Délai aléatoire pour simuler un humain"""
    time.sleep(random.uniform(min_sec, max_sec))

def download_photos(driver, source_id):
    """Télécharge les photos d'une annonce"""
    photos_folder = PHOTOS_DIR / f"vehicle_{source_id}"
    photos_folder.mkdir(exist_ok=True)
    
    downloaded = []
    
    try:
        # Méthode 1: Chercher les images via les éléments img
        img_elements = driver.find_elements(By.TAG_NAME, 'img')
        image_urls = set()
        
        for img in img_elements:
            try:
                src = img.get_attribute('src') or ''
                srcset = img.get_attribute('srcset') or ''
                
                # Vérifier si c'est une image LeBonCoin
                for url in [src] + srcset.split(','):
                    url = url.strip().split(' ')[0]  # Enlever le descripteur de taille
                    if 'leboncoin' in url and ('images' in url or 'lbcpb' in url):
                        if 'thumb' not in url.lower() and len(url) > 50:
                            image_urls.add(url)
            except:
                pass
        
        # Méthode 2: Chercher dans le source HTML
        page_source = driver.page_source
        patterns = [
            r'"(https://img\.leboncoin\.fr/api/v1/lbcpb1/images/[^"]+)"',
            r'"(https://[^"]*leboncoin[^"]*\.jpg[^"]*)"',
            r'"(https://[^"]*leboncoin[^"]*\.webp[^"]*)"',
        ]
        
        for pattern in patterns:
            found = re.findall(pattern, page_source)
            for url in found:
                if 'thumb' not in url.lower() and 'icon' not in url.lower():
                    image_urls.add(url.split('?')[0])
        
        # Télécharger chaque image (max 10)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.leboncoin.fr/'
        }
        
        for idx, img_url in enumerate(list(image_urls)[:10]):
            try:
                response = requests.get(img_url, headers=headers, timeout=10)
                if response.status_code == 200 and len(response.content) > 5000:  # Min 5KB
                    # Déterminer l'extension
                    ext = '.jpg'
                    if 'webp' in img_url:
                        ext = '.webp'
                    elif 'png' in img_url:
                        ext = '.png'
                    
                    photo_path = photos_folder / f"photo_{idx+1}{ext}"
                    with open(photo_path, 'wb') as f:
                        f.write(response.content)
                    downloaded.append(str(photo_path))
            except:
                pass
        
    except Exception as e:
        logger.warning(f"Erreur téléchargement photos: {e}")
    
    return downloaded

def init_database():
    """Initialise la base SQLite"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS vehicles (
        id INTEGER PRIMARY KEY,
        source_id TEXT UNIQUE,
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
        photos_path TEXT,
        date_scrape TEXT
    )''')
    conn.commit()
    conn.close()

# ============================================================================
# TASK 1: SCRAPING avec Anti-Détection
# ============================================================================

def task_scrape(max_pages=1, max_annonces=50):
    """Scrape LeBonCoin avec undetected-chromedriver"""
    logger.info("=" * 60)
    logger.info("TASK 1: SCRAPING (undetected-chromedriver)")
    logger.info("=" * 60)
    
    init_database()
    
    # Chrome avec anti-détection
    options = uc.ChromeOptions()
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-notifications')
    
    try:
        # Forcer la version de ChromeDriver compatible avec Chrome 142
        driver = uc.Chrome(options=options, version_main=142)
        logger.info("[OK] Chrome démarré (anti-détection activée)")
    except Exception as e:
        logger.error(f"[FAIL] Impossible de démarrer Chrome: {e}")
        return False
    
    vehicles = []
    
    try:
        # Collecter les URLs
        all_urls = []
        
        for page in range(1, max_pages + 1):
            if page == 1:
                url = "https://www.leboncoin.fr/c/voitures"
            else:
                url = f"https://www.leboncoin.fr/c/voitures/p-{page}"
            
            logger.info(f"[PAGE {page}/{max_pages}] {url}")
            driver.get(url)
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
                random_delay(0.8, 1.5)
            
            # Récupérer les URLs
            page_source = driver.page_source
            urls = list(set(re.findall(r'https://www\.leboncoin\.fr/ad/voitures/\d+', page_source)))
            all_urls.extend([u for u in urls if u not in all_urls])
            logger.info(f"  → {len(urls)} annonces sur cette page (total: {len(all_urls)})")
            
            if len(all_urls) >= max_annonces:
                break
        
        all_urls = all_urls[:max_annonces]
        logger.info(f"[SCRAPE] {len(all_urls)} annonces à scraper...")
        
        # Scraper chaque annonce
        for i, url in enumerate(all_urls):
            logger.info(f"  [{i+1}/{len(all_urls)}] Scraping...")
            
            try:
                driver.get(url)
                random_delay(3, 6)
                
                # Scroll aléatoire
                driver.execute_script(f'window.scrollTo(0, {random.randint(200, 500)});')
                random_delay(0.5, 1)
                
                text = driver.find_element(By.TAG_NAME, 'body').text
                lines = [l.strip() for l in text.split('\n') if l.strip()]
                
                data = {
                    'lien': url,
                    'source_id': url.split('/')[-1],
                    'date_scrape': datetime.now().isoformat()
                }
                
                # Ville et code postal
                for line in lines[:30]:
                    match = re.search(r'^(.+?)\s+(\d{5})\s*$', line)
                    if match:
                        ville = match.group(1).strip()
                        cp = match.group(2)
                        if len(ville) > 2 and not any(c.isdigit() for c in ville):
                            data['ville'] = ville
                            data['code_postal'] = cp
                            data['departement'] = cp[:2]
                            break
                
                # Prix
                for line in lines:
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
                
                # Extraire le titre (généralement dans les premières lignes)
                for line in lines[:15]:
                    # Le titre est souvent la première ligne longue qui n'est pas un menu
                    if len(line) > 15 and not any(x in line.lower() for x in ['accueil', 'recherche', 'connexion', 'publier', 'messages']):
                        # Vérifier que ça ressemble à un titre d'annonce auto
                        if any(x in line.upper() for x in ['PEUGEOT', 'RENAULT', 'CITROEN', 'BMW', 'AUDI', 'MERCEDES', 'VOLKSWAGEN', 'FORD', 'TOYOTA', 'FIAT', 'OPEL', 'NISSAN', 'HYUNDAI', 'KIA', 'SEAT', 'SKODA', 'DACIA', 'MINI', 'PORSCHE', 'VOLVO', 'MAZDA', 'SUZUKI', 'HONDA', 'MITSUBISHI', 'JEEP', 'LAND', 'ALFA', 'JAGUAR', 'LEXUS', 'TESLA', 'DS']):
                            data['titre'] = line
                            break
                
                # Caractéristiques
                for j, line in enumerate(lines):
                    line_lower = line.lower()
                    next_line = lines[j+1] if j+1 < len(lines) else ''
                    
                    if line_lower == 'marque':
                        data['marque'] = next_line.upper()
                    elif line_lower in ['modèle', 'modele']:
                        data['modele'] = next_line
                    elif 'année' in line_lower and next_line:
                        m = re.search(r'(\d{4})', next_line)
                        if m:
                            data['annee'] = int(m.group(1))
                    elif 'kilométrage' in line_lower and next_line:
                        # Amélioration: capturer tous les chiffres avec espaces/nbsp
                        # Format LeBonCoin: "30 000 km" ou "300000 km"
                        clean_km = next_line.replace('\xa0', '').replace('\u202f', '').replace(' ', '')
                        m = re.search(r'(\d+)', clean_km)
                        if m:
                            km_val = int(m.group(1))
                            # Validation: km entre 0 et 1 million
                            if 0 <= km_val <= 1000000:
                                data['km'] = km_val
                    elif line_lower == 'énergie':
                        data['energie'] = next_line
                    elif line_lower == 'boîte de vitesse' or line_lower == 'boite de vitesse':
                        # Vérifier que c'est bien une boîte (Manuelle/Automatique)
                        if next_line.lower() in ['manuelle', 'automatique', 'manuel', 'auto']:
                            data['boite_vitesse'] = next_line
                    elif line_lower == 'couleur':
                        data['couleur'] = next_line
                
                # 📸 Télécharger les photos
                photos = download_photos(driver, data['source_id'])
                data['nb_photos'] = len(photos)
                data['photos_path'] = str(PHOTOS_DIR / f"vehicle_{data['source_id']}")
                
                vehicles.append(data)
                logger.info(f"      → {data.get('marque', '?')} | {data.get('ville', '?')} | {data.get('prix', '?')}€ | 📸 {len(photos)} photos")
                
            except Exception as e:
                logger.warning(f"      [WARN] Erreur: {e}")
        
        # Sauvegarder en base
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        for v in vehicles:
            c.execute('''INSERT OR REPLACE INTO vehicles 
                (source_id, titre, prix, lien, marque, modele, annee, km,
                 energie, boite_vitesse, couleur, ville, code_postal, departement, 
                 nb_photos, photos_path, date_scrape)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                (v.get('source_id'), v.get('titre'), v.get('prix'), v.get('lien'),
                 v.get('marque'), v.get('modele'), v.get('annee'), v.get('km'),
                 v.get('energie'), v.get('boite_vitesse'), v.get('couleur'),
                 v.get('ville'), v.get('code_postal'), v.get('departement'),
                 v.get('nb_photos'), v.get('photos_path'), v.get('date_scrape')))
        
        conn.commit()
        conn.close()
        
        # Compter les photos téléchargées
        total_photos = sum(v.get('nb_photos', 0) for v in vehicles)
        logger.info(f"[OK] {len(vehicles)} véhicules sauvegardés | 📸 {total_photos} photos téléchargées")
        return True
        
    except Exception as e:
        logger.error(f"[FAIL] Erreur scraping: {e}")
        return False
    
    finally:
        try:
            driver.quit()
        except:
            pass

# ============================================================================
# TASK 2: VALIDATION
# ============================================================================

def task_validate():
    """Valide la qualité des données"""
    logger.info("=" * 60)
    logger.info("TASK 2: VALIDATION")
    logger.info("=" * 60)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM vehicles", conn)
        conn.close()
        
        if len(df) == 0:
            logger.error("[FAIL] Aucune donnée en base!")
            return False
        
        # Statistiques
        checks = {
            "total_records": len(df),
            "prix_rempli": f"{(df['prix'].notna().sum() / len(df) * 100):.1f}%",
            "marque_rempli": f"{(df['marque'].notna().sum() / len(df) * 100):.1f}%",
            "ville_rempli": f"{(df['ville'].notna().sum() / len(df) * 100):.1f}%",
            "km_rempli": f"{(df['km'].notna().sum() / len(df) * 100):.1f}%",
        }
        
        logger.info("--- QUALITÉ DES DONNÉES ---")
        for key, value in checks.items():
            logger.info(f"  {key}: {value}")
        
        # Validation
        prix_ok = df['prix'].notna().sum() / len(df) > 0.8
        marque_ok = df['marque'].notna().sum() / len(df) > 0.9
        
        if prix_ok and marque_ok:
            logger.info("[OK] Validation réussie")
            return True
        else:
            logger.warning("[WARN] Qualité insuffisante")
            return True  # Continue quand même
            
    except Exception as e:
        logger.error(f"[FAIL] Erreur validation: {e}")
        return False

# ============================================================================
# TASK 3: TRANSFORMATIONS
# ============================================================================

def task_transform():
    """Nettoie et enrichit les données"""
    logger.info("=" * 60)
    logger.info("TASK 3: TRANSFORMATIONS")
    logger.info("=" * 60)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Normaliser marques
        cursor.execute("UPDATE vehicles SET marque = UPPER(TRIM(marque)) WHERE marque IS NOT NULL")
        
        # Normaliser modèles
        cursor.execute("UPDATE vehicles SET modele = TRIM(modele) WHERE modele IS NOT NULL")
        
        # Calculer département si manquant
        cursor.execute("""
            UPDATE vehicles 
            SET departement = SUBSTR(code_postal, 1, 2) 
            WHERE departement IS NULL AND code_postal IS NOT NULL
        """)
        
        conn.commit()
        conn.close()
        
        logger.info("[OK] Transformations terminées")
        return True
        
    except Exception as e:
        logger.error(f"[FAIL] Erreur transformation: {e}")
        return False

# ============================================================================
# TASK 4: RAPPORT
# ============================================================================

def task_report():
    """Génère un rapport HTML"""
    logger.info("=" * 60)
    logger.info("TASK 4: GÉNÉRATION RAPPORT")
    logger.info("=" * 60)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM vehicles", conn)
        conn.close()
        
        if len(df) == 0:
            logger.warning("[WARN] Pas de données pour le rapport")
            return False
        
        # Statistiques
        stats = {
            'total': len(df),
            'prix_moyen': df['prix'].mean() if df['prix'].notna().any() else 0,
            'prix_median': df['prix'].median() if df['prix'].notna().any() else 0,
            'km_moyen': df['km'].mean() if df['km'].notna().any() else 0,
            'top_marques': df['marque'].value_counts().head(10).to_dict(),
            'top_villes': df['ville'].value_counts().head(10).to_dict(),
            'top_departements': df['departement'].value_counts().head(10).to_dict(),
        }
        
        # Générer HTML
        html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Rapport LeBonCoin - {datetime.now().strftime('%d/%m/%Y')}</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: #ff6600; text-align: center; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 30px 0; }}
        .stat-card {{ background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .stat-value {{ font-size: 32px; font-weight: bold; color: #ff6600; }}
        .stat-label {{ color: #666; margin-top: 5px; }}
        .section {{ background: white; padding: 25px; border-radius: 10px; margin: 20px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: #ff6600; color: white; }}
        tr:hover {{ background: #fff5ee; }}
        .bar {{ height: 20px; background: #ff6600; border-radius: 3px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚗 Rapport Marché Automobile LeBonCoin</h1>
        <p style="text-align:center;color:#666;">Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{stats['total']}</div>
                <div class="stat-label">Véhicules</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats['prix_moyen']:,.0f}€</div>
                <div class="stat-label">Prix moyen</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats['prix_median']:,.0f}€</div>
                <div class="stat-label">Prix médian</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats['km_moyen']:,.0f}</div>
                <div class="stat-label">KM moyen</div>
            </div>
        </div>
        
        <div class="section">
            <h2>🏆 Top 10 Marques</h2>
            <table>
                <tr><th>Marque</th><th>Nombre</th><th>Répartition</th></tr>
"""
        
        max_count = max(stats['top_marques'].values()) if stats['top_marques'] else 1
        for marque, count in stats['top_marques'].items():
            pct = (count / max_count) * 100
            html += f"""
                <tr>
                    <td><strong>{marque}</strong></td>
                    <td>{count}</td>
                    <td><div class="bar" style="width:{pct}%"></div></td>
                </tr>"""
        
        html += """
            </table>
        </div>
        
        <div class="section">
            <h2>📍 Top 10 Villes</h2>
            <table>
                <tr><th>Ville</th><th>Nombre</th><th>Répartition</th></tr>
"""
        
        max_count = max(stats['top_villes'].values()) if stats['top_villes'] else 1
        for ville, count in stats['top_villes'].items():
            if ville:
                pct = (count / max_count) * 100
                html += f"""
                <tr>
                    <td><strong>{ville}</strong></td>
                    <td>{count}</td>
                    <td><div class="bar" style="width:{pct}%"></div></td>
                </tr>"""
        
        html += """
            </table>
        </div>
        
        <div class="section">
            <h2>📋 Dernières annonces</h2>
            <table>
                <tr><th>Marque</th><th>Modèle</th><th>Prix</th><th>Année</th><th>KM</th><th>Ville</th></tr>
"""
        
        for _, row in df.head(20).iterrows():
            prix = f"{int(row['prix']):,}€" if pd.notna(row['prix']) else "N/A"
            km = f"{int(row['km']):,}" if pd.notna(row['km']) else "N/A"
            html += f"""
                <tr>
                    <td><strong>{row['marque'] or 'N/A'}</strong></td>
                    <td>{row['modele'] or 'N/A'}</td>
                    <td>{prix}</td>
                    <td>{row['annee'] or 'N/A'}</td>
                    <td>{km}</td>
                    <td>{row['ville'] or 'N/A'}</td>
                </tr>"""
        
        html += """
            </table>
        </div>
        
        <p style="text-align:center;color:#999;margin-top:40px;">
            Pipeline LeBonCoin v2.0 - Anti-détection activée
        </p>
    </div>
</body>
</html>
"""
        
        with open(REPORT_PATH, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"[OK] Rapport généré: {REPORT_PATH}")
        return True
        
    except Exception as e:
        logger.error(f"[FAIL] Erreur rapport: {e}")
        return False

# ============================================================================
# MAIN PIPELINE
# ============================================================================

def run_pipeline(max_pages=1, max_annonces=50):
    """Exécute le pipeline complet"""
    logger.info("=" * 60)
    logger.info("🚀 DÉMARRAGE DU PIPELINE")
    logger.info(f"   Pages: {max_pages} | Max annonces: {max_annonces}")
    logger.info("=" * 60)
    
    start_time = time.time()
    results = {}
    
    # Task 1: Scraping
    results['scrape'] = task_scrape(max_pages, max_annonces)
    
    if results['scrape']:
        # Task 2: Validation
        results['validate'] = task_validate()
        
        # Task 3: Transformations
        results['transform'] = task_transform()
        
        # Task 4: Rapport
        results['report'] = task_report()
    
    elapsed = time.time() - start_time
    
    logger.info("=" * 60)
    logger.info("📊 RÉSUMÉ DU PIPELINE")
    logger.info("=" * 60)
    for task, success in results.items():
        status = "✅" if success else "❌"
        logger.info(f"   {status} {task}")
    logger.info(f"   ⏱️ Durée totale: {elapsed:.1f}s")
    logger.info("=" * 60)
    
    return all(results.values())

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Arguments
    max_pages = 1
    max_annonces = 20
    
    for i, arg in enumerate(sys.argv):
        if arg == '--pages' and i+1 < len(sys.argv):
            max_pages = int(sys.argv[i+1])
        elif arg == '--max' and i+1 < len(sys.argv):
            max_annonces = int(sys.argv[i+1])
    
    success = run_pipeline(max_pages, max_annonces)
    sys.exit(0 if success else 1)
