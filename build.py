"""
Génère le site du portfolio à partir de l'export Notion.

    python build.py

Lit :
  - site.toml            : accueil, page « A propos », menu, couleurs des étiquettes ;
  - donnees/*.csv        : l'export CSV de la base Notion « Portfolio » ;
  - donnees/**/*.md      : le texte écrit dans chaque page de projet Notion (facultatif).
Crée le site dans le dossier _site/.

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
    "resume":        ["resume", "resume court", "accroche"],
    "annee":         ["annee", "date", "periode"],
    "mosaique":      ["mosaique", "photo mosaique", "photos mosaique", "photo d'accueil"],
    "une":           ["a la une", "une", "mis en avant", "en avant"],
    "type":          ["type", "nature", "type de projet"],
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
              "les filtres de la page Projets seront vides.")

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
# Pages détaillées : textes écrits dans les pages Notion
# ---------------------------------------------------------------
# L'export « Markdown & CSV » de Notion contient, à côté du CSV, un fichier .md
# par projet avec le texte écrit dans la page du projet. On les cherche dans
# tout le dossier donnees/ et on les associe aux projets par leur titre.

ID_NOTION = re.compile(r"\s+[0-9a-f]{32}$")
PROPRIETE = re.compile(r"^[^:\n]{1,60}:\s")


def lire_pages_notion():
    pages = {}
    for f in sorted((DOSSIER / "donnees").rglob("*.md")):
        lignes = f.read_text(encoding="utf-8-sig").replace("\r", "").split("\n")
        titre = ID_NOTION.sub("", f.stem)
        # Première ligne « # Titre »
        if lignes and lignes[0].startswith("# "):
            titre = lignes[0][2:].strip()
            lignes = lignes[1:]
        while lignes and not lignes[0].strip():
            lignes = lignes[1:]
        # Notion recopie ensuite les propriétés (« Tags: … ») : on les saute
        if lignes and PROPRIETE.match(lignes[0]):
            while lignes and lignes[0].strip():
                lignes = lignes[1:]
        corps = "\n".join(lignes).strip()
        if not corps:
            continue
        cle = identifiant(titre)
        # Un fichier exporté par Notion (avec son identifiant) passe avant un brouillon
        if cle in pages and not ID_NOTION.search(f.stem):
            continue
        pages[cle] = (corps, f)
    return pages


MEDIAS = {}   # fichiers d'images trouvés à côté des pages Notion -> chemin publié


def resoudre_image(src, fichier_md):
    """Image d'une page Notion : à côté du fichier .md, ou dans images/."""
    if re.match(r"^https?://", src):
        return src
    src = unquote(src.split("?")[0])
    voisin = (fichier_md.parent / src)
    if voisin.is_file():
        publie = f"medias/{identifiant(fichier_md.stem)}/{voisin.name}"
        MEDIAS[publie] = voisin
        return publie
    return trouver_fichier("images/" + Path(src).name, "une image de page")


def en_ligne(t, fichier_md):
    """Gras, italique et liens à l'intérieur d'une ligne."""
    t = texte(t)
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)",
               lambda m: f'<a href="{m.group(2)}" target="_blank">{m.group(1)}</a>', t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])[*_](?!\s)(.+?)(?<!\s)[*_](?![\w*])", r"<em>\1</em>", t)
    return t


