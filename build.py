"""
Génère le site du portfolio à partir de l'export Notion.

    python build.py

Lit :
  - site.toml            : page « A propos », menu, couleurs des étiquettes ;
  - donnees/*.csv        : l'export CSV de la base Notion « Portfolio ».
Crée le site dans le dossier _site/ (index.html, style.css, images/, documents/).

Sur GitHub, ce script est lancé automatiquement à chaque modification :
il n'y a normalement pas besoin d'y toucher.
Nécessite Python 3.11 ou plus récent, sans aucune installation.
"""

import csv
import html
import re
import shutil
import sys
import tomllib
import unicodedata
from pathlib import Path
from urllib.parse import unquote

DOSSIER = Path(__file__).parent
SORTIE = DOSSIER / "_site"
PREFIXE_COLLAB = "En collaboration avec"
AFFICHER_THEMES = False
NOM = ""

# Colonnes Notion reconnues (sans tenir compte des majuscules ni des accents).
# Pour renommer une colonne dans Notion, ajoute son nouveau nom ici.
COLONNES = {
    "titre":         ["nom", "titre"],
    "cadre":         ["entreprise", "cadre", "structure"],
    "collaboration": ["collaboration", "collaboration, propriete intellectuelle"],
    "description":   ["description"],
    "methodes":      ["tags", "methodes"],
    "themes":        ["themes", "theme"],
    "categorie":     ["categorie", "categories", "onglet"],
    "images":        ["images", "image"],
    "lien":          ["lien", "url"],
    "texte_lien":    ["texte du lien"],
    "brouillon":     ["brouillon", "masquer"],
    "ordre":         ["ordre"],
}


# ---------------------------------------------------------------
# Outils
# ---------------------------------------------------------------

def simplifier(mot):
    """Minuscules, sans accents ni espaces superflus : « Thèmes » -> « themes »."""
    mot = unicodedata.normalize("NFD", mot.strip().lower())
    return "".join(c for c in mot if unicodedata.category(c) != "Mn")


def identifiant(nom):
    """Nom d'onglet -> id d'ancre : « Comprendre les usages » -> « comprendre-les-usages »."""
    return re.sub(r"[^a-z0-9]+", "-", simplifier(nom)).strip("-")


def liste(valeur):
    """Les cases à choix multiples de Notion sont exportées en « a, b, c »."""
    return [v.strip() for v in (valeur or "").split(",") if v.strip()]


def texte(valeur):
    return html.escape(str(valeur).strip())


def paragraphes(description):
    blocs = [b.strip() for b in description.replace("\r", "").split("\n\n") if b.strip()]
    return "\n".join(f"        <p>{texte(' '.join(b.split()))}</p>" for b in blocs)


# ---------------------------------------------------------------
# Lecture des données
# ---------------------------------------------------------------

def lire_reglages():
    try:
        with open(DOSSIER / "site.toml", "rb") as f:
            return tomllib.load(f)
    except tomllib.TOMLDecodeError as erreur:
        sys.exit(f"Erreur dans site.toml : {erreur}\n"
                 "Vérifie les guillemets autour de cette ligne.")


def trouver_csv():
    fichiers = sorted((DOSSIER / "donnees").glob("*.csv"))
    if not fichiers:
        sys.exit("Aucun fichier CSV dans le dossier donnees/. "
                 "Exporte ta base Notion en CSV et dépose le fichier dans ce dossier.")
    # Notion exporte deux fichiers : « …_all.csv » contient toutes les lignes.
    complets = [f for f in fichiers if f.stem.endswith("_all")]
    choisi = (complets or fichiers)[0]
    if len(complets or fichiers) > 1:
        print(f"Plusieurs CSV trouvés, j'utilise « {choisi.name} ».")
    return choisi


