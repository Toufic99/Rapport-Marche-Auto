# 📊 Exemple d'Analyse Statistique

**Données généré à partir de: ~2,955 annonces automobiles**
**Période: Janvier 2025**

---

## 💰 Statistiques de Prix

### Par Type d'Énergie

| Type Énergie  | Nb Annonces | Prix Min | Prix Max | Prix Moyen | 
|--------------|-------------|----------|----------|-----------|
| Diesel       | 1,245       | 4,200€   | 89,500€  | 18,450€   |
| Essence      | 1,156       | 3,800€   | 95,000€  | 15,320€   |
| Hybride      | 312         | 12,500€  | 78,000€  | 28,950€   |
| Électrique   | 142         | 15,000€  | 125,000€ | 52,100€   |
| Autre        | 100         | 2,000€   | 45,000€  | 12,300€   |

### Analyse Diesel vs Essence

- **Diesel** représente **42%** des annonces
- **Essence** représente **39%** des annonces
- Les véhicules **Diesel** sont en moyenne **3,130€ plus chers** (écart de 20%)
- Diesel populaire pour usage professionnel/longues distances

---

## 🚙 Distribution par Kilométrage

| Plage KM    | Nb Véhicules | % du Total | Prix Moyen |
|-------------|--------------|-----------|-----------|
| 0 - 50,000  | 245          | 8.3%      | 28,500€   |
| 50-100,000  | 890          | 30.1%     | 22,100€   |
| 100-150,000 | 1,120        | 37.9%     | 14,800€   |
| 150-200,000 | 565          | 19.1%     | 9,200€    |
| 200,000+    | 135          | 4.6%      | 4,500€    |

**Insight**: Le marché se concentre sur les véhicules 100-150k km = meilleur rapport qualité/prix

---

## 📅 Distribution par Année

| Année | Nb Véhicules | % | Prix Moyen |
|-------|--------------|---|-----------|
| 2023+ | 120          | 4.1% | 42,800€ |
| 2021-2022 | 380 | 12.8% | 31,200€ |
| 2018-2020 | 890 | 30.1% | 19,500€ |
| 2015-2017 | 980 | 33.1% | 11,800€ |
| 2010-2014 | 485 | 16.4% | 6,200€ |
| Avant 2010 | 120 | 4.1% | 2,800€ |

---

## 🏆 Marques les Plus Fréquentes

| Rang | Marque | Nb Annonces | % | Prix Moyen |
|------|--------|-------------|---|-----------|
| 1    | Renault | 285 | 9.6% | 12,450€ |
| 2    | Peugeot | 278 | 9.4% | 13,200€ |
| 3    | Citroën | 215 | 7.3% | 10,800€ |
| 4    | Ford    | 185 | 6.3% | 11,500€ |
| 5    | Volkswagen | 168 | 5.7% | 16,300€ |
| 6-10 | Autres  | 1,426 | 48.2% | 18,900€ |

**Top Premium**: BMW, Mercedes, Audi avec prix moyen 32,000€+

---

## 🏙️ Top 10 Localités

| Région | Nb Annonces | % | Prix Moyen |
|--------|------------|---|-----------|
| Île-de-France | 385 | 13.0% | 19,800€ |
| Provence-Alpes-Côte d'Azur | 265 | 8.9% | 18,200€ |
| Auvergne-Rhône-Alpes | 245 | 8.3% | 16,500€ |
| Nouvelle-Aquitaine | 195 | 6.6% | 14,200€ |
| Occitanie | 180 | 6.1% | 13,800€ |
| Autres | 1,685 | 56.9% | 16,800€ |

---

## 📈 Corrélation Kilométrage vs Prix

```
Prix (€)
50,000 │     ★
        │  ★    ★
40,000 │
        │      ★
30,000 │   ★      ★
        │ ★    ★  
20,000 │  ★   ★ ★
        │★   ★  ★
10,000 │  ★ ★  ★
        │ ★  ★
    0 └─────────────────── km
      0  50k 100k 150k 200k+
```

**Corrélation Négative**: -0.82 (forte)
- Chaque 10,000 km = perte moyenne de **1,200€**

---

## 💼 Vendeurs (Particuliers vs Concessionnaires)

| Type Vendeur | Nb Annonces | % | Prix Moyen | Durée Moyenne |
|-------------|------------|---|-----------|--------------|
| Particulier | 2,485 | 84.0% | 14,500€ | 42 jours |
| Concessionnaire | 325 | 11.0% | 22,300€ | 28 jours |
| Professionnel | 145 | 4.9% | 18,700€ | 35 jours |

---

## 🔍 Observations Clés

1. **Marché Dominant**: Diesel & Essence représentent **81%** des annonces
2. **Valeur**: Le sweet spot = 3-7 ans, 80-120k km → **rapport qualité/prix optimal**
3. **Géographie**: Île-de-France représente **13%** du marché
4. **Vendeurs**: **84% particuliers** - accès direct majoritaire
5. **Tendance**: Hybrides et électriques en croissance (+12% YoY)

---

## 📌 Notes sur ces Données

✅ Données anonymisées à titre d'exemple  
✅ Structure réelle issue du scraper LeBonCoin  
✅ Nombres normalisés pour démonstration  
✅ Voir le rapport HTML pour interactions complètes  

**Pour générer vos propres statistiques:**
```bash
python stats.py
```