def markdown_vers_html(corps, fichier_md):
    """Convertit le texte d'une page Notion (titres, paragraphes, listes, images)."""
    sortie, paragraphe, liste_ouverte = [], [], None

    def fermer():
        nonlocal paragraphe, liste_ouverte
        if paragraphe:
            sortie.append(f"<p>{en_ligne(' '.join(paragraphe), fichier_md)}</p>")
            paragraphe = []
        if liste_ouverte:
            sortie.append(f"</{liste_ouverte}>")
            liste_ouverte = None

    for ligne in corps.split("\n"):
        brut = ligne.strip()
        image = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", brut)
        puce = re.match(r"^[-*+]\s+(.*)$", brut)
        numero = re.match(r"^\d+[.)]\s+(.*)$", brut)
        titre = re.match(r"^(#{1,6})\s+(.*)$", brut)
        if not brut:
            fermer()
        elif titre:
            fermer()
            sortie.append(f"<h3>{en_ligne(titre.group(2), fichier_md)}</h3>")
        elif image:
            fermer()
            src = texte(resoudre_image(image.group(2), fichier_md))
            alt = texte(image.group(1))
            sortie.append(f'<figure><a href="{src}" target="_blank"><img src="{src}" alt="{alt}" loading="lazy"></a>'
                          + (f"<figcaption>{alt}</figcaption>" if alt and not alt.lower().endswith(tuple(EXTENSIONS_IMAGES)) else "")
                          + "</figure>")
        elif puce or numero:
            balise = "ul" if puce else "ol"
            if paragraphe:
                sortie.append(f"<p>{en_ligne(' '.join(paragraphe), fichier_md)}</p>")
                paragraphe = []
            if liste_ouverte != balise:
                if liste_ouverte:
                    sortie.append(f"</{liste_ouverte}>")
                sortie.append(f"<{balise}>")
                liste_ouverte = balise
            sortie.append(f"<li>{en_ligne((puce or numero).group(1), fichier_md)}</li>")
        else:
            if liste_ouverte:
                sortie.append(f"</{liste_ouverte}>")
                liste_ouverte = None
            paragraphe.append(brut)
    fermer()
    return "\n".join(sortie)


# ---------------------------------------------------------------
# Construction de la page
# ---------------------------------------------------------------

COULEURS_TAGS = {}


def lien_tag(nom, tag_actif=None):
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


def bloc_tags(p, tag_actif=None):
    tags = [lien_tag(t, tag_actif) for t in etiquettes_de(p)]
    return f'<div class="tags">{"".join(tags)}</div>' if tags else ""


def sous_titre(p):
    """« EPFL · 2024 »"""
    morceaux = [p.get("cadre", ""), p.get("annee", "")]
    return ", ".join(texte(m) for m in morceaux if m.strip())


def resume(p):
    """La phrase de la carte : colonne Résumé, sinon la première phrase de la description."""
    if p.get("resume"):
        return p["resume"]
    desc = " ".join(p.get("description", "").split())
    phrase = re.split(r"(?<=[.!?])\s", desc, maxsplit=1)[0]
    return phrase if len(phrase) <= 220 else phrase[:217].rsplit(" ", 1)[0] + "…"


def images_de(p):
    return [trouver_fichier("images/" + nom, f"l'image du projet « {p['titre']} »,")
            for nom in noms_images(p.get("images"))]


def ancre(p):
    return "projet-" + identifiant(p["titre"])


def meta(p):
    """Ligne sous le titre : type de projet (en couleur), cadre et année."""
    morceaux = []
    if p.get("type"):
        morceaux.append(f'<span class="type">{texte(p["type"])}</span>')
    st = sous_titre(p)
    if st:
        morceaux.append(st)
    return f'<p class="meta">{" ".join(morceaux)}</p>' if morceaux else ""


def est_a_la_une(p):
    return simplifier(p.get("une", "")) in ("yes", "oui", "true", "x", "1")


def carte_projet(p, tag_actif=None, grande=False):
    """La carte d'un projet dans une page de catégorie ou d'étiquette."""
    images = images_de(p)
    image = (f'<div class="carte-image"><img src="{texte(images[0])}" alt="" loading="lazy"></div>'
             if images else '')
    st = sous_titre(p)
    return f"""      <article class="carte{' grande' if grande else ''}">
        <a class="carte-lien" href="#{ancre(p)}">
          {image}
          <h3>{texte(p['titre'])}</h3>
          {meta(p)}
          <p class="resume">{texte(resume(p))}</p>
        </a>
        {bloc_tags(p, tag_actif)}
      </article>"""


