import sqlite3

conn = sqlite3.connect('data/vehicles.db')
c = conn.cursor()

# Nettoyer les villes parasites
textes_parasites = ['en ligne', 'votre espace', 'bailleur', 'annonce', 'favori', 'batterie', 'aller']

print("Nettoyage des villes parasites...")
for texte in textes_parasites:
    c.execute("UPDATE vehicles SET ville = NULL WHERE ville LIKE ?", (f'%{texte}%',))
    print(f"  - '{texte}': {c.rowcount} lignes nettoyees")

conn.commit()

# Verifier
c.execute('SELECT COUNT(*) FROM vehicles WHERE ville IS NOT NULL')
count_valid = c.fetchone()[0]
c.execute('SELECT COUNT(*) FROM vehicles')
total = c.fetchone()[0]
print(f"\nVehicules avec ville valide: {count_valid}/{total}")

c.execute('SELECT DISTINCT ville FROM vehicles WHERE ville IS NOT NULL LIMIT 10')
villes = [r[0] for r in c.fetchall()]
print(f"Villes restantes: {villes}")

conn.close()
print("\n[OK] Base nettoyee!")
