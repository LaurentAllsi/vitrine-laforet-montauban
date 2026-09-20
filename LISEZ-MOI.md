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

### 3. Afficher la vitrine sur l'écran

**L'URL Launcher intégré Samsung ne sait pas afficher une simple page web.** « Install Web App » attend un dossier contenant un `sssp_config.xml` et une application Tizen `.wgt` **signée avec un certificat Samsung** (test réalisé le 19/09/2026 : google.com, neverssl.com et la vitrine donnent tous « impossible de télécharger l'application Web »). Ne pas insister avec cette méthode, ni avec « Install from USB Device » (même paquet requis).

**Solution retenue : l'ancien mini-PC, branché en HDMI**, avec un navigateur en plein écran (mode kiosque) qui ouvre la vitrine. Remis à zéro le 20/09/2026 (Windows 10 Entreprise 2016 LTSB, build 1607) pour repartir sans le logiciel de l'ancien prestataire.

**Important — navigateur.** Le Edge fourni par défaut sur cette version de Windows (« Edge Legacy ») ne comprend pas les couleurs de la vitrine (propriété CSS `var()`, arrivée avec Edge 15 / 2017). Installer l'un des deux, tous les deux gratuits et à jour automatiquement :
- [Microsoft Edge (nouvelle version)](https://www.microsoft.com/edge) — recommandé, déjà pensé pour ce genre d'usage.
- [Google Chrome](https://www.google.com/chrome/)

**Mise en place, dans l'ordre :**

1. **Installer** Edge ou Chrome (lien ci-dessus).
2. **Copier `pc-windows\lancer_vitrine.bat`** (dans ce dépôt) sur le mini-PC. Le plus simple : sur le mini-PC, ouvrir cette adresse dans le navigateur et l'enregistrer :
   `https://raw.githubusercontent.com/LaurentAllsi/vitrine-laforet-montauban/main/pc-windows/lancer_vitrine.bat`
   Ce script ouvre la vitrine en plein écran et **la relance automatiquement si elle se ferme ou plante**.
3. **Le placer dans le dossier de démarrage de Windows** : `Win + R` → taper `shell:startup` → Entrée → coller le fichier `.bat` dans ce dossier.
4. **Orientation portrait** : clic droit sur le bureau → *Paramètres d'affichage* → *Orientation* → **Portrait**. Si l'écran affiche alors la vitrine couchée, modifier plutôt l'adresse dans `lancer_vitrine.bat` (ajouter `?rot=90` ou `?rot=-90` juste après `.github.io/`) et remettre l'orientation Windows en Paysage.
5. **Empêcher la mise en veille** : *Paramètres → Système → Alimentation et mise en veille* → écran et veille sur **Jamais**.
6. **Connexion automatique au démarrage** (pour repartir seul après une coupure de courant) : `Win + R` → `netplwiz` → décocher *« Les utilisateurs doivent entrer un nom et un mot de passe »* → OK → saisir le mot de passe du compte une fois.
7. **Redémarrer le PC** pour tout vérifier d'un coup : il doit arriver directement sur la vitrine, sans écran de connexion ni fenêtre visible.

### Maintenance du mini-PC

**Arrêter la vitrine pour reprendre la main.** Le script relance le navigateur tant qu'il tourne : il faut arrêter le script *et* le navigateur en même temps. `Win + R`, puis :
```
taskkill /f /im cmd.exe /im msedge.exe
```
(si `Win + R` ne répond pas : `Ctrl + Alt + Suppr` → Gestionnaire des tâches → *Fichier → Exécuter une nouvelle tâche* → même commande). Pour un arrêt définitif, supprimer `lancer_vitrine.bat` de `shell:startup`. Pour relancer sans redémarrer : double-clic sur le fichier.

**Supprimer la bulle « Traduire cette page ? »** (Edge, une seule fois). Invite de commandes **en administrateur** (menu Démarrer → taper `cmd` → clic droit → *Exécuter en tant qu'administrateur*) :
```
reg add "HKLM\SOFTWARE\Policies\Microsoft\Edge" /v TranslateEnabled /t REG_DWORD /d 0 /f
```
puis relancer la vitrine. Contrôle : `edge://policy` doit lister *TranslateEnabled = 0*. Avec Chrome : `HKLM\SOFTWARE\Policies\Google\Chrome`, même valeur.

**Prise en main à distance.** Ne pas utiliser le Bureau à distance de Windows (RDP) : il verrouille la session affichée à l'écran et la vitrine disparaîtrait. Utiliser un outil qui partage la session en cours (RustDesk, Chrome Remote Desktop), installé comme service avec accès sans surveillance et mot de passe fort.

**Solutions de repli**, si ce PC devait être remplacé un jour :
- Un petit lecteur HDMI (Fire TV Stick, Raspberry Pi, mini-PC) avec un navigateur en kiosque — même principe.
- Vidéo / images sur clé USB lues par MagicInfo Lite intégré à l'écran (gratuit, mise à jour manuelle).
- Un service d'affichage dynamique dont le lecteur est déjà signé pour Samsung (abonnement).

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
| `pc-windows/lancer_vitrine.bat` | Lance la vitrine en plein écran sur le mini-PC, avec relance automatique |

Charte : Laforêt 2026 (bleu #153D8A, cyan #009EE3, police Lexend, bulle à pointe bas-gauche).