def page_projet(p, pages):
    """La page détaillée d'un projet."""
    corps = pages.get(identifiant(p["titre"]))
    if corps:
        texte_page = markdown_vers_html(*corps)
    else:
        texte_page = paragraphes(p.get("description", ""))

    extra = []
    if p.get("collaboration"):
        extra.append(f'<p class="collab">{texte(PREFIXE_COLLAB)} {texte(p["collaboration"])}</p>')
    if p.get("lien"):
        libelle = p.get("texte_lien") or "Voir le projet"
        extra.append(f'<p><a class="lien" href="{texte(p["lien"])}" target="_blank">{texte(libelle)} →</a></p>')

    images = "\n".join(
        f'        <a href="{texte(i)}" target="_blank"><img src="{texte(i)}" alt="{texte(p["titre"])}" loading="lazy"></a>'
        for i in images_de(p))
    st = sous_titre(p)
    return f"""<section class="theme page-projet" id="{ancre(p)}">
  <div class="conteneur">
    <p class="retour"><a href="#" onclick="history.back(); return false;">← Retour</a></p>
    <h2>{texte(p['titre'])}</h2>
    {meta(p)}
    {bloc_tags(p)}
    <div class="detail">
      <div class="detail-texte">
{texte_page}
{chr(10).join(extra)}
      </div>
      <div class="detail-images">
{images}
      </div>
    </div>
  </div>
</section>"""


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
        contact.append(f'<p class="reseaux"><a class="icone" href="{l}" target="_blank" '
                       f'aria-label="Profil LinkedIn" title="LinkedIn"><i class="fa-brands fa-linkedin"></i></a></p>')
    if ap.get("cv"):
        cv = texte(trouver_fichier(ap["cv"], "le CV"))
        contact.append(f'<p class="lien-cv"><a href="{cv}" target="_blank">Voir mon CV</a></p>')

    photo = ""
    if ap.get("photo"):
        src = texte(trouver_fichier(ap["photo"], "la photo"))
        photo = f'<img class="photo" src="{src}" alt="{texte(NOM)}">'

    return f"""<section class="theme a-propos" id="a-propos">
  <div class="conteneur colonnes-a-propos">
    <div>
      <h2>{texte(ap.get('titre', ap.get('onglet', 'A propos')))}</h2>
      <div class="carte-visite">
        {photo}
        <div class="contact">
          {(chr(10) + '          ').join(contact)}
        </div>
      </div>
      <div class="texte-a-propos">
{paragraphes(ap.get('texte', ''))}
      </div>
    </div>
{bulles_thematiques(ap.get('thematiques', []))}
  </div>
</section>"""


# Positions des bulles (en % de la largeur) : un nuage en zigzag, comme sur la maquette
POSITIONS_BULLES = [34, 60, 8, 52, 0, 30, 62, 14, 46, 4]


def bulles_thematiques(thematiques):
    """Le schéma de bulles avec les thématiques, à droite de la page « A propos »."""
    if not thematiques:
        return ""
    pas = 94   # écart vertical entre deux bulles, en pixels
    bulles = []
    for i, nom in enumerate(thematiques):
        gauche = POSITIONS_BULLES[i % len(POSITIONS_BULLES)]
        bulles.append(f'      <li class="bulle" style="--x: {gauche}%; --y: {i * pas}px">'
                      f'<span>{texte(nom)}</span></li>')
    hauteur = (len(thematiques) - 1) * pas + 140
    return (f'    <ul class="thematiques" style="--hauteur: {hauteur}px" aria-label="Mes thématiques">\n'
            + "\n".join(bulles) + "\n    </ul>")


