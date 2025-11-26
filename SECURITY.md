# 🔒 Guide de Sécurité

## Responsabilités Légales

### ⚠️ Important - Lisez Attentivement

Ce scraper extrait des données de **LeBonCoin.fr**. Voici les précautions légales essentielles :

#### 1. Respectez les Conditions d'Utilisation
- ✅ Lire [Conditions LeBonCoin](https://www.leboncoin.fr/aide/conditions.htm)
- ✅ Vérifier la clause de scraping/bots
- ✅ Respecter les robots.txt

#### 2. Limitations Raisonnables
```
⚠️ NE PAS:
- Scraper des données personnelles (emails, téléphones)
- Revendre les données
- Utiliser à titre commercial sans accord
- Scraper continuellement (plus de 100 pages/jour)
- Bloquer les serveurs avec trop de requêtes
```

#### 3. Usage Autorisé
```
✅ AUTORISÉ:
- Usage personnel/éducatif
- Analyse de marché
- Portfolio de développeur
- Recherche
- Scraping raisonnable (delays respectés)
```

### Responsabilité Légale
L'utilisation de ce code vous incombe. L'auteur n'est pas responsable de :
- Blocages IP par LeBonCoin
- Poursuites légales pour ToS violation
- Pertes de données
- Dommages directs/indirects

---

## 🔐 Sécurité du Code

### 1. Variables Sensibles

**❌ JAMAIS faire ceci :**
```python
# Mauvais - credentials en dur
headers = {
    'Authorization': 'Bearer mon_token_secret',
    'API-Key': 'clé_super_secrète'
}
```

**✅ À faire :**
```python
# Bon - utiliser variables d'environnement
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('API_KEY')
```

### 2. Fichiers .env

**Toujours mettre .env dans .gitignore :**
```bash
# .gitignore
.env
.env.local
.env.*.local
```

**Ne JAMAIS commit de fichier .env :**
```bash
# ❌ Mauvais
git add .env
git commit -m "Add credentials"

# ✅ Bon
git add .env.example
git commit -m "Add example config"
```

### 3. Base de Données

**Sécuriser l'accès à SQLite :**
```bash
# Permissions fichier (Unix/Linux)
chmod 600 leboncoin_vehicles.db

# Ne pas partager la DB en publique
# Exporter en CSV/JSON pour partage
```

**Valider les entrées :**
```python
# ❌ Mauvais - SQL injection
query = f"SELECT * FROM vehicles WHERE id = {user_input}"

# ✅ Bon - Prepared statements
cursor.execute("SELECT * FROM vehicles WHERE id = ?", (user_input,))
```

---

## 🛡️ Anti-Détection Responsable

### Délais Raisonnables
```python
# ✅ BON - Respecte les serveurs
config = {
    'delay_min': 2,      # Minimum 2 secondes
    'delay_max': 8,      # Maximum 8 secondes
    'max_pages': 50,     # Max 50 pages
}
```

```python
# ❌ MAUVAIS - Surcharge serveurs
config = {
    'delay_min': 0.1,    # Trop rapide
    'delay_max': 0.5,
    'max_pages': 10000,  # Trop agressif
}
```

### Headers Honnêtes
```python
# ✅ Honnête - Identifie le scraper
headers = {
    'User-Agent': 'MyBot/1.0 (+http://myproject.com/bot)',
    'From': 'admin@myproject.com'
}

# ⚠️ Trompeur - Prétendre être navigateur
headers = {
    'User-Agent': 'Mozilla/5.0...',  # Imite navigateur
}
```

---

## 📊 Données Personnelles

### Protection des Données

**Si vous scrapez des données personnelles :**

1. **Consentement**: Avez-vous le droit d'accès ?
2. **RGPD**: Si en UE, respectez les droits RGPD
3. **Stockage**: Sécurisez la base de données
4. **Accès**: Limitez qui peut voir les données
5. **Suppression**: Permettre suppression sur demande

### Anonymisation

```python
# ❌ Données personnelles stockées
vehicles = [
    {
        'seller_name': 'Jean Dupont',      # ⚠️ PII
        'seller_phone': '06 12 34 56 78',  # ⚠️ PII
        'seller_email': 'jean@email.com'   # ⚠️ PII
    }
]

# ✅ Données anonymisées
vehicles = [
    {
        'seller_type': 'Particulier',      # ✅ OK
        'seller_id': 'hash_anonyme_123',   # ✅ OK
        # Pas de contact personnel
    }
]
```

---

## 🔍 Audit & Compliance

### Checklist de Sécurité

- [ ] `.env` ajouté dans `.gitignore`
- [ ] Pas de credentials en dur dans le code
- [ ] Délais appropriés entre requêtes (2+ sec)
- [ ] Pas de données personnelles stockées
- [ ] User-Agent honnête et identifiable
- [ ] Respecte les ToS de LeBonCoin
- [ ] Gère les erreurs 403 proprement
- [ ] Logs contiennent pas de secrets
- [ ] Base de données sécurisée
- [ ] Documentation légale incluse

### Vérifier le Code

```bash
# Chercher credentials en dur
grep -r "password\|secret\|api_key" --include="*.py" .

# Chercher URLs sensibles
grep -r "http://.*@\|https://.*@" --include="*.py" .

# Vérifier fichiers non gitignore
git status
```

---

## ⚠️ Signaler une Vulnérabilité

**Si vous trouvez une faille de sécurité :**

1. **NE PAS l'exposer publiquement** (pas d'issue GitHub)
1. **Contacter en privé** : [toufic.bathish123@gmail.com](mailto:toufic.bathish123@gmail.com)
3. **Décrire**: Qu'est-ce qui pose problème
4. **POC optionnel**: Preuve du concept
5. **Attendre** la correction avant de divulguer

### Exemple Email
```
Sujet: [SECURITY] Vulnérabilité trouvée

Bonjour,

J'ai trouvé une vulnérabilité dans leboncoin-scraper:

Type: SQL Injection
Localisation: leboncoin_scraper.py ligne 123
Sévérité: Haute

Description:
Les requêtes SQL n'utilisent pas prepared statements...

PoC:
...

Merci
```

---

## 🔄 Mise à Jour de Sécurité

### Rester à Jour

```bash
# Vérifier dépendances pour failles
pip install safety
safety check

# Mettre à jour pip et packages
pip install --upgrade pip
pip install --upgrade -r requirements.txt
```

### Versions Sûres

```bash
# Voir versions installées
pip list

# Installer version spécifique
pip install requests==2.31.0
```

---

## 📚 Ressources Sécurité

- [OWASP Top 10](https://owasp.org/www-project-top-ten/) - Vulnérabilités web
- [PEP 8](https://pep8.org/) - Code sécurisé Python
- [RGPD](https://www.cnil.fr/fr/rgpd-reglement-general-sur-la-protection-des-donnees) - Données personnelles UE
- [Scraping Éthique](https://www.ibiblio.org/pub/docs/about.ethics.html)

---

## ✅ Checklist Avant de Publier

- [ ] Pas de credentials visibles
- [ ] .env dans .gitignore
- [ ] Documentation légale complète
- [ ] Code analysé pour failles
- [ ] Dépendances à jour
- [ ] Tests de sécurité fait
- [ ] License inclus
- [ ] SECURITY.md dans repo

---

**Scraping responsable = succès à long terme ! 🚀**
