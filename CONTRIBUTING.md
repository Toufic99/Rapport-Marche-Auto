# 🤝 Guide de Contribution

Merci d'intéresser au projet ! Les contributions sont bienvenues et très appréciées.

## 📋 Comment Contribuer

### 1️⃣ Signaler un Bug 🐛

Ouvre une **Issue** avec :
- **Titre clair** : Ex: `[BUG] Timeout après 500 requêtes`
- **Description** : Qu'est-ce qui s'est passé ?
- **Étapes pour reproduire** : Comment l'erreur se manifeste
- **Résultat attendu** : Quel comportement devrait se produire
- **Environnement** : OS, version Python, etc.

```
Titre: [BUG] Error 403 après 100 pages

Description:
Le scraper s'arrête avec erreur 403 après ~100 pages.

Étapes:
1. Configurer max_pages=200
2. Lancer scraper
3. Attendre ~1h

Résultat: HTTP 403 Forbidden après 96 pages
Attendu: Continuer avec retry
```

### 2️⃣ Proposer une Amélioration 💡

Crée une **Discussion** (tab Discussions) ou une **Issue** avec tag `enhancement` :
- Décrire l'amélioration
- Expliquer le bénéfice
- Proposer une approche (optionnel)

Exemples d'améliorations souhaitées :
- [ ] Ajouter support Selenium pour sites dynamiques
- [ ] Intégrer base de données PostgreSQL
- [ ] Créer API Flask pour données temps réel
- [ ] Dashboard Streamlit interactif
- [ ] Support multi-site (Vinted, Leboncoin, etc.)

### 3️⃣ Soumettre du Code 🚀

#### Fork et Clone
```bash
# 1. Fork le repo (bouton GitHub)
# 2. Clone ton fork
git clone https://github.com/TON_USERNAME/leboncoin-scraper.git
cd leboncoin-scraper

# 3. Ajouter remote upstream
git remote add upstream https://github.com/ORIGINAL_AUTHOR/leboncoin-scraper.git
```

#### Créer une Branch
```bash
# Toujours créer une nouvelle branche pour chaque feature/fix
git checkout -b feature/ma-super-feature

# Ou pour un bug fix:
git checkout -b fix/correction-timeout
```

**Convention de nommage** :
- `feature/nom-feature` : Nouvelle fonctionnalité
- `fix/nom-bug` : Correction de bug
- `docs/nom-doc` : Documentation
- `refactor/nom-refactoring` : Refactorisation
- `test/nom-test` : Ajout de tests

#### Développer
```bash
# 1. Mettre en place environnement
python -m venv env
source env/bin/activate  # Sur Windows: env\Scripts\activate
pip install -r requirements.txt

# 2. Faire les modifications
# Éditer les fichiers, ajouter features, fixer bugs

# 3. Tester
pytest tests/
python -m pytest --cov=.  # Avec coverage

# 4. Vérifier la qualité
# - Code lisible et commenté
# - Suivre le style PEP 8
# - Ajouter docstrings
```

#### Committer et Pusher
```bash
# Committer avec message clair et descriptif
git add .
git commit -m "feature: ajouter support Selenium pour sites JS dynamiques"

# Messages de commit utiles:
# feature: ajouter...
# fix: corriger...
# docs: mettre à jour documentation
# refactor: réorganiser code...
# test: ajouter tests pour...

# Pusher vers ta branche
git push origin feature/ma-super-feature
```

#### Ouvrir une Pull Request (PR)
1. Aller sur GitHub
2. Cliquer **"Compare & pull request"**
3. Remplir le template :

```markdown
## Description
Brève description de ce PR

## Type de changement
- [ ] Bug fix (correction sans breaking change)
- [ ] Feature (nouvelle fonctionnalité)
- [ ] Breaking change (peut casser utilisateurs)
- [ ] Documentation update

## Changements
- Point 1
- Point 2
- Point 3

## Tests effectués
- [ ] Test local effectué
- [ ] Tests unitaires passent
- [ ] Pas de warning

## Screenshots (si applicable)
[Ajouter screenshots si UI change]
```

---

## 📝 Standards de Code

### Style & Format
- ✅ Suivre **PEP 8** (Python)
- ✅ Max 100 caractères par ligne
- ✅ Noms explicites (pas `a`, `x`, `temp`)
- ✅ Ajouter docstrings aux fonctions

### Exemple bon code
```python
def extract_vehicle_data(html_content: str) -> dict:
    """
    Extraire les données d'un véhicule depuis le HTML.
    
    Args:
        html_content (str): Contenu HTML brut
        
    Returns:
        dict: Données structurées du véhicule
        
    Raises:
        ValueError: Si HTML invalide
    """
    try:
        soup = BeautifulSoup(html_content, 'lxml')
        vehicle_data = {
            'title': soup.find('h1', class_='title').text,
            'price': soup.find('span', class_='price').text,
            'km': soup.find('span', class_='km').text,
        }
        return vehicle_data
    except AttributeError as e:
        raise ValueError(f"HTML structure invalide: {e}")
```

### Tests
Toute nouvelle feature doit avoir des tests :
```python
def test_extract_vehicle_data():
    """Tester extraction de données véhicule"""
    html = "<div><h1>Renault Clio</h1></div>"
    result = extract_vehicle_data(html)
    assert result['title'] == "Renault Clio"
```

---

## 🔄 Workflow Review

1. **Tu ouvres un PR**
   ↓
2. **Mainteneur/Contributeurs critiquent**
   ↓
3. **Tu apportes les modifications** (si demandé)
   ↓
4. **Merge en master** ✅

Sois patient et constructif dans les échanges !

---

## 📚 Ressources

- [PEP 8 Style Guide](https://pep8.org/)
- [Git Documentation](https://git-scm.com/doc)
- [GitHub Guides](https://guides.github.com/)
- [Python Docstrings](https://www.python.org/dev/peps/pep-0257/)

---

## ❓ Questions ?

- Ouvre une **Issue** avec tag `question`
- Utilise l'onglet **Discussions** pour questions générales
- 📧 Contacter [toufic.bathish123@gmail.com](mailto:toufic.bathish123@gmail.com) ou [LinkedIn](https://www.linkedin.com/in/toufic-bathich-b73081233) si besoin

---

## 🎉 Merci !

Toute contribution, même petite, aide à améliorer le projet.
Tu seras crédité dans le fichier `CONTRIBUTORS.md` !

**Happy coding! 🚀**
