import sqlite3

conn = sqlite3.connect('leboncoin_vehicles.db')
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM vehicles')
total = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM vehicles WHERE statut = "ACTIVE"')
actives = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM vehicles WHERE priorite = 1')
poitiers = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM photos')
photos = cursor.fetchone()[0]

print('📊 STATISTIQUES ACTUELLES')
print('========================')
print(f'🚗 Total voitures: {total}')
print(f'✅ Actives: {actives}')
print(f'⭐ Poitiers: {poitiers}')
print(f'📸 Photos: {photos}')

conn.close()
