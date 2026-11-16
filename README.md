# Portfolio d'Anouck Blouin

Site en ligne : https://anouckbln.github.io

## Comment ça marche

Les projets sont rédigés dans la base Notion « Portfolio ». On l'exporte en CSV, on dépose le fichier sur GitHub, et le site se regénère tout seul.

| Fichier | Rôle | À modifier ? |
|---|---|---|
| `donnees/` | L'export CSV de la base Notion | Oui, à chaque mise à jour |
| `images/` | Les images des projets | Oui, pour en ajouter |
| `site.toml` | Présentation, contact, liste et ordre des onglets | De temps en temps |
| `style.css` | Couleurs, police, tailles, marges | Pour changer l'apparence |
| `build.py` | Le script Python qui transforme le CSV en site | Non |
| `.github/workflows/publier.yml` | Lance `build.py` et publie le site à chaque modification | Non |

---

## La base Notion

Colonnes reconnues (le nom compte, pas l'ordre ; majuscules et accents ignorés) :

| Colonne Notion | Type conseillé | Ce qu'elle devient sur le site |
|---|---|---|
| **Nom** | Titre | Titre du projet |
| **Entreprise** | Sélection | Ligne grise sous le titre (EPFL, Action Située…) |
| **Collaboration, propriété intellectuelle** | Texte | Ligne « En collaboration avec … » sous la description |
| **Description** | Texte | Texte du projet ; une ligne vide = un nouveau paragraphe |
| **thèmes** | Sélection multiple | Étiquettes saumon, cliquables |
| **Tags** | Sélection multiple | Étiquettes à contour bleu (méthodes, outils), cliquables |
| **Catégorie** | Sélection (ou multiple) | Onglet où le projet apparaît |
| **Images** | Texte | Noms des fichiers du dossier `images/`, séparés par des virgules |
| **Lien** | URL | Bouton « Voir le projet » |
| **Brouillon** | Case à cocher | Cochée : le projet est caché |
| **Ordre** | Nombre (facultatif) | Ordre d'affichage ; sinon, l'ordre de l'export |

Chaque étiquette (thème ou tag) est cliquable : elle ouvre une page qui regroupe tous les projets portant cette étiquette, quel que soit leur onglet. Ces pages sont créées automatiquement : un nouveau tag ajouté dans Notion a sa page dès la prochaine mise à jour. Pour regrouper deux projets, il suffit donc de leur donner le même tag, écrit de la même façon.

Toute autre colonne est ignorée : tu peux en garder pour toi (dates, notes…).

Les options de **Catégorie** doivent être écrites exactement comme les onglets de `site.toml`.

## Mettre le site à jour après une modification dans Notion

1. Dans Notion, ouvre la base Portfolio, clique sur **•••** en haut à droite, puis **Exporter**.
2. Choisis **Markdown & CSV**, puis **Exporter**. Dézippe le fichier téléchargé.
3. Sur GitHub, ouvre le dossier `donnees/`, clique sur **Add file › Upload files**, glisse les fichiers `.csv` et valide avec **Commit changes**.

Les fichiers exportés ont toujours le même nom : ils remplacent les anciens. Le site est en ligne une à deux minutes plus tard.

## Ajouter une image

1. Ouvre le dossier `images/` sur GitHub, puis **Add file › Upload files** et glisse ton image.
2. Donne-lui un nom simple, sans espaces ni accents, par exemple `film-lignon.jpg`.
3. Dans Notion, écris ce nom dans la colonne **Images** du projet (plusieurs images : `a.jpg, b.jpg`).

Conseil : garde des images de moins de 500 Ko (1600 px de large suffisent). Pour réduire une image : squoosh.app.

## Ajouter ou renommer un onglet

1. Dans `site.toml`, ajoute ou modifie un bloc :

```toml
[[categorie]]
nom = "Faire participer"
titre = "Faire participer les habitant·es"
```

2. Dans Notion, ajoute la même option à la colonne **Catégorie**, écrite exactement pareil que `nom`.

L'ordre des blocs dans `site.toml` est l'ordre des onglets. Le premier s'ouvre à l'arrivée sur le site.

## Changer l'apparence

Ouvre `style.css` : les couleurs, la police et la largeur se règlent dans les premières lignes (`--bleu`, `--tag`, `--largeur`…). Les marges sur les côtés sont dans le bloc `.conteneur`, et la largeur minimale des blocs projets dans le bloc `.projets` (`360px`).

## Si le site ne se met pas à jour

1. Ouvre l'onglet **Actions** du dépôt. Clique sur la dernière exécution, puis sur l'étape **Générer le site**.
2. Lis les lignes « Attention : … ». Elles signalent une image introuvable ou une catégorie mal orthographiée. Le site est quand même publié, sans l'élément en cause.
3. Une croix rouge signale une erreur bloquante, le plus souvent un guillemet oublié dans `site.toml` : le message indique la ligne.
4. Le navigateur garde parfois l'ancienne version en mémoire : recharge la page avec `Ctrl+Maj+R` (`Cmd+Maj+R` sur Mac).

## Voir le site sur ton ordinateur avant de publier (facultatif)

Avec Python 3.11 ou plus récent, ouvre un terminal dans le dossier du site et lance `python build.py`, puis ouvre `_site/index.html` dans ton navigateur.
