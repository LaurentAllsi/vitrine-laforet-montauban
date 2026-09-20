#!/usr/bin/env python
"""
Génère les données de la présentation de vitrine Laforêt Montauban.

  python generer.py

- lit les annonces à vendre / à louer sur laforet.com/montauban
- télécharge photos, DPE et crée les QR codes dans public/img/
- copie les visuels déposés dans le dossier instagram/ (si présents)
- écrit public/data.json, lu par public/index.html (le lecteur qui tourne sur l'écran)

Dépendance : pip install segno pillow
"""
import html
import json
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

import segno
from PIL import Image

ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT / "public"
IMG = PUBLIC / "img"
INSTA_DIR = ROOT / "instagram"

SITE = "https://www.laforet.com"
AGENCE = SITE + "/agence-immobiliere/montauban"
INSTAGRAM_URL = "https://www.instagram.com/laforetmontauban/"
GOOGLE_AVIS_QR = PUBLIC / "img" / "brand" / "qr-avis-google.png"   # versionné dans le dépôt (le cloud n'a pas accès à OneDrive)

POOL = 6            # annonces gardées par catégorie (3 affichées par cycle, on tourne dans le lot)
MAX_PHOTOS = 3      # photos par annonce
INSTA_MAX = 4

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9",
}


def get(url, binary=False, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=40) as r:
                data = r.read()
                return (data, r.headers.get("Content-Type", "")) if binary else data.decode("utf-8", "replace")
        except Exception as e:  # noqa: BLE001
            if i == retries - 1:
                raise
            time.sleep(2 * (i + 1))


def to_text(fragment):
    fragment = re.sub(r"<(script|style|svg)[^>]*>.*?</\1>", "", fragment, flags=re.S)
    fragment = re.sub(r"<br\s*/?>|</p>|</li>|</h\d>|</div>", "\n", fragment)
    fragment = re.sub(r"<[^>]+>", " ", fragment)
    fragment = html.unescape(fragment)
    fragment = re.sub(r"[ \t ]+", " ", fragment)
    fragment = "\n".join(line.strip() for line in fragment.split("\n"))
    return re.sub(r"\n\s*\n+", "\n", fragment).strip()


def clean_num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


# ----------------------------------------------------------------------------- liste
def parse_list(page_html, kind):
    items = []
    for art in re.findall(r"<article.*?</article>", page_html, re.S):
        m = re.search(r'data-hover-detail-value="\{&quot;id&quot;:(\d+)', art)
        if not m:
            continue  # squelettes de chargement
        pid = m.group(1)
        g = lambda k: (re.search(r'data-gtm-item-%s-param="([^"]*)"' % k, art) or [None, ""])[1]
        link = re.search(r'href="(https://www\.laforet\.com[^"]*-%s)"' % pid, art)
        txt = to_text(art)
        items.append({
            "id": pid,
            "kind": kind,
            "url": link.group(1) if link else "",
            "type": html.unescape(g("type")),
            "city": html.unescape(g("city")).title(),
            "zip": g("zipcode"),
            "price": clean_num(g("price")),
            "surface": clean_num(g("size")),
            "rooms": g("rooms-nb"),
            "criteria": html.unescape(g("criteria")),
            "new": "Nouveauté" in txt,
            "exclusive": "Favoriz" in art,
            "features": [f for f, k in (
                ("Ascenseur", "ascenseur"), ("Piscine", "piscine"), ("Balcon", "balcon"),
                ("Parking", "parking"), ("Garage", "garage"), ("Cheminée", "cheminee"),
                ("Cave", "cave"), ("Meublé", "meuble"),
            ) if g(k) == "true"],
        })
    return items


def scrape_list(kind):
    path = "acheter" if kind == "vente" else "louer"
    items, seen, total = [], set(), None
    for page in range(1, 8):
        url = f"{AGENCE}/{path}" + (f"?page={page}" if page > 1 else "")
        h = get(url)
        if total is None:
            m = re.search(r"(\d+)\s+(?:biens|annonces)", to_text(h))
            total = int(m.group(1)) if m else None
        new = [i for i in parse_list(h, kind) if i["id"] not in seen]
        if not new:
            break
        for i in new:
            seen.add(i["id"])
        items += new
        if total and len(items) >= total:
            break
    return items, total or len(items)


# ----------------------------------------------------------------------------- détail
def fmt_eur(x):
    return f"{x:,.0f}".replace(",", " ") + " €"