def lire_projets():
    chemin = trouver_csv()
    with open(chemin, encoding="utf-8-sig", newline="") as f:
        lignes = list(csv.DictReader(f))
    if not lignes:
        return []

    # Associe chaque colonne du CSV à un champ connu
    correspondance = {}
    for colonne in lignes[0].keys():
        cle = simplifier(colonne or "")
        for champ, noms in COLONNES.items():
            if cle in noms or (champ == "collaboration" and cle.startswith("collaboration")):
                correspondance[champ] = colonne

    if "titre" not in correspondance:
        sys.exit(f"Colonne « Nom » introuvable dans {chemin.name}.")
    if "categorie" not in correspondance:
        print("Attention : pas de colonne « Catégorie » dans Notion, "
              "tous les projets vont dans le premier onglet.")

    projets = []
    for position, ligne in enumerate(lignes):
        p = {champ: (ligne.get(col) or "").strip() for champ, col in correspondance.items()}
        if not p["titre"]:
            continue
        if simplifier(p.get("brouillon", "")) in ("yes", "oui", "true", "x", "1"):
            continue
        try:
            p["_ordre"] = float(p.get("ordre", "").replace(",", "."))
        except ValueError:
            p["_ordre"] = float("inf")
        p["_position"] = position
        projets.append(p)

    projets.sort(key=lambda p: (p["_ordre"], p["_position"]))
    print(f"{len(projets)} projets lus dans {chemin.name}.")
    return projets


EXTENSIONS_IMAGES = [".jpg", ".jpeg", ".png", ".webp", ".gif"]


def trouver_fichier(chemin, quoi="Le fichier"):
    """Renvoie le chemin du fichier tel qu'il existe dans le dépôt.
    Si « photo.jpg » n'existe pas mais « photo.png » ou « Photo.JPG » oui, on prend celui-là."""
    chemin = chemin.strip().lstrip("/")
    if (DOSSIER / chemin).is_file():
        return chemin
    cible = Path(chemin)
    dossier = DOSSIER / cible.parent
    if dossier.is_dir():
        candidats = [f for f in dossier.iterdir() if f.is_file()]
        for f in candidats:
            if f.name.lower() == cible.name.lower():
                return str(cible.parent / f.name)
        if cible.suffix.lower() in EXTENSIONS_IMAGES:
            for f in candidats:
                if f.stem.lower() == cible.stem.lower() and f.suffix.lower() in EXTENSIONS_IMAGES:
                    return str(cible.parent / f.name)
    print(f"Attention : {quoi} « {chemin} » est introuvable.")
    return chemin


def noms_images(valeur):
    """Accepte « a.jpg, b.jpg » ou les chemins d'une colonne Fichiers de Notion."""
    noms = []
    for morceau in liste(valeur):
        nom = unquote(morceau.split("?")[0]).replace("\\", "/").split("/")[-1].strip()
        if nom:
            noms.append(nom)
    return noms


# ---------------------------------------------------------------
# Construction de la page
# ---------------------------------------------------------------

COULEURS_TAGS = {}


def lien_tag(nom, tag_actif):
    """Une étiquette cliquable qui ouvre la page regroupant les projets de ce tag."""
    actif = " actif" if tag_actif and identifiant(nom) == identifiant(tag_actif) else ""
    couleur = COULEURS_TAGS.get(identifiant(nom))
    style = f' style="--couleur-tag: {texte(couleur)}"' if couleur else ""
    return f'<a class="tag{actif}"{style} href="#tag-{identifiant(nom)}">{texte(nom)}</a>'


def etiquettes_de(p):
    """Les étiquettes affichées : colonne Tags, et thèmes si afficher_themes = true."""
    tags = liste(p.get("methodes"))
    if AFFICHER_THEMES:
        tags = liste(p.get("themes")) + tags
    return tags


def titre_complet(p):
    """« Titre - Cadre », comme sur la maquette."""
    titre, cadre = p["titre"].strip(), p.get("cadre", "").strip()
    if cadre and not titre.endswith(cadre):
        return f"{titre} - {cadre}"
    return titre


