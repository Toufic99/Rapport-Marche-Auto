"""
API FastAPI pour LeBonCoin Scraper
==================================
Endpoints disponibles:
- GET /                 → Accueil
- GET /vehicles         → Liste tous les véhicules
- GET /vehicles/{id}    → Détails d'un véhicule
- GET /search           → Recherche avec filtres
- GET /stats            → Statistiques du marché
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse
import sqlite3
from pathlib import Path
from typing import Optional

# Initialiser l'API
app = FastAPI(
    title="🚗 LeBonCoin API",
    description="API pour interroger les données de véhicules scrapées sur LeBonCoin",
    version="1.0.0"
)

# Chemin de la base de données
DB_PATH = Path(__file__).parent / "data" / "leboncoin.db"


def get_db():
    """Connexion à la base SQLite"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Pour avoir des dictionnaires
    return conn


# ============================================================================
# ENDPOINT: Accueil
# ============================================================================
@app.get("/", response_class=HTMLResponse)
def home():
    """Page d'accueil avec documentation"""
    return """
    <html>
    <head><title>LeBonCoin API</title></head>
    <body style="font-family: Arial; max-width: 800px; margin: 50px auto;">
        <h1>🚗 LeBonCoin API</h1>
        <p>Bienvenue sur l'API de données automobiles</p>
        <h2>Endpoints disponibles :</h2>
        <ul>
            <li><a href="/vehicles">/vehicles</a> - Liste tous les véhicules</li>
            <li><a href="/vehicles/1">/vehicles/1</a> - Détails du véhicule #1</li>
            <li><a href="/search?marque=BMW">/search?marque=BMW</a> - Chercher les BMW</li>
            <li><a href="/search?prix_max=10000">/search?prix_max=10000</a> - Véhicules < 10000€</li>
            <li><a href="/stats">/stats</a> - Statistiques du marché</li>
            <li><a href="/docs">/docs</a> - Documentation Swagger</li>
        </ul>
    </body>
    </html>
    """


# ============================================================================
# ENDPOINT: Liste des véhicules
# ============================================================================
@app.get("/vehicles")
def get_vehicles(
    limit: int = Query(50, description="Nombre max de résultats"),
    offset: int = Query(0, description="Décalage pour pagination")
):
    """Retourne la liste de tous les véhicules"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, leboncoin_id, marque, modele, annee, km, prix, 
               energie, boite_vitesse, ville, departement, lien
        FROM vehicles
        ORDER BY id DESC
        LIMIT ? OFFSET ?
    """, (limit, offset))
    
    vehicles = [dict(row) for row in cursor.fetchall()]
    
    # Compter le total
    cursor.execute("SELECT COUNT(*) FROM vehicles")
    total = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "vehicles": vehicles
    }


