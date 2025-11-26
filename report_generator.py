import sqlite3
from datetime import datetime
import csv


class ReportGenerator:
    """Génère rapports HTML et CSV améliorés"""
    
    def __init__(self, db_name='leboncoin_vehicles.db'):
        self.db_name = db_name
    
    def get_seller_status(self, vehicle_row):
        """Détermine si le vendeur est nouveau ou pas"""
        try:
            # Chercher le nombre d'annonces de ce vendeur
            seller_name = vehicle_row.get('seller_name', 'Particulier')
            
            if not seller_name or seller_name == 'Particulier':
                return '👤 Particulier'
            
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM vehicles WHERE seller_name = ?", (seller_name,))
            count = cursor.fetchone()[0]
            conn.close()
            
            if count <= 2:
                return '🆕 Nouveau Vendeur'
            elif count <= 5:
                return '📈 Vendeur Actif'
            else:
                return '🏢 Vendeur Établi'
        except:
            return '👤 Particulier'
    
    def get_vehicles(self):
        """Récupère toutes les voitures"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM vehicles 
            ORDER BY date_annonce DESC
        ''')
        data = cursor.fetchall()
        conn.close()
        return data
    
    def get_stats(self):
        """Calcule les statistiques"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM vehicles')
        total = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM vehicles WHERE statut = "ACTIVE"')
        actives = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM vehicles WHERE statut = "VENDUE"')
        vendues = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM vehicles WHERE priorite = 1')
        poitiers = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(prix_current) FROM vehicles WHERE prix_current IS NOT NULL AND prix_current != "N/A" AND CAST(prix_current AS FLOAT) >= 400')
        prix_moyen = float(cursor.fetchone()[0] or 0)
        
        cursor.execute('SELECT MIN(CAST(prix_current AS FLOAT)) FROM vehicles WHERE prix_current IS NOT NULL AND prix_current != "N/A" AND CAST(prix_current AS FLOAT) >= 400')
        prix_min = float(cursor.fetchone()[0] or 0)
        
        cursor.execute('SELECT MAX(CAST(prix_current AS FLOAT)) FROM vehicles WHERE prix_current IS NOT NULL AND prix_current != "N/A" AND CAST(prix_current AS FLOAT) >= 400')
        prix_max = float(cursor.fetchone()[0] or 0)
        
        conn.close()
        
        return {
            'total': total,
            'actives': actives,
            'vendues': vendues,
            'poitiers': poitiers,
            'prix_moyen': prix_moyen,
            'prix_min': prix_min,
            'prix_max': prix_max
        }
    
    def get_energy_stats(self):
        """Récupère les statistiques par type d'énergie"""
        conn = sqlite3.connect(self.db_name)
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
                WHERE total_count > 0
                ORDER BY total_count DESC
            """)
            
            energy_data = cursor.fetchall()
            conn.close()
            return energy_data
        except Exception as e:
            print(f"[ERROR] Getting energy stats: {e}")
            conn.close()
            return []
    
    def generate_csv(self):
        """Génère le CSV"""
        data = self.get_vehicles()
        
        with open('leboncoin_rapport_complet.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'ID', 'Titre', 'Marque', 'Modele', 'Annee', 'KM',
                'Energie', 'Boite Vitesse',
                'Prix Initial', 'Prix Actuel', 'Date Annonce', 'Date Lancement',
                'Statut', 'Ville', 'Priorite', 'Lien'
            ])
            
            for row in data:
                try:
                    energie = row['energie'] if row['energie'] else 'N/A'
                except (IndexError, TypeError, KeyError):
                    energie = 'N/A'
                
                try:
                    boite_vitesse = row['boite_vitesse'] if row['boite_vitesse'] else 'N/A'
                except (IndexError, TypeError, KeyError):
                    boite_vitesse = 'N/A'
                
                writer.writerow([
                    row['id'],
                    row['titre'],
                    row['marque'],
                    row['modele'],
                    row['annee'] if row['annee'] else 'N/A',
                    f"{row['km']} km" if row['km'] else 'N/A',
                    energie,
                    boite_vitesse,
                    row['prix_initial'],
                    row['prix_current'],
                    row['date_annonce'],
                    row['date_annonce'],
                    row['statut'],
                    row['ville'],
                    'POITIERS' if row['priorite'] == 1 else 'Autre',
                    row['lien']
                ])
        
        return 'leboncoin_rapport_complet.csv'
    
    def generate_html(self):
        """Génère le rapport HTML amélioré"""
        data = self.get_vehicles()
        stats = self.get_stats()
        
        html = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport Marché Auto - Analyse Complète</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }}
        
        .container {{
            max-width: 1600px;
            margin: 0 auto;
        }}
        
        header {{
            text-align: center;
            color: white;
            margin-bottom: 40px;
            animation: fadeIn 0.5s ease-in;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        
        header h1 {{
            font-size: 3.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
            font-weight: 700;
        }}
        
        header p {{
            font-size: 1.1em;
            opacity: 0.95;
            letter-spacing: 0.5px;
        }}
        
        .update-time {{
            background: rgba(255,255,255,0.1);
            padding: 10px 20px;
            border-radius: 20px;
            display: inline-block;
            margin-top: 15px;
            font-size: 0.9em;
            backdrop-filter: blur(10px);
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0,0,0,0.15);
        }}
        
        .stat-card h3 {{
            color: #666;
            font-size: 0.8em;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
        }}
        
        .stat-card .value {{
            font-size: 2.5em;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .stat-card.highlight {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }}
        
        .stat-card.highlight h3,
        .stat-card.highlight .value {{
            color: white;
            -webkit-text-fill-color: white;
            background: none;
        }}
        
        .legend {{
            background: rgba(255,255,255,0.1);
            color: white;
            padding: 15px 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
            font-size: 0.9em;
        }}
        
        .table-header {{
            color: white;
            margin-bottom: 20px;
            font-size: 1.8em;
            font-weight: 700;
        }}
        
        .table-container {{
            background: white;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            overflow: hidden;
            margin-bottom: 40px;
        }}
        
        .table-wrapper {{
            /* Affiche environ 10 lignes puis scroll */
            max-height: 480px;
            overflow-y: auto;
            border-top: 1px solid #ddd;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 18px 15px;
            text-align: left;
            font-weight: 600;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            white-space: nowrap;
        }}
        
        td {{
            padding: 14px 15px;
            border-bottom: 1px solid #eee;
            font-size: 0.93em;
        }}
        
        tr:hover {{
            background: #f9f9f9;
        }}
        
        .id {{
            font-weight: 700;
            color: #667eea;
            min-width: 50px;
        }}
        
        .titre {{
            font-weight: 500;
            color: #333;
            max-width: 300px;
        }}
        
        .price {{
            color: #27ae60;
            font-weight: 700;
            font-size: 1.05em;
        }}
        
        .date {{
            color: #3498db;
            font-size: 0.9em;
        }}
        
        .ville {{
            background: #e8f4f8;
            padding: 6px 10px;
            border-radius: 6px;
            font-size: 0.85em;
            color: #0277bd;
            font-weight: 500;
            display: inline-block;
        }}
        
        .ville.poitiers {{
            background: #fff3cd;
            color: #856404;
            font-weight: 700;
        }}
        
        .status {{
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 0.85em;
            font-weight: 600;
            text-align: center;
            display: inline-block;
        }}
        
        .status.active {{
            background: #d4edda;
            color: #155724;
        }}
        
        .status.sold {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .priorite {{
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 700;
            text-align: center;
            display: inline-block;
        }}
        
        .priorite.poitiers {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }}
        
        .priorite.autre {{
            background: #f0f0f0;
            color: #666;
        }}
        
        .voir-btn {{
            display: inline-block;
            padding: 10px 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 8px;
            text-decoration: none;
            font-size: 0.85em;
            font-weight: 700;
            transition: all 0.3s ease;
            text-align: center;
            white-space: nowrap;
        }}
        
        .voir-btn:hover {{
            transform: scale(1.05);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }}
        
        footer {{
            text-align: center;
            color: white;
            margin-top: 40px;
            padding: 30px;
            opacity: 0.9;
            border-top: 1px solid rgba(255,255,255,0.2);
        }}
        
        footer p {{
            margin: 8px 0;
            font-size: 0.95em;
        }}
        
        @media (max-width: 768px) {{
            table {{
                font-size: 0.8em;
            }}
            
            th, td {{
                padding: 10px 8px;
            }}
            
            .titre {{
                max-width: 150px;
            }}
        }}
        
        .filters-container {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }}
        
        .filter-group {{
            display: flex;
            flex-direction: column;
        }}
        
        .filter-group label {{
            font-weight: 600;
            margin-bottom: 8px;
            color: #333;
            font-size: 0.9em;
        }}
        
        .filter-group input,
        .filter-group select {{
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
            transition: all 0.3s ease;
            font-family: inherit;
        }}
        
        .filter-group input:focus,
        .filter-group select:focus {{
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }}
        
        .filter-buttons {{
            display: flex;
            gap: 10px;
            align-items: flex-end;
        }}
        
        .btn-filter, .btn-reset {{
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.9em;
        }}
        
        .btn-filter {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            flex: 1;
        }}
        
        .btn-filter:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
        }}
        
        .btn-reset {{
            background: #f0f0f0;
            color: #333;
        }}
        
        .btn-reset:hover {{
            background: #e0e0e0;
        }}
        
        #searchResults {{
            background: rgba(255,255,255,0.1);
            color: white;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 0.9em;
        }}
        
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚗 Rapport Marché Auto</h1>
            <p>Analyse Automatique - France Entière</p>
            <div class="update-time">
                Rapport actualisé le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}
            </div>
        </header>
        
        <div class="stats">
            <div class="stat-card">
                <h3>Total</h3>
                <div class="value">{stats['total']}</div>
            </div>
            <div class="stat-card">
                <h3>Actives</h3>
                <div class="value">{stats['actives']}</div>
            </div>
            <div class="stat-card">
                <h3>Vendues</h3>
                <div class="value">{stats['vendues']}</div>
            </div>
            <div class="stat-card">
                <h3>Prix Moyen</h3>
                <div class="value">{stats['prix_moyen']:,.0f}€</div>
            </div>
            <div class="stat-card">
                <h3>Min → Max</h3>
                <div class="value" style="font-size: 1.4em;">{stats['prix_min']:,.0f}€ → {stats['prix_max']:,.0f}€</div>
            </div>
        </div>
        
        <div class="legend">
            <strong>Légende :</strong> 
            <span style="background: #d4edda; padding: 0 5px; border-radius: 3px;">✓ ACTIVE</span> = En vente | 
            <span style="background: #f8d7da; padding: 0 5px; border-radius: 3px;">✗ VENDUE</span> = Disparue
        </div>
        
        <div class="table-header">Statistiques par Type d'Énergie</div>
        
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Type d'Énergie</th>
                        <th>Nombre de Véhicules</th>
                        <th>Prix Moyen</th>
                        <th>Kilométrage Moyen</th>
                    </tr>
                </thead>
                <tbody>
"""

        energy_stats = self.get_energy_stats()
        for energie, count, avg_price, avg_km, avg_days in energy_stats:
            if count > 0:
                avg_price_fmt = f"{avg_price:,.0f}€" if avg_price else "N/A"
                avg_km_fmt = f"{avg_km:,.0f} km" if avg_km else "N/A"
                
                html += f"""
                    <tr>
                        <td><strong>{energie}</strong></td>
                        <td>{count}</td>
                        <td>{avg_price_fmt}</td>
                        <td>{avg_km_fmt}</td>
                    </tr>
"""
        
        html += """
                </tbody>
            </table>
        </div>
        
        <div class="filters-container">
            <div class="filter-group">
                <label for="searchInput">Rechercher</label>
                <input type="text" id="searchInput" placeholder="Titre, marque, ville...">
            </div>
            <div class="filter-group">
                <label for="sortBy">Trier par</label>
                <select id="sortBy">
                    <option value="date-desc">Date (Plus récent)</option>
                    <option value="date-asc">Date (Plus ancien)</option>
                    <option value="price-asc">Prix (Moins cher)</option>
                    <option value="price-desc">Prix (Plus cher)</option>
                    <option value="km-asc">Kilométrage (Moins)</option>
                    <option value="km-desc">Kilométrage (Plus)</option>
                    <option value="ville-asc">Ville (A→Z)</option>
                    <option value="status-asc">Statut</option>
                </select>
            </div>
            <div class="filter-group">
                <label for="filterStatus">Statut</label>
                <select id="filterStatus">
                    <option value="">Tous</option>
                    <option value="ACTIVE">En vente (ACTIVE)</option>
                    <option value="VENDUE">Vendue (VENDUE)</option>
                </select>
            </div>
            <div class="filter-group">
                <label for="filterEnergy">Énergie</label>
                <select id="filterEnergy">
                    <option value="">Tous</option>
                    <option value="Essence">Essence</option>
                    <option value="Diesel">Diesel</option>
                    <option value="Électrique">Électrique</option>
                    <option value="Hybride">Hybride</option>
                </select>
            </div>
            <div class="filter-group">
                <label for="filterYear">Année Min</label>
                <input type="number" id="filterYear" placeholder="Ex: 2015" min="1900" max="2025">
            </div>
            <div class="filter-group">
                <label for="filterBoite">Boîte de Vitesse</label>
                <select id="filterBoite">
                    <option value="">Tous</option>
                    <option value="Manuelle">Manuelle</option>
                    <option value="Automatique">Automatique</option>
                    <option value="CVT">CVT</option>
                </select>
            </div>
            <div class="filter-group">
                <label for="filterPriceMin">Prix Min (€)</label>
                <input type="number" id="filterPriceMin" placeholder="Ex: 5000" min="0">
            </div>
            <div class="filter-group">
                <label for="filterPriceMax">Prix Max (€)</label>
                <input type="number" id="filterPriceMax" placeholder="Ex: 30000" min="0">
            </div>
            <div class="filter-group">
                <label for="filterVendor">Type Vendeur</label>
                <select id="filterVendor">
                    <option value="">Tous</option>
                    <option value="Particulier">Particulier</option>
                    <option value="Nouveau">Nouveau Vendeur</option>
                    <option value="Actif">Vendeur Actif</option>
                    <option value="Établi">Vendeur Établi</option>
                </select>
            </div>
            <div class="filter-buttons">
                <button class="btn-filter" onclick="filterTable()">Appliquer</button>
                <button class="btn-reset" onclick="resetFilters()">Réinitialiser</button>
            </div>
        </div>
        
        <div id="searchResults" style="display: none;"></div>
        
        <div class="table-header">Liste des Voitures</div>
        
        <div class="table-container">
            <div class="table-wrapper">
            <table id="vehicleTable">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Titre</th>
                        <th>Marque</th>
                        <th>Année</th>
                        <th>Kilométrage</th>
                        <th>Énergie</th>
                        <th>Boîte</th>
                        <th>Ville</th>
                        <th>Prix</th>
                        <th>Date Mise en Ligne</th>
                        <th>Statut</th>
                        <th>Vendeur</th>
                        <th>Profil Vendeur</th>
                        <th>Annonces Vendeur</th>
                        <th>Priorité</th>
                        <th>Lien</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for row in data:
            ville_class = 'poitiers' if row['priorite'] == 1 else ''
            priorite_class = 'poitiers' if row['priorite'] == 1 else 'autre'
            priorite_text = '⭐ POITIERS' if row['priorite'] == 1 else 'Autre'
            status_class = 'active' if row['statut'] == 'ACTIVE' else 'sold'
            status_text = '✓ ACTIVE' if row['statut'] == 'ACTIVE' else '✗ VENDUE'
            lien_display = f'<a href="{row["lien"]}" target="_blank" class="voir-btn">Voir →</a>' if row['lien'] != 'N/A' else '—'
            
            # Convertir le prix en float pour le formater
            try:
                prix = float(row['prix_current'])
                prix_text = f'{prix:,.0f}€'
            except (ValueError, TypeError):
                prix_text = str(row['prix_current'])
            
            # Formater les données
            annee = row['annee'] if row['annee'] else 'N/A'
            km = f"{row['km']:,} km" if row['km'] else 'N/A'
            
            try:
                energie = row['energie'] if row['energie'] else 'N/A'
            except (IndexError, TypeError, KeyError):
                energie = 'N/A'
            
            try:
                boite_vitesse = row['boite_vitesse'] if row['boite_vitesse'] else 'N/A'
            except (IndexError, TypeError, KeyError):
                boite_vitesse = 'N/A'
            
            # Formater jours_en_vente
            try:
                jours_vente = row['jours_en_vente'] if row['jours_en_vente'] else 0
                jours_text = f"{jours_vente} j" if jours_vente else "—"
            except (IndexError, TypeError, KeyError):
                jours_text = "—"
            
            # Formater vendeur
            try:
                seller_name = row['seller_name'] if row['seller_name'] else 'Particulier'
            except (IndexError, TypeError, KeyError):
                seller_name = 'Particulier'
            
            # Déterminer profil du vendeur (nouveau, actif, établi)
            profil_vendeur = self.get_seller_status(row)
            
            # Nombre d'annonces du vendeur
            try:
                nb_annonces = row['nb_annonces_vendeur'] if row['nb_annonces_vendeur'] else 1
                nb_text = f"{nb_annonces}"
            except (IndexError, TypeError, KeyError):
                nb_text = "1"
            
            html += f"""
                <tr>
                    <td class="id">#{row['id']}</td>
                    <td class="titre">{row['titre']}</td>
                    <td>{row['marque']}</td>
                    <td>{annee}</td>
                    <td>{km}</td>
                    <td><strong>{energie}</strong></td>
                    <td>{boite_vitesse}</td>
                    <td><span class="ville {ville_class}">{row['ville']}</span></td>
                    <td class="price">{prix_text}</td>
                    <td class="date">{row['date_annonce']}</td>
                    <td><span class="status {status_class}">{status_text}</span></td>
                    <td>{seller_name}</td>
                    <td>{profil_vendeur}</td>
                    <td>{nb_text}</td>
                    <td><span class="priorite {priorite_class}">{priorite_text}</span></td>
                    <td>{lien_display}</td>
                </tr>