def bloc_projet(p, tag_actif=None):
    m = [f"        <h3>{texte(titre_complet(p))}</h3>"]

    etiquettes = [lien_tag(t, tag_actif) for t in etiquettes_de(p)]
    if etiquettes:
        m.append(f'        <div class="tags">{"".join(etiquettes)}</div>')

    if p.get("description"):
        m.append(paragraphes(p["description"]))

    if p.get("collaboration"):
        m.append(f'        <p class="collab">{texte(PREFIXE_COLLAB)} {texte(p["collaboration"])}</p>')

    if p.get("lien"):
        libelle = p.get("texte_lien") or "Voir le projet"
        m.append(f'        <p><a class="lien" href="{texte(p["lien"])}" target="_blank">{texte(libelle)} →</a></p>')

    images = noms_images(p.get("images"))
    if images:
        lignes = []
        for nom in images:
            chemin = texte(trouver_fichier("images/" + nom, f"l'image du projet « {p['titre']} »,"))
            lignes.append(f'          <a href="{chemin}" target="_blank">'
                          f'<img src="{chemin}" alt="{texte(p["titre"])}" loading="lazy"></a>')
        m.append('        <div class="images">\n' + "\n".join(lignes) + "\n        </div>")

    return '      <article class="projet">\n' + "\n".join(m) + "\n      </article>"


def section_a_propos(ap):
    """La page « A propos », sur fond bleu."""
    if not ap:
        return ""
    contact = [f'<p class="contact-nom">{texte(NOM)}</p>']
    if ap.get("telephone"):
        contact.append(f"<p>{texte(ap['telephone'])}</p>")
    if ap.get("email"):
        e = texte(ap["email"])
        contact.append(f'<p><a href="mailto:{e}">{e}</a></p>')
    if ap.get("linkedin"):
        l = texte(ap["linkedin"])
        contact.append(f'<p><a href="{l}" target="_blank">{l}</a></p>')
    if ap.get("cv"):
        cv = texte(trouver_fichier(ap["cv"], "le CV"))
        contact.append(f'<p class="lien-cv"><a href="{cv}" target="_blank">Voir mon CV</a></p>')

    photo = ""
    if ap.get("photo"):
        src = texte(trouver_fichier(ap["photo"], "la photo"))
        photo = f'<img class="photo" src="{src}" alt="{texte(NOM)}">'

    return f"""<section class="theme a-propos" id="a-propos">
  <div class="conteneur">
    <h2>{texte(ap.get('titre', ap.get('onglet', 'A propos')))}</h2>
    <div class="carte-visite">
      {photo}
      <div class="contact">
        {(chr(10) + '        ').join(contact)}
      </div>
    </div>
    <div class="texte-a-propos">
{paragraphes(ap.get('texte', ''))}
    </div>
  </div>
</section>"""


def section_accueil(acc):
    """La page d'accueil : la photo de couverture et sa légende."""
    if not acc or not acc.get("image"):
        return ""
    src = texte(trouver_fichier(acc["image"], "l'image de couverture"))
    legende = f'\n    <p class="legende-accueil">{texte(acc["legende"])}</p>' if acc.get("legende") else ""
    return f"""<section class="theme accueil" id="accueil">
  <div class="conteneur couverture">
    <img src="{src}" alt="{texte(acc.get('legende', NOM))}">{legende}
  </div>
</section>"""


