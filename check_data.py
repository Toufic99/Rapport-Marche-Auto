import sqlite3

conn = sqlite3.connect('data/vehicles.db')
c = conn.cursor()

print('='*60)
print('RESUME DES DONNEES COLLECTEES')
print('='*60)

c.execute('SELECT COUNT(*) FROM vehicles')
print(f'Vehicules: {c.fetchone()[0]}')

c.execute('SELECT COUNT(*) FROM photos')
print(f'Photos: {c.fetchone()[0]}')

print('\n--- Completude des colonnes ---')
colonnes = ['ville', 'code_postal', 'km', 'annee', 'energie', 'boite_vitesse', 'type_vendeur', 'marque', 'modele', 'prix_current']
for col in colonnes:
    c.execute(f"SELECT COUNT(*) FROM vehicles WHERE {col} IS NOT NULL AND {col} != ''")
    count = c.fetchone()[0]
    pct = count/42*100
    bar = '█' * int(pct/5) + '░' * (20-int(pct/5))
    print(f'{col:15} {bar} {count}/42 ({pct:.0f}%)')

print('\n--- Echantillon de vehicules ---')
c.execute('''SELECT marque, modele, annee, km, ville, code_postal, energie, prix_current 
             FROM vehicles LIMIT 8''')
for row in c.fetchall():
    marque = row[0][:12] if row[0] else 'N/A'
    modele = row[1][:15] if row[1] else 'N/A'
    annee = row[2] or 'N/A'
    km = row[3][:10] if row[3] else 'N/A'
    ville = row[4][:12] if row[4] else 'N/A'
    cp = row[5] or 'N/A'
    energie = row[6][:10] if row[6] else 'N/A'
    prix = row[7] or 'N/A'
    print(f'{marque:12} | {modele:15} | {annee:4} | {km:10} | {ville:12} {cp:5} | {energie:10} | {prix}')

conn.close()