def enrich(item):
    h = get(item["url"])
    og = re.findall(r'<meta property="og:image(?:_\d+)?" content="([^"]+)"', h)
    photos = list(dict.fromkeys(og))[:MAX_PHOTOS]
    item["photo_urls"] = photos

    # description : première ligne = accroche (quartier), ensuite le texte
    txt = to_text(h)
    start = txt.rfind("\nDescription\n")  # la 1re occurrence est le menu de navigation
    m = re.search(r"\nDescription\n(.*?)(?:\nHonoraires à la charge|\nDisponible|\nLoyer hors charges|show#toggle)", txt[start:], re.S) if start >= 0 else None
    desc = m.group(1).strip() if m else ""
    lines = [l.strip() for l in desc.split("\n") if l.strip()]
    accroche, resume = "", ""
    if lines:
        first = re.sub(r"^\w[\w\- ]*\s*\?\s*", "", lines[0]).strip()  # "Montauban ? Quartier …"
        if len(lines) > 1 and len(first) <= 70:
            accroche, rest = first, " ".join(lines[1:])
        else:
            rest = " ".join(lines)
        resume = rest
        if len(resume) > 190:
            cut = resume[:190].rsplit(" ", 1)[0]
            resume = cut.rstrip(",;:-") + "…"
    item["accroche"] = accroche
    item["resume"] = resume

    # détails complémentaires
    flat = re.sub(r"\s+", " ", txt)
    if item["kind"] == "vente":
        fee = re.search(r"Honoraires à la charge (?:du vendeur|de l['’]acquéreur[^.]{0,80})", flat)
        item["honoraires"] = fee.group(0) if fee else "Honoraires à la charge du vendeur"
        terrain = re.search(r"Surf\. terrain : ([\d\s,\.]+) m²", flat)
        item["terrain"] = terrain.group(1).strip() if terrain else ""
    else:
        hc = re.search(r"Loyer hors charges ([\d\s,\.]+) € par mois, provision charges ([\d\s,\.]+) €", flat)
        dg = re.search(r"Dépôt de garantie : ([\d\s,\.]+) €", flat)
        hon = re.search(r"Honoraires TTC charge locataire : ([^*]*?TTC)", flat)
        item["loyer_hc"] = hc.group(1).strip() if hc else ""
        item["charges"] = hc.group(2).strip() if hc else ""
        item["depot"] = dg.group(1).strip() if dg else ""
        item["honoraires"] = ("Honoraires locataire : " + hon.group(1).strip()) if hon else ""
        dispo = re.search(r"Disponible(?: le)? ?([\d/]*)", flat)
        item["dispo"] = ""
    # DPE (image servie par le site)
    item["dpe_url"] = f"{SITE}/ajax/properties/{item['id']}/dpe"
    return item


def download(url, dest, min_bytes=1500):
    data, ctype = get(url, binary=True)
    if len(data) < min_bytes:
        raise ValueError("fichier trop petit")
    dest.write_bytes(data)
    return ctype


def shrink(path, max_side=1400):
    """Allège les photos (l'écran n'a pas besoin de plus, la mémoire du lecteur est limitée)."""
    im = Image.open(path).convert("RGB")
    im.thumbnail((max_side, max_side))
    im.save(path, "JPEG" if path.suffix == ".jpg" else "PNG", quality=82, optimize=True)


def make_qr(url, dest_svg):
    qr = segno.make(url, error="m", micro=False)
    qr.save(str(dest_svg), scale=10, border=1, dark="#153D8A", light="#FFFFFF", xmldecl=False, svgns=True)


def build_item(item):
    d = IMG / item["id"]
    d.mkdir(parents=True, exist_ok=True)
    photos = []
    for n, u in enumerate(item.pop("photo_urls")):
        try:
            ext = ".png" if u.lower().endswith(".png") else ".jpg"
            download(u, d / f"photo{n}{ext}", min_bytes=5000)
            shrink(d / f"photo{n}{ext}")
            photos.append(f"img/{item['id']}/photo{n}{ext}")
        except Exception as e:  # noqa: BLE001
            print(f"   ! photo {u}: {e}")
    item["photos"] = photos
    dpe_url = item.pop("dpe_url")
    try:
        ctype = download(dpe_url, d / "dpe.bin")
        ext = ".svg" if "svg" in ctype else ".png" if "png" in ctype else ".jpg" if "jp" in ctype else ".png"
        (d / "dpe.bin").replace(d / f"dpe{ext}")
        item["dpe"] = f"img/{item['id']}/dpe{ext}"
    except Exception as e:  # noqa: BLE001
        print(f"   ! dpe {item['id']}: {e}")
        item["dpe"] = ""
    make_qr(item["url"], d / "qr.svg")
    item["qr"] = f"img/{item['id']}/qr.svg"
    return item


def rank(items):
    return sorted(items, key=lambda i: (i["new"], i["exclusive"], int(i["id"])), reverse=True)


