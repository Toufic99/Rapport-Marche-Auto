import sqlite3

conn = sqlite3.connect('data/vehicles.db')
c = conn.cursor()

print("=== LIENS DES ANNONCES ===")
c.execute("SELECT id, lien FROM vehicles WHERE lien IS NOT NULL LIMIT 10")
for row in c.fetchall():
    lien = row[1] if row[1] else 'N/A'
    print(f"ID {row[0]}: {lien[:80]}...")

print("\n=== STATISTIQUES LIENS ===")
c.execute("SELECT COUNT(*) FROM vehicles WHERE lien IS NOT NULL AND lien != ''")
print(f"Avec lien: {c.fetchone()[0]}")
c.execute("SELECT COUNT(*) FROM vehicles WHERE lien LIKE '%leboncoin.fr%'")
print(f"Liens LeBonCoin valides: {c.fetchone()[0]}")

conn.close()