def section_accueil(acc, projets):
    """La page d'accueil : la mosaïque de photos (ou une image unique) et sa légende."""
    if not acc:
        return ""
    legende = f'\n    <p class="legende-accueil">{texte(acc["legende"])}</p>' if acc.get("legende") else ""
    mosaique = acc.get("mosaique", [])

    if mosaique:
        par_nom = {identifiant(p["titre"]): p for p in projets}
        # Colonne « Mosaïque » de Notion : les photos de l'accueil qui mènent à ce projet
        par_photo = {}
        for p in projets:
            for nom in noms_images(p.get("mosaique")):
                par_photo[Path(nom).stem.lower()] = p
        tuiles = []
        for i, photo in enumerate(mosaique):
            src = texte(trouver_fichier(photo.get("image", ""), "une photo de la mosaïque"))
            nom_projet = photo.get("projet", "")
            p = par_nom.get(identifiant(nom_projet)) if nom_projet else None
            if not nom_projet:
                p = par_photo.get(Path(photo.get("image", "")).stem.lower())
            if nom_projet and not p:
                print(f"Attention : le projet « {nom_projet} » de la mosaïque est introuvable, "
                      f"la photo mène à la page Projets.")
            lien = f"#{ancre(p)}" if p else "#projets"
            titre = p["titre"] if p else "Voir les projets"
            alt = texte(photo.get("description", ""))
            tuiles.append(f'      <a class="tuile" href="{lien}" title="{texte(titre)}" style="--i: {i}">'
                          f'<img src="{src}" alt="{alt}"></a>')
        visuel = '    <div class="mosaique">\n' + "\n".join(tuiles) + "\n    </div>"
    elif acc.get("image"):
        src = texte(trouver_fichier(acc["image"], "l'image de couverture"))
        visuel = f'    <img class="image-couverture" src="{src}" alt="{texte(acc.get("legende", NOM))}">'
    else:
        return ""

    return f"""<section class="theme accueil" id="accueil">
  <div class="conteneur couverture">
{visuel}{legende}
  </div>
</section>"""


def grille(cartes):
    return f"""    <div class="projets">

{chr(10).join(cartes)}

    </div>"""