# ----------------------------------------------------------------------------- agence
AGENCY = {
    "address": "15 allée de l’Empereur, 82000 Montauban",
    "phone": "05 63 91 76 26",
    "email": "montauban@laforet.com",
    "web": "laforet.com/montauban",
    "parking": "Parkings Griffoul, Occitan ou Cathédrale à proximité",
}
DAYS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]


def scrape_hours():
    """Horaires lus sur la page de l'agence ; en cas d'échec, les derniers connus."""
    fallback = [{"day": d, "slots": [["09:00", "12:00"], ["14:00", "19:00"]] if d != "Dimanche" else []} for d in DAYS]
    fallback[5]["slots"][1][1] = "18:00"
    try:
        flat = re.sub(r"\s+", " ", to_text(get(AGENCE)))
        out = []
        for i, d in enumerate(DAYS):
            nxt = DAYS[i + 1] if i + 1 < len(DAYS) else "Métiers"
            m = re.search(r"%s (.*?) %s" % (d, nxt), flat)
            seg = m.group(1) if m else ""
            slots = [[a, b] for a, b in re.findall(r"(\d{2}:\d{2}) - (\d{2}:\d{2})", seg)]
            out.append({"day": d, "slots": slots})
        if sum(len(x["slots"]) for x in out) >= 8:
            return out
    except Exception as e:  # noqa: BLE001
        print("   ! horaires:", e)
    return fallback


# ----------------------------------------------------------------------------- instagram
def added_at(f):
    """Date d'ajout d'un visuel : dernier commit git (fiable dans le cloud, où tous les fichiers
    ont la même date de fichier) ; à défaut la date du fichier (dossier local pas encore publié)."""
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%ct", "--", str(f)], cwd=ROOT,
                             capture_output=True, text=True, timeout=20).stdout.strip()
        if out:
            return int(out)
    except Exception:  # noqa: BLE001
        pass
    return int(f.stat().st_mtime)


def collect_instagram():
    out = []
    dest = IMG / "insta"
    dest.mkdir(parents=True, exist_ok=True)
    for old in dest.iterdir():  # fichier par fichier : OneDrive verrouille parfois les dossiers
        try:
            old.unlink()
        except OSError:
            pass
    if INSTA_DIR.exists():
        files = [f for f in INSTA_DIR.iterdir() if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")]
        files.sort(key=lambda f: (added_at(f), f.name), reverse=True)   # les plus récemment ajoutés d'abord
        for n, f in enumerate(files[:INSTA_MAX]):
            shutil.copy(f, dest / f"{n}{f.suffix.lower()}")
            out.append(f"img/insta/{n}{f.suffix.lower()}")
    return out


# ----------------------------------------------------------------------------- main
def main():
    IMG.mkdir(parents=True, exist_ok=True)
    data = {"generated_at": datetime.now().isoformat(timespec="minutes")}

    counts = {}
    for kind in ("vente", "location"):
        key = "vente" if kind == "vente" else "louer"
        print(f"→ liste {kind}…")
        items, total = scrape_list("vente" if kind == "vente" else "location")
        counts[kind] = total
        print(f"   {len(items)} annonces lues (site : {total})")
        pool = rank([i for i in items if i["price"]])[:POOL]
        built = []
        for it in pool:
            try:
                built.append(build_item(enrich(it)))
                print(f"   ✓ {it['id']} {it['type']} {it['price']}")
            except Exception as e:  # noqa: BLE001
                print(f"   ✗ {it['id']}: {e}")
        data[key] = built

    # nettoyage des anciens dossiers d'annonces
    keep = {i["id"] for k in ("vente", "louer") for i in data[k]} | {"insta", "qr", "brand"}
    for d in IMG.iterdir():
        if d.is_dir() and d.name not in keep:
            shutil.rmtree(d, ignore_errors=True)

    data["counts"] = {"vente": counts["vente"], "location": counts["location"]}
    data["agency"] = AGENCY
    data["hours"] = scrape_hours()
    data["insta"] = collect_instagram()

    qrd = IMG / "qr"
    qrd.mkdir(exist_ok=True)
    make_qr(INSTAGRAM_URL, qrd / "instagram.svg")
    make_qr(AGENCE + "/estimer", qrd / "estimer.svg")
    make_qr(AGENCE, qrd / "agence.svg")
    data["qr_avis"] = "img/brand/qr-avis-google.png" if GOOGLE_AVIS_QR.exists() else ""

    (PUBLIC / "data.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n✔ data.json écrit ({len(data['vente'])} vente, {len(data['louer'])} location, {len(data['insta'])} visuels Instagram)")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
