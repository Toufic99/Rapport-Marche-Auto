"""Générateur de rapport HTML simple - Un seul tableau avec pagination"""
import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path

conn = sqlite3.connect('data/vehicles.db')
df = pd.read_sql_query('SELECT * FROM vehicles', conn)
conn.close()

print(f'Véhicules en base: {len(df)}')

# HTML - Un seul tableau avec pagination et liens
html = f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Car Analytics - {len(df)} véhicules</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; margin: 20px; background: #f0f4f8; }}
        .container {{ max-width: 1500px; margin: 0 auto; }}
        h1 {{ color: #2563eb; text-align: center; margin-bottom: 5px; }}
        .subtitle {{ text-align: center; color: #666; margin-bottom: 20px; }}
        .controls {{ text-align: center; margin: 20px 0; }}
        .controls button {{ background: #2563eb; color: white; border: none; padding: 10px 20px; margin: 0 5px; border-radius: 5px; cursor: pointer; font-size: 14px; }}
        .controls button:hover {{ background: #1d4ed8; }}
        .controls button:disabled {{ background: #ccc; cursor: not-allowed; }}
        .controls span {{ margin: 0 15px; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; background: white; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        th {{ background: #2563eb; color: white; padding: 12px 8px; text-align: left; position: sticky; top: 0; }}
        td {{ padding: 10px 8px; border-bottom: 1px solid #eee; }}
        tr:hover {{ background: #eff6ff; }}
        tr:nth-child(even) {{ background: #fafafa; }}
        tr:nth-child(even):hover {{ background: #eff6ff; }}
        .prix {{ font-weight: bold; color: #2563eb; }}
        .km {{ color: #666; }}
        .link-btn {{ background: #2563eb; color: white; padding: 5px 10px; border-radius: 3px; text-decoration: none; font-size: 12px; }}
        .link-btn:hover {{ background: #1d4ed8; }}
        .hidden {{ display: none; }}
    </style>
</head>
<body>
<div class="container">
    <h1>🚗 Car Analytics - Rapport Marché Automobile</h1>
    <p class="subtitle">{len(df)} véhicules | Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
    
    <div class="controls">
        <button onclick="prevPage()">◀ Précédent</button>
        <span id="pageInfo">Page 1 / ?</span>
        <button onclick="nextPage()">Suivant ▶</button>
        <select id="perPage" onchange="changePerPage()" style="margin-left: 20px; padding: 8px;">
            <option value="10">10 par page</option>
            <option value="20" selected>20 par page</option>
            <option value="50">50 par page</option>
            <option value="100">Tous</option>
        </select>
    </div>
    
    <table>
        <thead>
            <tr>
                <th>Marque</th>
                <th>Modèle</th>
                <th>Année</th>
                <th>Kilométrage</th>
                <th>Prix</th>
                <th>Énergie</th>
                <th>Boîte</th>
                <th>Ville</th>
                <th>Dept</th>
                <th>Annonce</th>
            </tr>
        </thead>
        <tbody id="tableBody">
'''

for idx, row in df.iterrows():
    marque = row['marque'] if pd.notna(row['marque']) else '-'
    modele = row['modele'] if pd.notna(row['modele']) else '-'
    annee = int(row['annee']) if pd.notna(row['annee']) else '-'
    km = f"{int(row['km']):,} km" if pd.notna(row['km']) else '-'
    prix = f"{int(row['prix']):,} €" if pd.notna(row['prix']) else '-'
    energie = row['energie'] if pd.notna(row['energie']) else '-'
    boite = row['boite_vitesse'] if pd.notna(row['boite_vitesse']) else '-'
    ville = row['ville'] if pd.notna(row['ville']) else '-'
    dept = row['departement'] if pd.notna(row['departement']) else '-'
    lien = row['lien'] if pd.notna(row['lien']) else '#'
    
    html += f'''<tr class="data-row">
            <td>{marque}</td>
            <td>{modele}</td>
            <td>{annee}</td>
            <td class="km">{km}</td>
            <td class="prix">{prix}</td>
            <td>{energie}</td>
            <td>{boite}</td>
            <td>{ville}</td>
            <td>{dept}</td>
            <td><a href="{lien}" target="_blank" class="link-btn">Voir</a></td>
        </tr>'''

html += '''
        </tbody>
    </table>
</div>

<script>
let currentPage = 1;
let perPage = 20;
const rows = document.querySelectorAll('.data-row');
const totalRows = rows.length;

function showPage(page) {
    const start = (page - 1) * perPage;
    const end = start + perPage;
    
    rows.forEach((row, index) => {
        if (index >= start && index < end) {
            row.classList.remove('hidden');
        } else {
            row.classList.add('hidden');
        }
    });
    
    const totalPages = Math.ceil(totalRows / perPage);
    document.getElementById('pageInfo').textContent = `Page ${page} / ${totalPages}`;
}

function nextPage() {
    const totalPages = Math.ceil(totalRows / perPage);
    if (currentPage < totalPages) {
        currentPage++;
        showPage(currentPage);
    }
}

function prevPage() {
    if (currentPage > 1) {
        currentPage--;
        showPage(currentPage);
    }
}

function changePerPage() {
    perPage = parseInt(document.getElementById('perPage').value);
    if (perPage === 100) perPage = totalRows; // "Tous"
    currentPage = 1;
    showPage(currentPage);
}

// Initialisation
showPage(1);
</script>
</body>
</html>'''

Path('leboncoin_rapport.html').write_text(html, encoding='utf-8')
print('[OK] Rapport régénéré avec', len(df), 'véhicules!')