"""
        
        html += """
                </tbody>
            </table>
            </div>
        </div>
        
        <footer>
            <p><strong>📊 Système de Scraping Automatique</strong></p>
            <p>Mise à jour automatique: 🌅 08:00 et 🌆 18:00 chaque jour</p>
            <p style="font-size: 0.85em; opacity: 0.8;">Base de données: vehicles.db | Rapport CSV: rapport_complet.csv</p>
        </footer>
    </div>
    
    <script>
        let originalRows = [];
        
        document.addEventListener('DOMContentLoaded', function() {
            const table = document.getElementById('vehicleTable');
            originalRows = Array.from(table.getElementsByTagName('tbody')[0].getElementsByTagName('tr'));
        });
        
        function filterTable() {
            const search = document.getElementById('searchInput').value.toLowerCase();
            const status = document.getElementById('filterStatus').value;
            const energy = document.getElementById('filterEnergy').value;
            const year = parseInt(document.getElementById('filterYear').value) || 0;
            const boite = document.getElementById('filterBoite').value;
            const priceMin = parseFloat(document.getElementById('filterPriceMin').value) || 0;
            const priceMax = parseFloat(document.getElementById('filterPriceMax').value) || Infinity;
            const vendor = document.getElementById('filterVendor').value;
            const sortBy = document.getElementById('sortBy').value;
            const tbody = document.getElementById('vehicleTable').getElementsByTagName('tbody')[0];
            
            let rows = [...originalRows];
            
            // Filtrer par recherche
            if (search) {
                rows = rows.filter(row => {
                    const text = row.textContent.toLowerCase();
                    return text.includes(search);
                });
            }
            
            // Filtrer par statut
            if (status) {
                rows = rows.filter(row => {
                    const statusCell = row.cells[10]; // Colonne Statut (après suppression de "Jours en Vente")
                    return statusCell.textContent.includes(status);
                });
            }
            
            // Filtrer par énergie
            if (energy) {
                rows = rows.filter(row => {
                    const energyCell = row.cells[5]; // Colonne Énergie
                    return energyCell.textContent.includes(energy);
                });
            }
            
            // Filtrer par année
            if (year > 0) {
                rows = rows.filter(row => {
                    const yearCell = parseInt(row.cells[3].textContent);
                    return yearCell >= year;
                });
            }
            
            // Filtrer par boîte
            if (boite) {
                rows = rows.filter(row => {
                    const boiteCell = row.cells[6]; // Colonne Boîte
                    return boiteCell.textContent.includes(boite);
                });
            }
            
            // Filtrer par prix
            rows = rows.filter(row => {
                const priceCell = row.cells[8].textContent.replace('€', '').trim();
                const price = parseFloat(priceCell);
                return price >= priceMin && price <= priceMax;
            });
            
            // Filtrer par vendeur
            if (vendor) {
                rows = rows.filter(row => {
                    const vendorCell = row.cells[12]; // Colonne Profil Vendeur (nouvel index)
                    if (vendor === 'Particulier') {
                        return vendorCell.textContent.includes('Particulier');
                    } else if (vendor === 'Nouveau') {
                        return vendorCell.textContent.includes('Nouveau');
                    } else if (vendor === 'Actif') {
                        return vendorCell.textContent.includes('Actif') && !vendorCell.textContent.includes('Établi');
                    } else if (vendor === 'Établi') {
                        return vendorCell.textContent.includes('Établi');
                    }
                });
            }
            
            // Trier
            rows.sort((a, b) => {
                switch(sortBy) {
                    case 'price-asc':
                        return parseFloat(a.cells[8].textContent) - parseFloat(b.cells[8].textContent);
                    case 'price-desc':
                        return parseFloat(b.cells[8].textContent) - parseFloat(a.cells[8].textContent);
                    case 'km-asc':
                        return parseFloat(a.cells[4].textContent) - parseFloat(b.cells[4].textContent);
                    case 'km-desc':
                        return parseFloat(b.cells[4].textContent) - parseFloat(a.cells[4].textContent);
                    case 'ville-asc':
                        return a.cells[7].textContent.localeCompare(b.cells[7].textContent);
                    case 'status-asc':
                        return a.cells[10].textContent.localeCompare(b.cells[10].textContent);
                    default:
                        return 0;
                }
            });
            
            // Afficher les résultats
            tbody.innerHTML = '';
            rows.forEach(row => tbody.appendChild(row.cloneNode(true)));
            
            const resultDiv = document.getElementById('searchResults');
            resultDiv.style.display = 'block';
            resultDiv.textContent = '✓ ' + rows.length + ' résultat(s) trouvé(s)';
        }
        
        function resetFilters() {
            document.getElementById('searchInput').value = '';
            document.getElementById('filterStatus').value = '';
            document.getElementById('filterEnergy').value = '';
            document.getElementById('filterYear').value = '';
            document.getElementById('filterBoite').value = '';
            document.getElementById('filterPriceMin').value = '';
            document.getElementById('filterPriceMax').value = '';
            document.getElementById('filterVendor').value = '';
            document.getElementById('sortBy').value = 'date-desc';
            document.getElementById('searchResults').style.display = 'none';
            
            const tbody = document.getElementById('vehicleTable').getElementsByTagName('tbody')[0];
            tbody.innerHTML = '';
            originalRows.forEach(row => tbody.appendChild(row.cloneNode(true)));
        }
        
        // Recherche en temps réel
        document.getElementById('searchInput').addEventListener('keyup', filterTable);
    </script>
</body>
</html>
"""
        
        with open('leboncoin_rapport.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        return 'leboncoin_rapport.html'


if __name__ == '__main__':
    gen = ReportGenerator()
    csv_file = gen.generate_csv()
    html_file = gen.generate_html()
    print(f"[REPORT] CSV: {csv_file}")
    print(f"[REPORT] HTML: {html_file}")