# ============================================================================
# ENDPOINT: Détails d'un véhicule
# ============================================================================
@app.get("/vehicles/{vehicle_id}")
def get_vehicle(vehicle_id: int):
    """Retourne les détails d'un véhicule spécifique"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM vehicles WHERE id = ?", (vehicle_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail=f"Véhicule {vehicle_id} non trouvé")
    
    return dict(row)


# ============================================================================
# ENDPOINT: Recherche avec filtres
# ============================================================================
@app.get("/search")
def search_vehicles(
    marque: Optional[str] = Query(None, description="Filtrer par marque (ex: BMW, PEUGEOT)"),
    modele: Optional[str] = Query(None, description="Filtrer par modèle"),
    prix_min: Optional[int] = Query(None, description="Prix minimum"),
    prix_max: Optional[int] = Query(None, description="Prix maximum"),
    km_max: Optional[int] = Query(None, description="Kilométrage maximum"),
    annee_min: Optional[int] = Query(None, description="Année minimum"),
    energie: Optional[str] = Query(None, description="Type d'énergie (Diesel, Essence, Électrique)"),
    boite: Optional[str] = Query(None, description="Boîte de vitesse (Manuelle, Automatique)"),
    ville: Optional[str] = Query(None, description="Ville"),
    departement: Optional[str] = Query(None, description="Département (ex: 86, 75)"),
    limit: int = Query(50, description="Nombre max de résultats")
):
    """Recherche de véhicules avec filtres multiples"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Construire la requête dynamiquement
    query = "SELECT * FROM vehicles WHERE 1=1"
    params = []
    
    if marque:
        query += " AND UPPER(marque) = UPPER(?)"
        params.append(marque)
    
    if modele:
        query += " AND UPPER(modele) LIKE UPPER(?)"
        params.append(f"%{modele}%")
    
    if prix_min:
        query += " AND prix >= ?"
        params.append(prix_min)
    
    if prix_max:
        query += " AND prix <= ?"
        params.append(prix_max)
    
    if km_max:
        query += " AND km <= ?"
        params.append(km_max)
    
    if annee_min:
        query += " AND annee >= ?"
        params.append(annee_min)
    
    if energie:
        query += " AND UPPER(energie) = UPPER(?)"
        params.append(energie)
    
    if boite:
        query += " AND UPPER(boite_vitesse) LIKE UPPER(?)"
        params.append(f"%{boite}%")
    
    if ville:
        query += " AND UPPER(ville) LIKE UPPER(?)"
        params.append(f"%{ville}%")
    
    if departement:
        query += " AND departement = ?"
        params.append(departement)
    
    query += f" ORDER BY prix ASC LIMIT {limit}"
    
    cursor.execute(query, params)
    vehicles = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return {
        "count": len(vehicles),
        "filters": {
            "marque": marque,
            "prix_min": prix_min,
            "prix_max": prix_max,
            "km_max": km_max,
            "energie": energie
        },
        "vehicles": vehicles
    }


# ============================================================================
# ENDPOINT: Statistiques
# ============================================================================
@app.get("/stats")
def get_stats():
    """Retourne les statistiques du marché automobile"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Stats générales
    cursor.execute("SELECT COUNT(*) FROM vehicles")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT AVG(prix), MIN(prix), MAX(prix) FROM vehicles WHERE prix IS NOT NULL")
    prix_stats = cursor.fetchone()
    
    cursor.execute("SELECT AVG(km) FROM vehicles WHERE km IS NOT NULL")
    km_moyen = cursor.fetchone()[0]
    
    # Top marques
    cursor.execute("""
        SELECT marque, COUNT(*) as count, AVG(prix) as prix_moyen
        FROM vehicles
        WHERE marque IS NOT NULL
        GROUP BY marque
        ORDER BY count DESC
        LIMIT 10
    """)
    top_marques = [{"marque": row[0], "count": row[1], "prix_moyen": round(row[2]) if row[2] else 0} 
                   for row in cursor.fetchall()]
    
    # Top villes
    cursor.execute("""
        SELECT ville, COUNT(*) as count
        FROM vehicles
        WHERE ville IS NOT NULL
        GROUP BY ville
        ORDER BY count DESC
        LIMIT 10
    """)
    top_villes = [{"ville": row[0], "count": row[1]} for row in cursor.fetchall()]
    
    # Répartition énergie
    cursor.execute("""
        SELECT energie, COUNT(*) as count
        FROM vehicles
        WHERE energie IS NOT NULL
        GROUP BY energie
        ORDER BY count DESC
    """)
    repartition_energie = [{"energie": row[0], "count": row[1]} for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        "total_vehicules": total,
        "prix": {
            "moyen": round(prix_stats[0]) if prix_stats[0] else 0,
            "min": prix_stats[1],
            "max": prix_stats[2]
        },
        "km_moyen": round(km_moyen) if km_moyen else 0,
        "top_marques": top_marques,
        "top_villes": top_villes,
        "repartition_energie": repartition_energie
    }


# ============================================================================
# Lancer le serveur
# ============================================================================
if __name__ == "__main__":
    import uvicorn
    print("🚀 Démarrage de l'API sur http://localhost:8000")
    print("📚 Documentation: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
