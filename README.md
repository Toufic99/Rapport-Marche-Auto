# 🚗 LEBONCOIN SCRAP BEAUTIFUL - SYSTÈME COMPLET & INNOVANT

## ✨ FONCTIONNALITÉS

### 1. **Scraping Intelligent**
- ✅ Récupère les annonces de voitures de LeBonCoin
- ✅ Numéro ID unique pour chaque voiture (#1, #2, etc.)
- ✅ Extraction automatique: marque, modèle, prix, description
- ✅ **Téléchargement des photos** dans dossier `voitures_photos/`

### 2. **Suivi des Annonces**
- ✅ **Détection automatique des ventes** (annonce disparue = vendue)
- ✅ Colonne **STATUT**: ACTIVE ou VENDUE
- ✅ **Date de vente** enregistrée automatiquement
- ✅ **Durée de vente**: Jours entre annonce et vente
- ✅ **Historique des prix** en base de données

### 3. **Base de Données SQLite**
- **leboncoin_vehicles.db** contient:
  - Table `vehicles`: Infos complètes de chaque voiture
  - Table `price_history`: Historique des prix
  - Table `photos`: Références des photos téléchargées
  
### 4. **Rapports Générés**
- **leboncoin_rapport_complet.csv**: Export complet avec tous les détails
- **leboncoin_rapport.html**: Rapport visuel avec statistiques
- Données mises à jour à CHAQUE scraping

### 5. **Mise à Jour Automatique - 2x PAR JOUR**
- **08:00 (Matin)**: Premier scraping
- **18:00 (Soir)**: Deuxième scraping
- Détection des changements entre matin et soir
- Historique complet disponible

---

## 🚀 LANCEMENT RAPIDE

### Option 1: TEST IMMÉDIAT
```powershell
cd C:\Users\User\OneDrive\Desktop\TripoDATA
.\TripoEnv\Scripts\python.exe leboncoin_scrap_beautiful.py
```

### Option 2: PLANIFICATION AUTOMATIQUE (Recommandé)

**Étape 1: Ouvrir PowerShell EN TANT QU'ADMINISTRATEUR**

**Étape 2: Exécuter le script de création des tâches**
```powershell
cd C:\Users\User\OneDrive\Desktop\TripoDATA
powershell -ExecutionPolicy Bypass -File create_tasks.ps1
```

**Résultat:** Deux tâches créées (8h et 18h) ✓

---

## 📊 FICHIERS GÉNÉRÉS

| Fichier | Description |
|---------|-------------|
| `leboncoin_vehicles.db` | Base de données SQLite complète |
| `leboncoin_rapport_complet.csv` | Export CSV (Excel) |
| `leboncoin_rapport.html` | Rapport visuel (statistiques) |
| `voitures_photos/` | Dossier avec toutes les photos |

---

## 📈 DONNÉES DISPONIBLES PAR VOITURE

Pour chaque voiture scrapée:

```
ID:                    #1, #2, #3, ...
Titre:                 "Renault Clio 1.5 dCi 75cv"
Marque:                "Renault"
Modèle:                "Clio"
Prix Initial:          8500 €
Prix Actuel:           8500 € (peut changer)
Prix Historique:       [8500, 8400, 8300...] (SQLite)
Statut:                ACTIVE ou VENDUE
Date Annonce:          2025-11-19
Date Première Vue:     2025-11-19 17:06:04
Date Dernière Vue:     2025-11-19 18:30:15
Date Vendu:            2025-11-20 08:15:00
Jours en Vente:        1 jour
Lien Annonce:          https://www.leboncoin.fr/vo/...
Photos:                photo_1.jpg, photo_2.jpg...
Description Complète:  [Texte complet de l'annonce]
```

---

## 🔍 ANALYSES POSSIBLES

Avec ces données, tu peux:

1. **Prix moyen par marque** → Comparer Renault vs Peugeot vs autres
2. **Temps de vente moyen** → Quelle voiture se vend vite?
3. **Tendance des prix** → Prix qui baisse = urgence de vendre?
4. **Alertes de prix** → Notifier si prix baisse de 500€
5. **Marques tendance** → Quelles voitures se vendent le plus?
6. **Âge vs Prix** → Années par rapport au prix

---

## 🛠️ COMMANDES UTILES

### Voir les tâches planifiées
```powershell
Get-ScheduledTask -TaskName "LeBonCoin*" | Select-Object TaskName, State
```

### Exécuter maintenant (matin)
```powershell
Start-ScheduledTask -TaskName "LeBonCoin Scraper Morning"
```

### Exécuter maintenant (soir)
```powershell
Start-ScheduledTask -TaskName "LeBonCoin Scraper Evening"
```

### Voir l'historique d'exécution
```powershell
Get-ScheduledTaskInfo -TaskName "LeBonCoin Scraper Morning"
```

### Supprimer les tâches
```powershell
Unregister-ScheduledTask -TaskName "LeBonCoin Scraper Morning" -Confirm:$false
Unregister-ScheduledTask -TaskName "LeBonCoin Scraper Evening" -Confirm:$false
```

### Ouvrir le rapport visuel
```powershell
Start-Process leboncoin_rapport.html
```

### Ouvrir la base de données (SQLite)
```powershell
# Télécharger DB Browser for SQLite depuis:
# https://sqlitebrowser.org/
# Puis ouvrir leboncoin_vehicles.db
```

---

## 💡 EXEMPLE DE WORKFLOW QUOTIDIEN

```
08:00 ─► MATIN
  ├─ leboncoin_scrap_beautiful.py exécuté
  ├─ Scrape LeBonCoin
  ├─ Détecte 10 nouvelles voitures
  ├─ Détecte 2 voitures vendues
  ├─ Mise à jour BD
  └─ Rapport généré

18:00 ─► SOIR
  ├─ leboncoin_scrap_beautiful.py exécuté (2ème fois)
  ├─ Scrape LeBonCoin
  ├─ Détecte 5 nouvelles voitures
  ├─ Détecte 3 voitures vendues
  ├─ Mise à jour BD
  └─ Rapport généré (mis à jour)

RESULTAT:
  - 15 nouvelles voitures du jour
  - 5 voitures vendues du jour
  - Historique complet en BD
  - Données prêtes pour analyse
```

---

## 🎯 PROCHAINES ÉTAPES POSSIBLES

1. **Alertes Email** → Être notifié des baisse de prix
2. **Dashboard Web** → Interface web pour visualiser les données
3. **API** → Accéder aux données via API REST
4. **ML/Prédictions** → Prédire le prix de vente optimal
5. **Notifications** → Alerter quand une voiture spécifique se vend
6. **Export PowerBI** → Analyser avec Power BI

---

## 📝 NOTES IMPORTANTES

- ✅ Le système est **entièrement automatisé**
- ✅ Les données sont **persistantes** (BD SQLite)
- ✅ Les photos sont **sauvegardées localement**
- ✅ L'historique est **conservé** (voitures + prix)
- ✅ **Zéro configuration supplémentaire** après création des tâches
- ⚠️ Les tâches nécessitent **PowerShell EN TANT QU'ADMIN** pour être créées

---

## 🆘 TROUBLESHOOTING

### Les tâches ne se créent pas
- ✓ Vérifier que PowerShell est exécuté EN TANT QU'ADMINISTRATEUR
- ✓ Utiliser le script `create_tasks.ps1` (pas le .bat)

### La scraping échoue
- ✓ Vérifier la connexion Internet
- ✓ Vérifier que LeBonCoin n'a pas changé sa structure HTML
- ✓ Vérifier les logs dans le fichier python

### Base de données corrompue
- ✓ Supprimer `leboncoin_vehicles.db` et relancer
- ✓ Les données seront rescrapées à nouveau

---

## 📞 SUPPORT

Les erreurs courantes:
- `'charmap' codec` → Encodage Windows (géré dans le code)
- `module not found` → Vérifier les imports et packages
- `Access denied` → Exécuter PowerShell EN TANT QU'ADMIN

---

**Créé avec ❤️ pour un scraping innovant et performant !**
