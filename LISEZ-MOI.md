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

### 3. Régler l'écran (manuel Samsung LFD, chap. 07)
1. Brancher l'écran au réseau (RJ45 ou Wi-Fi) et régler **date et heure**.
2. `MENU → OnScreen Display → Display Orientation` → orientation **Portrait** (« Source Content Orientation »).
3. `MENU → Système → Play via` → **URL Launcher**.
4. `HOME → URL Launcher Settings → Install Web App` → saisir l'adresse Cloudflare de la vitrine.
5. `HOME → URL Launcher` pour lancer. **À tester** : éteindre puis rallumer l'écran (ou couper le courant) et vérifier que la vitrine redémarre seule ; sinon regarder les réglages `Système` (source à l'allumage).
6. Programmer l'allumage / extinction : `On/Off Timer` (manuel p. 52-53).

Si la page s'affiche **couchée** : ajouter `?rot=90` (ou `?rot=-90`) à l'adresse, ou `?rot=auto`.
Si le menu « URL Launcher » n'existe pas sur votre modèle, ou si l'écran refuse la connexion sécurisée (HTTPS) : voir le plan B.

### 4. Mise à jour automatique (dans le cloud, PC éteint)
Le workflow GitHub Actions (`.github/workflows/vitrine.yml`) s'exécute **chaque jour vers 6 h 30 et 14 h 30** : il relit laforet.com/montauban, régénère les données et republie. Suivi : onglet *Actions* du dépôt ; lancement immédiat : *Run workflow*.
- Si le site laforet.com est indisponible ou renvoie trop peu d'annonces, **rien n'est publié** : la version de la veille reste affichée.
- GitHub désactive les tâches planifiées d'un dépôt public inactif depuis 60 jours ; le workflow enregistre `data.json` chaque jour pour rester actif. Si un e-mail GitHub signale la désactivation, cliquer sur *Enable workflow*.
- `mettre_a_jour.bat` reste disponible pour lancer une mise à jour depuis le PC (optionnel).

## Instagram
Ajouter les visuels dans le dossier `instagram/` du dépôt : GitHub → dossier `instagram` → *Add file → Upload files* (jpg / png, idéalement 4:5 ou carré). La publication se relance automatiquement ; les 4 plus récents sont affichés. Depuis le PC : déposer dans le dossier local `instagram/` puis lancer `mettre_a_jour.bat`. Instagram interdit la récupération automatique sans l'API officielle (compte pro + Facebook + jeton).

## Plan B (si URL Launcher est absent ou instable)
`URL Launcher Settings → Install from USB Device` : copier le contenu de `public/` sur une clé USB. Même rendu, hors ligne ; la mise à jour se fait alors en changeant la clé.

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
