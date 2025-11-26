# 📊 Exemples de Résultats

Ce dossier contient des **exemples de résultats** générés par le scraper.

## 📁 Fichiers

### `sample_output.json`
Exemple de données structurées extraites (10 annonces d'exemple)

Contient :
- ID unique
- Titre, Marque, Modèle
- Prix, Kilométrage, Année
- Type énergie, Boîte vitesses
- Localisation, Vendeur
- Statut (Active/Vendue)

### `sample_statistics.md`
Exemple de statistiques générées à partir de ~2,955 annonces

Contient :
- Prix moyen par type d'énergie
- Distribution géographique
- Kilométrage moyen par année
- Analyses de tendances

### `RAPPORT_EXEMPLE.md`
Extrait du rapport HTML généré en format texte

Montre :
- Structure du rapport
- Types de filtres
- Analyses incluses
- Format final

---

## 🚀 Pour Générer Vos Propres Résultats

```bash
# 1. Scraper les données
python leboncoin_scraper.py

# 2. Générer le rapport
python report_generator.py

# 3. Analyser les statistiques
python stats.py
```

**Fichiers générés :**
- `leboncoin_vehicles.db` (base de données SQLite)
- `leboncoin_rapport.html` (rapport interactif)
- `leboncoin_rapport_complet.csv` (export CSV)

---

## 📊 Exemple de Résultat Réel

Pour voir un exemple concret du rapport généré, consultez les fichiers dans ce dossier !
