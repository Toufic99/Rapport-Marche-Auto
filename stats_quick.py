import sqlite3
import pandas as pd

DB_PATH = 'data/vehicles.db'

conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query('SELECT * FROM vehicles', conn)

print('\n' + '='*70)
print('📊 STATISTIQUES DE LA BASE DE DONNÉES v3.0')
print('='*70)

print(f'\n📈 DONNÉES COLLECTÉES:')
print(f'   • Total véhicules: {len(df)}')
print(f'   • Marques différentes: {df["marque"].nunique()}')
print(f'   • Villes différentes: {df["ville"].nunique()}')

if df['prix'].notna().any():
    print(f'\n💰 PRIX:')
    print(f'   • Prix moyen: {df["prix"].mean():.0f}€')
    print(f'   • Prix médian: {df["prix"].median():.0f}€')
    print(f'   • Prix minimum: {df["prix"].min():.0f}€')
    print(f'   • Prix maximum: {df["prix"].max():.0f}€')

if df['km'].notna().any():
    print(f'\n🛣️  KILOMÉTRAGE:')
    print(f'   • Km moyen: {df["km"].mean():.0f} km')
    print(f'   • Km médian: {df["km"].median():.0f} km')

print(f'\n🚗 TOP 10 MARQUES:')
top_marques = df['marque'].value_counts().head(10)
for i, (marque, count) in enumerate(top_marques.items(), 1):
    print(f'   {i}. {marque}: {count} véhicules')

print(f'\n📍 TOP 10 VILLES:')
top_villes = df['ville'].value_counts().head(10)
for i, (ville, count) in enumerate(top_villes.items(), 1):
    print(f'   {i}. {ville}: {count} véhicules')

print(f'\n⚡ ÉNERGIES:')
energies = df['energie'].value_counts()
for energie, count in energies.items():
    pct = (count / len(df) * 100)
    print(f'   • {energie}: {count} ({pct:.1f}%)')

if 'nb_photos' in df.columns:
    print(f'\n📸 PHOTOS:')
    print(f'   • Total photos comptées: {df["nb_photos"].sum():.0f}')
    print(f'   • Moyenne par annonce: {df["nb_photos"].mean():.1f}')

if 'date_scrape' in df.columns:
    dates = df['date_scrape'].dropna()
    if len(dates) > 0:
        first = dates.min()[:10]
        last = dates.max()[:10]
        print(f'\n📅 PÉRIODE:')
        print(f'   • Première collecte: {first}')
        print(f'   • Dernière collecte: {last}')

print('\n' + '='*70)

conn.close()
