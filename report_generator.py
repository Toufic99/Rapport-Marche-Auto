import sqlite3
from datetime import datetime
import json


class ReportGenerator:
    """Génère un rapport HTML visuel amélioré"""
    
    def __init__(self, db_name='data/leboncoin.db'):
        self.db_name = db_name
    
    def get_statistics(self):
        """Récupère les statistiques globales"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Nombre de voitures actives
        cursor.execute('SELECT COUNT(*) FROM vehicles WHERE statut = "ACTIVE"')
        actives = cursor.fetchone()[0]
        
        # Nombre de voitures vendues
        cursor.execute('SELECT COUNT(*) FROM vehicles WHERE statut = "VENDUE"')
        vendues = cursor.fetchone()[0]
        
        # Total
        cursor.execute('SELECT COUNT(*) FROM vehicles')
        total = cursor.fetchone()[0]
        
        # Prix moyen (nettoyer les prix)
        cursor.execute('SELECT prix_current FROM vehicles WHERE prix_current IS NOT NULL')
        prices = cursor.fetchall()
        prix_values = []
        for p in prices:
            try:
                # Nettoyer le prix - enlever tous les caractères non-numériques sauf le point
                prix_str = str(p[0])
                # Remplacer les espaces spéciaux par rien
                prix_str = prix_str.replace('\u202f', '').replace('\xa0', '').replace(' ', '')
                # Enlever le symbole euro et tout ce qui suit
                prix_str = prix_str.replace('€', '')
                # Garder seulement les chiffres
                prix_clean = ''.join(c for c in prix_str if c.isdigit())
                if prix_clean and len(prix_clean) <= 7:  # Max 9,999,999 EUR (raisonnable pour une voiture)
                    prix_val = float(prix_clean)
                    # Filtrer les prix aberrants
                    if 100 <= prix_val <= 500000:  # Entre 100€ et 500,000€
                        prix_values.append(prix_val)
            except:
                pass
        
        prix_moyen = sum(prix_values) / len(prix_values) if prix_values else 0
        prix_min = min(prix_values) if prix_values else 0
        prix_max = max(prix_values) if prix_values else 0
        
        # Temps moyen de vente
        cursor.execute('''
            SELECT AVG(julianday(date_vendu) - julianday(date_first_seen))
            FROM vehicles 
            WHERE statut = "VENDUE" AND date_vendu IS NOT NULL
        ''')
        temps_moyen = cursor.fetchone()[0]
        
        # Marques les plus populaires
        cursor.execute('''
            SELECT marque, COUNT(*) as count 
            FROM vehicles 
            GROUP BY marque 
            ORDER BY count DESC 
            LIMIT 10
        ''')
        top_marques = cursor.fetchall()
        
        conn.close()
        return {
            'actives': actives,
            'vendues': vendues,
            'total': total,
            'prix_moyen': prix_moyen,
            'prix_min': prix_min,
            'prix_max': prix_max,
            'temps_moyen': temps_moyen,
            'top_marques': top_marques
        }
    
    def get_vehicles(self):
        """Récupère toutes les voitures"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM vehicles 
            ORDER BY id DESC
        ''')
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def generate_html(self):
        """Génère un rapport HTML amélioré"""
        stats = self.get_statistics()
        vehicles = self.get_vehicles()
        
        # Préparer les données pour le graphique
        marques_labels = [m[0] for m in stats['top_marques']]
        marques_values = [m[1] for m in stats['top_marques']]
        
        html = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport LeBonCoin - Marche Automobile</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }}
        
        .container {{
            max-width: 1600px;
            margin: 0 auto;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(102, 126, 234, 0.4);
        }}
        
        header h1 {{
            font-size: 2.8em;
            margin-bottom: 10px;
        }}
        
        header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-card h3 {{
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}
        
        .stat-card .number {{
            font-size: 2.5em;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .charts-section {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .chart-card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }}
        
        .chart-card h3 {{
            margin-bottom: 20px;
            color: #333;
        }}
        
        .vehicles-section {{
            background: white;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .vehicles-header {{
            padding: 25px;
            background: #f8f9fa;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
        }}
        
        .vehicles-header h2 {{
            color: #333;
        }}
        
        .search-box {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        
        .search-box input, .search-box select {{
            padding: 10px 15px;
            border: 2px solid #eee;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }}
        
        .search-box input:focus, .search-box select:focus {{
            outline: none;
            border-color: #667eea;
        }}
        
        .search-box input {{
            width: 250px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            position: sticky;
            top: 0;
        }}
        
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .status-active {{
            background: #d4edda;
            color: #155724;
            padding: 5px 12px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.85em;
        }}
        
        .status-vendue {{
            background: #f8d7da;
            color: #721c24;
            padding: 5px 12px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.85em;
        }}
        
        .status-null {{
            background: #e2e3e5;
            color: #383d41;
            padding: 5px 12px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.85em;
        }}
        
        .btn-voir {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.85em;
            display: inline-block;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .btn-voir:hover {{
            transform: scale(1.05);
            box-shadow: 0 3px 10px rgba(102, 126, 234, 0.4);
        }}
        
        .btn-disabled {{
            background: #6c757d;
            color: #ccc;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.85em;
            display: inline-block;
            cursor: not-allowed;
        }}
        
        .footer {{
            text-align: center;
            padding: 30px;
            color: rgba(255,255,255,0.7);
            margin-top: 30px;
        }}
        
        .table-container {{
            max-height: 600px;
            overflow-y: auto;
        }}
        
        .prix {{
            font-weight: 600;
            color: #28a745;
        }}
        
        .titre-cell {{
            max-width: 300px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        
        #vehicleCount {{
            background: #667eea;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Rapport Marche Automobile</h1>
            <p>Mis a jour le {datetime.now().strftime('%d/%m/%Y a %H:%M:%S')} | {stats['total']} vehicules analyses</p>
        </header>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Vehicules</h3>
                <div class="number">{stats['total']}</div>
            </div>
            <div class="stat-card">
                <h3>En Vente</h3>
                <div class="number">{stats['actives']}</div>
            </div>
            <div class="stat-card">
                <h3>Vendues</h3>
                <div class="number">{stats['vendues']}</div>
            </div>
            <div class="stat-card">
                <h3>Prix Moyen</h3>
                <div class="number">{stats['prix_moyen']:,.0f} EUR</div>
            </div>
            <div class="stat-card">
                <h3>Prix Min</h3>
                <div class="number">{stats['prix_min']:,.0f} EUR</div>
            </div>
            <div class="stat-card">
                <h3>Prix Max</h3>
                <div class="number">{stats['prix_max']:,.0f} EUR</div>
            </div>
        </div>
        
        <div class="charts-section">
            <div class="chart-card">
                <h3>Top 10 Marques</h3>
                <canvas id="brandChart"></canvas>
            </div>
            <div class="chart-card">
                <h3>Repartition par Statut</h3>
                <canvas id="statusChart"></canvas>
            </div>
        </div>
        
        <div class="vehicles-section">
            <div class="vehicles-header">
                <h2>Liste des Vehicules <span id="vehicleCount">{len(vehicles)}</span></h2>
                <div class="search-box">
                    <input type="text" id="searchInput" placeholder="Rechercher (marque, modele, titre...)">
                    <select id="statusFilter">
                        <option value="">Tous les statuts</option>
                        <option value="ACTIVE">En vente</option>
                        <option value="VENDUE">Vendues</option>
                    </select>
                    <select id="marqueFilter">
                        <option value="">Toutes les marques</option>
"""
        
        # Ajouter les marques au filtre
        marques_uniques = sorted(set(v['marque'] for v in vehicles if v['marque']))
        for marque in marques_uniques[:50]:  # Limiter à 50 marques
            html += f'                        <option value="{marque}">{marque}</option>\n'
        
        html += """
                    </select>
                </div>
            </div>
            
            <div class="table-container">
                <table id="vehiclesTable">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Titre</th>
                            <th>Marque</th>
                            <th>Annee</th>
                            <th>KM</th>
                            <th>Prix</th>
                            <th>Ville</th>
                            <th>Vendeur</th>
                            <th>Energie</th>
                            <th>Statut</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        
        for vehicle in vehicles:
            statut = vehicle.get('statut') or 'N/A'
            if statut == 'ACTIVE':
                statut_class = 'status-active'
            elif statut == 'VENDUE':
                statut_class = 'status-vendue'
            else:
                statut_class = 'status-null'
            
            titre = (vehicle.get('titre') or 'N/A')[:50]
            marque = vehicle.get('marque') or 'N/A'
            annee = vehicle.get('annee') or '-'
            km = vehicle.get('km') or '-'
            prix = vehicle.get('prix_current') or vehicle.get('prix_initial') or 'N/A'
            
            # Utiliser la colonne ville
            ville = vehicle.get('ville') or '-'
            
            type_vendeur = vehicle.get('type_vendeur') or '-'
            energie = vehicle.get('energie') or '-'
            lien = vehicle.get('lien') or ''
            
            # Vérifier si le lien est valide
            lien_valide = lien and lien.startswith('http') and '/ad/' in lien
            if lien_valide:
                btn_html = f'<a href="{lien}" target="_blank" class="btn-voir">Voir</a>'
            else:
                btn_html = '<span class="btn-disabled">N/A</span>'
            
            # Classe pour type vendeur
            vendeur_class = 'status-active' if type_vendeur == 'Particulier' else ('status-vendue' if type_vendeur == 'Pro' or type_vendeur == 'Professionnel' else 'status-null')
            
            html += f"""
                        <tr data-marque="{marque}" data-statut="{statut}" data-ville="{ville}">
                            <td><strong>#{vehicle['id']}</strong></td>
                            <td class="titre-cell" title="{titre}">{titre}</td>
                            <td>{marque}</td>
                            <td>{annee}</td>
                            <td>{km}</td>
                            <td class="prix">{prix}</td>
                            <td>{ville}</td>
                            <td><span class="{vendeur_class}">{type_vendeur}</span></td>
                            <td>{energie}</td>
                            <td><span class="{statut_class}">{statut}</span></td>
                            <td>{btn_html}</td>
                        </tr>
"""
        
        html += f"""
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="footer">
            <p>Genere par LeBonCoin Scraper | Base de donnees: {self.db_name}</p>
            <p>Data Engineering Pipeline - Rapport Automatise</p>
        </div>
    </div>
    
    <script>
        // Graphique des marques
        const brandCtx = document.getElementById('brandChart').getContext('2d');
        new Chart(brandCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(marques_labels)},
                datasets: [{{
                    label: 'Nombre de vehicules',
                    data: {json.dumps(marques_values)},
                    backgroundColor: [
                        '#667eea', '#764ba2', '#f093fb', '#f5576c',
                        '#4facfe', '#00f2fe', '#43e97b', '#38f9d7',
                        '#fa709a', '#fee140'
                    ],
                    borderRadius: 5
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    y: {{ beginAtZero: true }}
                }}
            }}
        }});
        
        // Graphique des statuts
        const statusCtx = document.getElementById('statusChart').getContext('2d');
        new Chart(statusCtx, {{
            type: 'doughnut',
            data: {{
                labels: ['En vente', 'Vendues', 'Autre'],
                datasets: [{{
                    data: [{stats['actives']}, {stats['vendues']}, {stats['total'] - stats['actives'] - stats['vendues']}],
                    backgroundColor: ['#43e97b', '#f5576c', '#e2e3e5'],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ position: 'bottom' }}
                }}
            }}
        }});
        
        // Filtrage du tableau
        const searchInput = document.getElementById('searchInput');
        const statusFilter = document.getElementById('statusFilter');
        const marqueFilter = document.getElementById('marqueFilter');
        const table = document.getElementById('vehiclesTable');
        const vehicleCount = document.getElementById('vehicleCount');
        
        function filterTable() {{
            const searchTerm = searchInput.value.toLowerCase();
            const statusValue = statusFilter.value;
            const marqueValue = marqueFilter.value;
            const rows = table.querySelectorAll('tbody tr');
            let visibleCount = 0;
            
            rows.forEach(row => {{
                const text = row.textContent.toLowerCase();
                const rowStatus = row.dataset.statut;
                const rowMarque = row.dataset.marque;
                
                const matchesSearch = text.includes(searchTerm);
                const matchesStatus = !statusValue || rowStatus === statusValue;
                const matchesMarque = !marqueValue || rowMarque === marqueValue;
                
                if (matchesSearch && matchesStatus && matchesMarque) {{
                    row.style.display = '';
                    visibleCount++;
                }} else {{
                    row.style.display = 'none';
                }}
            }});
            
            vehicleCount.textContent = visibleCount;
        }}
        
        searchInput.addEventListener('input', filterTable);
        statusFilter.addEventListener('change', filterTable);
        marqueFilter.addEventListener('change', filterTable);
    </script>
</body>
</html>
"""
        
        filename = 'leboncoin_rapport.html'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print("[REPORT] Rapport HTML genere: " + filename)
        return filename


if __name__ == '__main__':
    generator = ReportGenerator()
    generator.generate_html()