def construire_page(reglages, projets, pages):
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
                      f"n'est pas dans site.toml : le projet est dans « Tous » mais dans aucun filtre. "
                      f"Catégories possibles : {', '.join(noms)}.")

    def categories_de(p):
        return liste(p.get("categorie"))

    reglages_projets = reglages.get("projets", {})
    titre_projets = reglages_projets.get("titre", "Projets")

    accueil = section_accueil(reglages.get("accueil", {}), projets)
    sections = [s for s in (accueil, section_a_propos(ap)) if s]
    page_depart = "#accueil" if accueil else "#projets"

    # Menu : Accueil, Projets, A propos, CV
    menu = []
    if accueil:
        menu.append(f'      <a href="#accueil">{texte(reglages.get("accueil", {}).get("onglet", "Accueil"))}</a>')
    menu.append(f'      <a href="#projets">{texte(titre_projets)}</a>')
    if ap:
        menu.append(f'      <a href="#a-propos">{texte(ap.get("onglet", "A propos"))}</a>')
    if ap.get("cv") and reglages_projets.get("cv_dans_menu", True):
        cv = texte(trouver_fichier(ap["cv"], "le CV"))
        menu.append(f'      <a href="{cv}" target="_blank">CV</a>')



    # Page « Projets » : toutes les cartes, et les axes (catégories) comme filtres.
    # Chaque filtre est une page à part (#axe-…), qui ne montre que les projets de cet axe.
    def barre_filtres(actif):
        boutons = [f'<a class="filtre{" actif" if actif is None else ""}" href="#projets">'
                   f'{texte(reglages_projets.get("tous", "Tous"))}</a>']
        for c in categories:
            classe = "filtre actif" if actif == c["nom"] else "filtre"
            boutons.append(f'<a class="{classe}" href="#axe-{identifiant(c["nom"])}">'
                           f'{texte(c.get("onglet", c["nom"]))}</a>')
        return '    <nav class="filtres" aria-label="Filtrer les projets">' + "".join(boutons) + "</nav>"

    intro_projets = (f'\n    <p class="intro-projets">{texte(reglages_projets["intro"])}</p>'
                     if reglages_projets.get("intro") else "")
    # « À la une » : les projets cochés dans Notion, en grand, puis tous les autres
    une = [p for p in projets if est_a_la_une(p)]
    if une:
        autres = [p for p in projets if not est_a_la_une(p)]
        rangees_projets = (f'    <h3 class="titre-rangee">{texte(reglages_projets.get("titre_une", "À la une"))}</h3>\n'
                           f'    <div class="projets une">\n\n'
                           + "\n".join(carte_projet(p, grande=True) for p in une)
                           + "\n\n    </div>\n"
                           f'    <h3 class="titre-rangee">{texte(reglages_projets.get("titre_autres", "Tous les projets"))}</h3>\n'
                           + grille([carte_projet(p) for p in autres]))
    else:
        rangees_projets = grille([carte_projet(p) for p in projets])

    sections.append(f"""<section class="theme" id="projets">
  <div class="conteneur">
    <h2>{texte(titre_projets)}</h2>{intro_projets}
{barre_filtres(None)}
{rangees_projets}
  </div>
</section>""")
    for c in categories:
        cartes = [carte_projet(p) for p in projets if c["nom"] in categories_de(p)]
        intro = f'\n    <p class="intro-axe">{texte(c["titre"])}</p>' if c.get("titre") else ""
        sections.append(f"""<section class="theme" id="axe-{identifiant(c['nom'])}">
  <div class="conteneur">
    <h2>{texte(titre_projets)}</h2>{intro_projets}
{barre_filtres(c["nom"])}{intro}
{grille(cartes)}
  </div>
</section>""")

    # Une page détaillée par projet
    for p in projets:
        sections.append(page_projet(p, pages))

    # Une page par étiquette : tous les projets qui la portent
    tags = {}
    for p in projets:
        for t in etiquettes_de(p):
            tags.setdefault(identifiant(t), t)
    for slug, nom in sorted(tags.items()):
        concernes = [p for p in projets if slug in [identifiant(t) for t in etiquettes_de(p)]]
        nombre = f"{len(concernes)} projet" + ("s" if len(concernes) > 1 else "")
        sections.append(f"""<section class="theme page-tag" id="tag-{slug}">
  <div class="conteneur">
    <p class="retour"><a href="#" onclick="history.back(); return false;">← Retour</a></p>
    <h2>{texte(nom)}</h2>
    <p class="compte">{nombre}</p>
{grille([carte_projet(p, tag_actif=nom) for p in concernes])}
  </div>
</section>""")

    description = texte(" ".join(ap.get("texte", "").split())[:300])
    email = texte(ap.get("email", ""))
    pied = texte(NOM) + (f' · <a href="mailto:{email}">{email}</a>' if email else "")
    if site.get("mention_ia"):
        pied += f'\n    <p class="mention-ia">{texte(site["mention_ia"])}</p>'


    return f"""<!DOCTYPE html>
<!-- Page générée automatiquement par build.py à partir de Notion : ne pas modifier à la main. -->
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{texte(site.get('titre', NOM or 'Portfolio'))}</title>
  <meta name="description" content="{description}">
  <!-- Icônes (LinkedIn) : Font Awesome Free, fichiers dans le dossier icones/ -->
  <link rel="stylesheet" href="icones/css/fontawesome.min.css">
  <link rel="stylesheet" href="icones/css/brands.min.css">
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
    if (/^#(projet-|axe-|tag-)/.test(actif)) actif = '#projets';
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
    pages = lire_pages_notion()
    page = construire_page(reglages, projets, pages)
    avec_page = sum(1 for p in projets if identifiant(p["titre"]) in pages)
    print(f"{avec_page} projets ont une page détaillée écrite dans Notion, "
          f"les autres utilisent la colonne Description.")

    if SORTIE.exists():
        shutil.rmtree(SORTIE)
    SORTIE.mkdir()
    (SORTIE / "index.html").write_text(page, encoding="utf-8")
    shutil.copy(DOSSIER / "style.css", SORTIE / "style.css")
    shutil.copytree(DOSSIER / "images", SORTIE / "images")
    for dossier in ("documents", "icones", "polices"):
        if (DOSSIER / dossier).exists():
            shutil.copytree(DOSSIER / dossier, SORTIE / dossier)
    for publie, source in MEDIAS.items():
        (SORTIE / publie).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(source, SORTIE / publie)
    print(f"Site généré dans {SORTIE.name}/.")


if __name__ == "__main__":
    main()