def construire_page(reglages, projets):
    global PREFIXE_COLLAB, AFFICHER_THEMES, NOM
    site = reglages["site"]
    ap = reglages.get("a_propos", {})
    NOM = site.get("nom", "")
    PREFIXE_COLLAB = site.get("texte_collaboration", "En collaboration avec")
    etiquettes = reglages.get("etiquettes", {})
    AFFICHER_THEMES = bool(etiquettes.get("afficher_themes", False))
    COULEURS_TAGS.update({identifiant(k): v for k, v in etiquettes.get("couleurs", {}).items()})

    categories = reglages.get("categorie", [])
    noms = [c["nom"] for c in categories]
    premier = noms[0] if noms else ""

    for p in projets:
        for c in liste(p.get("categorie")):
            if c not in noms:
                print(f"Attention : la catégorie « {c} » (projet « {p['titre']} ») "
                      f"n'est pas dans site.toml, le projet n'est affiché dans aucune page. "
                      f"Catégories possibles : {', '.join(noms)}.")

    def categories_de(p):
        return liste(p.get("categorie")) or [premier]

    # Menu : « A propos » puis les catégories
    menu = []
    if ap:
        menu.append(f'      <a href="#a-propos">{texte(ap.get("onglet", "A propos"))}</a>')
    menu += [f'      <a href="#{identifiant(c["nom"])}">{texte(c.get("onglet", c["nom"]))}</a>'
             for c in categories]

    accueil = section_accueil(reglages.get("accueil", {}))
    sections = [s for s in (accueil, section_a_propos(ap)) if s]
    page_depart = "#accueil" if accueil else "#a-propos"
    for c in categories:
        blocs = [bloc_projet(p) for p in projets if c["nom"] in categories_de(p)]
        sections.append(f"""<section class="theme" id="{identifiant(c['nom'])}">
  <div class="conteneur">
    <h2>{texte(c.get('titre', c['nom']))}</h2>
    <div class="projets">

{chr(10).join(blocs)}

    </div>
  </div>
</section>""")

    # Une page par étiquette : tous les projets qui la portent, quelle que soit
    # leur catégorie. Elle s'ouvre en cliquant sur l'étiquette.
    tags = {}
    for p in projets:
        for t in etiquettes_de(p):
            tags.setdefault(identifiant(t), t)
    for slug, nom in sorted(tags.items()):
        concernes = [p for p in projets if slug in [identifiant(t) for t in etiquettes_de(p)]]
        blocs = [bloc_projet(p, tag_actif=nom) for p in concernes]
        nombre = f"{len(concernes)} projet" + ("s" if len(concernes) > 1 else "")
        sections.append(f"""<section class="theme page-tag" id="tag-{slug}">
  <div class="conteneur">
    <p class="retour"><a href="#" onclick="history.back(); return false;">← Retour</a></p>
    <h2>{texte(nom)}</h2>
    <p class="compte">{nombre}</p>
    <div class="projets">

{chr(10).join(blocs)}

    </div>
  </div>
</section>""")

    description = texte(" ".join(ap.get("texte", "").split())[:300])
    email = texte(ap.get("email", ""))
    pied = texte(NOM) + (f' · <a href="mailto:{email}">{email}</a>' if email else "")

    return f"""<!DOCTYPE html>
<!-- Page générée automatiquement par build.py à partir de Notion : ne pas modifier à la main. -->
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{texte(site.get('titre', NOM or 'Portfolio'))}</title>
  <meta name="description" content="{description}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Open+Sans:ital,wght@0,400;0,600;0,700;0,800;1,400;1,600;1,700;1,800&display=swap">
  <link rel="stylesheet" href="style.css">
</head>
<body>

<header class="entete">
  <div class="conteneur">
    <a class="nom" href="{page_depart}">{texte(NOM)}</a>
    <nav class="menu">
{chr(10).join(menu)}
    </nav>
  </div>
</header>

<main>

{(chr(10) * 2).join(sections)}

</main>

<footer>
  <div class="conteneur">
    {pied}
  </div>
</footer>

<script>
  // Souligne l'élément du menu correspondant à la page ouverte
  function marquerMenu() {{
    var liens = document.querySelectorAll('.menu a');
    var actif = location.hash || '{page_depart}';
    liens.forEach(function (lien) {{
      lien.classList.toggle('actif', lien.getAttribute('href') === actif);
    }});
  }}
  // Chaque page s'ouvre en haut, menu visible
  window.addEventListener('hashchange', function () {{
    marquerMenu();
    window.scrollTo(0, 0);
  }});
  marquerMenu();
  if (location.hash) window.addEventListener('load', function () {{ window.scrollTo(0, 0); }});
</script>

</body>
</html>
"""


def main():
    reglages = lire_reglages()
    projets = lire_projets()
    page = construire_page(reglages, projets)

    if SORTIE.exists():
        shutil.rmtree(SORTIE)
    SORTIE.mkdir()
    (SORTIE / "index.html").write_text(page, encoding="utf-8")
    shutil.copy(DOSSIER / "style.css", SORTIE / "style.css")
    shutil.copytree(DOSSIER / "images", SORTIE / "images")
    if (DOSSIER / "documents").exists():
        shutil.copytree(DOSSIER / "documents", SORTIE / "documents")
    print(f"Site généré dans {SORTIE.name}/.")


if __name__ == "__main__":
    main()
