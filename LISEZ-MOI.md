# Vitrine Laforêt Montauban — écran Samsung OM46N (portrait)

Présentation de ~10 pages qui se met à jour toute seule : annonces à vendre / à louer lues sur laforet.com/montauban, visuels Instagram, services, contact.

## Comment ça marche

```
laforet.com/montauban ──► generer.py ──► public/ (index.html + data.json + images) ──► hébergement web ──► écran
     (annonces, horaires)   (1×/jour)                                                   (Cloudflare Pages)   (URL Launcher)
```

- `public/index.html` : le « lecteur » affiché sur l'écran (1080×1920, portrait). Il relit `data.json` toutes les 10 min et se recharge chaque nuit à 4 h.
- `generer.py` : récupère les annonces, télécharge photos + DPE, crée les QR codes, lit les horaires, copie les visuels du dossier `instagram/`.
- **Seul `public/` est publié.** Ne rien mettre de sensible dedans.

Déroulé (≈ 2 min) : Accueil · 3 ventes · Nos métiers + estimation · 3 locations · Instagram · Contact + avis Google. Les annonces tournent : chaque tour affiche 3 nouvelles ventes/locations parmi les 6 sélectionnées (nouveautés et exclusivités en priorité).

## Mise en route

### 1. Tester sur le PC
```
pip install segno pillow
python generer.py
python -m http.server 8765 --directory public
```
Ouvrir http://localhost:8765 (ajouter `?fast=1&debug=1` pour un défilement rapide avec infos de contrôle).

### 2. Hébergement (en place)
Dépôt GitHub : https://github.com/LaurentAllsi/vitrine-laforet-montauban
Adresse à saisir dans l'écran : **https://laurentallsi.github.io/vitrine-laforet-montauban/**
Publication par GitHub Pages, sans rien à installer ni à payer.

### 3. Afficher la vitrine sur l'écran — ATTENTION
**L'URL Launcher intégré Samsung ne sait pas afficher une simple page web.** « Install Web App » attend un dossier contenant un `sssp_config.xml` et une application Tizen `.wgt` **signée avec un certificat Samsung** (test réalisé le 19/09/2026 : google.com, neverssl.com et la vitrine donnent tous « impossible de télécharger l'application Web »). Ne pas insister avec cette méthode.

Voies possibles :
1. **Petit lecteur branché en HDMI** (ancien mini-PC, Fire TV Stick, Raspberry Pi, mini-PC Windows) qui ouvre la vitrine en plein écran (navigateur en mode kiosque). Aucune modification de la vitrine. Portrait : rotation dans le lecteur (Windows) ou par l'écran (`MENU → OnScreen Display → Display Orientation → Source Content Orientation → Portrait`) avec `?rot=90` ou `?rot=-90` dans l'adresse.
2. **Vidéo / images sur clé USB** lues par MagicInfo Lite (gratuit, mise à jour manuelle).
3. **Service d'affichage dynamique** dont le lecteur est déjà signé pour Samsung (abonnement).

### 4. Mise à jour automatique (dans le cloud, PC éteint)
Le workflow GitHub Actions (`.github/workflows/vitrine.yml`) s'exécute **chaque jour vers 6 h 30 et 14 h 30** : il relit laforet.com/montauban, régénère les données et republie. Suivi : onglet *Actions* du dépôt ; lancement immédiat : *Run workflow*.
- Si le site laforet.com est indisponible ou renvoie trop peu d'annonces, **rien n'est publié** : la version de la veille reste affichée.
- GitHub désactive les tâches planifiées d'un dépôt public inactif depuis 60 jours ; le workflow enregistre `data.json` chaque jour pour rester actif. Si un e-mail GitHub signale la désactivation, cliquer sur *Enable workflow*.
- `mettre_a_jour.bat` reste disponible pour lancer une mise à jour depuis le PC (optionnel).

## Instagram
Ajouter les visuels dans le dossier `instagram/` du dépôt : GitHub → dossier `instagram` → *Add file → Upload files* (jpg / png, idéalement 4:5 ou carré). La publication se relance automatiquement ; les 4 plus récents sont affichés. Depuis le PC : déposer dans le dossier local `instagram/` puis lancer `mettre_a_jour.bat`. Instagram interdit la récupération automatique sans l'API officielle (compte pro + Facebook + jeton).

## Mentions légales affichées
Prix, honoraires (vendeur ou locataire), dépôt de garantie et **DPE** sont repris de l'annonce sur laforet.com pour chaque bien affiché.

## Fichiers
| Fichier | Rôle |
|---|---|
| `generer.py` | Lecture du site + génération des données |
| `mettre_a_jour.bat` | Lance la génération puis publie (git) |
| `public/index.html` | Lecteur affiché sur l'écran |
| `public/data.json`, `public/img/` | Données et images générées (ne pas éditer à la main) |
| `instagram/` | Vos visuels à afficher |

Charte : Laforêt 2026 (bleu #153D8A, cyan #009EE3, police Lexend, bulle à pointe bas-gauche).
