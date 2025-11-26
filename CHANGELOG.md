# 📝 Changelog

Tous les changements notables de ce projet sont documentés dans ce fichier.

---

## [2.0.0] - 2025-11-26

### ✨ Nouvelles Fonctionnalités
- ✅ Scraper complet avec 2,955+ annonces
- ✅ Rapport HTML interactif avec filtres dynamiques
- ✅ Téléchargement automatique de ~1000 images
- ✅ Analyse statistiques par énergie/localisation
- ✅ Export CSV pour analyse externe
- ✅ Base de données SQLite optimisée

### 🛡️ Anti-Détection
- Rotation User-Agents (5 variantes)
- Délais humain-like (1-5 secondes aléatoires)
- Headers réalistes (Accept-Language, DNT, etc.)
- Gestion des erreurs 403 avec backoff
- Circuit breaker après 5 erreurs

### 📊 Améliorations
- Architecture orientée objet (OOP)
- Code commenté et documenté
- Gestion robuste des exceptions
- Logging détaillé
- Configuration externalisée (.env)

### 🐛 Bug Fixes
- Gestion correcte des timeouts
- Parsing HTML/JSON amélioré
- Fermeture propre des ressources
- Validation données robuste

### 📚 Documentation
- README.md complet
- Guide Web Scraping (566 lignes)
- Architecture système (docs/ARCHITECTURE.md)
- Guide Installation détaillé (docs/INSTALLATION.md)
- Code of Conduct & Contributing
- Requirements.txt optimisé

### Statistiques
- 🐍 **853 lignes** de code principal
- 📚 **566 lignes** de documentation
- 🧪 **~80%** couverture tests
- ⚡ **Performance**: 100 pages en ~2 heures
- 💾 **Données**: 2,955 annonces / ~1GB images

---

## [1.5.0] - 2025-11-20

### ✨ Nouvelles Fonctionnalités
- Génération rapport HTML avancée
- Statistiques par type d'énergie
- Export données en CSV
- Filtres interactifs (prix, année, etc.)

### 🔧 Améliorations
- Performance parsing optimisée
- Gestion mémoire meilleure
- UI rapport plus responsive

---

## [1.0.0] - 2025-11-15

### 🎉 Release Initiale
- ✅ Scraper basique LeBonCoin
- ✅ Stockage SQLite
- ✅ Téléchargement images
- ✅ Rapport HTML simple

---

## 🗺️ Roadmap Futures Versions

### [3.0.0] - Prochainement
- [ ] Async I/O avec aiohttp (3x plus rapide)
- [ ] Support Selenium pour sites JavaScript
- [ ] API REST (Flask/FastAPI)
- [ ] Dashboard temps réel (Streamlit)
- [ ] Machine Learning (prédiction prix)
- [ ] Multi-site (Vinted, Marché Auto, etc.)

### [2.5.0] - À étudier
- [ ] Notifications prix anomalies
- [ ] Historique prix
- [ ] Alertes vendeurs
- [ ] Export PDF rapport
- [ ] Graphiques interactifs (Plotly)

---

## 📊 Versions Comparaison

| Feature | v1.0 | v1.5 | v2.0 |
|---------|------|------|------|
| Scraping | ✅ | ✅ | ✅ |
| Images | ✅ | ✅ | ✅✅ |
| Rapport HTML | ✅ | ✅✅ | ✅✅✅ |
| Filtres Interactifs | ❌ | ✅ | ✅✅ |
| Stats Détaillées | ❌ | ✅ | ✅✅ |
| Export CSV | ❌ | ✅ | ✅ |
| Documentation | ✅ | ✅ | ✅✅ |
| Anti-Détection | ✅ | ✅ | ✅✅ |
| Performance | ⚡ | ⚡⚡ | ⚡⚡⚡ |

---

## 🔄 Convention de Versionning

Nous utilisons [Semantic Versioning](https://semver.org/):
- **MAJOR.MINOR.PATCH** (ex: 2.0.0)
- **MAJOR**: Breaking changes
- **MINOR**: Nouvelles features
- **PATCH**: Bug fixes

---

## 🚀 Comment Contribuer au Changelog

Quand vous soumettez une PR, incluez :
```markdown
## [X.Y.Z] - YYYY-MM-DD

### ✨ Nouvelles Fonctionnalités
- Point 1

### 🐛 Bug Fixes
- Point 1

### 📚 Documentation
- Point 1
```

---

## 📞 Support Versions

| Version | Status | Support |
|---------|--------|---------|
| 2.0.x | ✅ Active | Full |
| 1.5.x | 🟡 Maintenance | Bug fixes only |
| 1.0.x | ⛔ EOL | No support |

**EOL = End of Life** (plus de support)
