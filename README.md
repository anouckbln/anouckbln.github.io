# Portfolio d'Anouck Blouin

Site en ligne : https://anouckbln.github.io

## Comment ça marche

Les projets sont rédigés dans la base Notion « Portfolio ». On l'exporte en CSV, on dépose le fichier sur GitHub, et le site se regénère tout seul.

| Fichier | Rôle | À modifier ? |
|---|---|---|
| `donnees/` | L'export CSV de la base Notion | Oui, à chaque mise à jour |
| `images/` | Les images des projets et ta photo | Oui, pour en ajouter |
| `documents/` | Ton CV en PDF | Pour le mettre à jour |
| `site.toml` | Page « A propos », menu, couleurs des étiquettes | De temps en temps |
| `style.css` | Couleurs, police, tailles, marges | Pour changer l'apparence |
| `icones/` | L'icône LinkedIn (bibliothèque Font Awesome, gratuite) | Non |
| `build.py` | Le script Python qui transforme le CSV en site | Non |
| `.github/workflows/publier.yml` | Lance `build.py` et publie le site à chaque modification | Non |

---

## La base Notion

Colonnes reconnues (le nom compte, pas l'ordre ; majuscules et accents ignorés) :

| Colonne Notion | Type conseillé | Ce qu'elle devient sur le site |
|---|---|---|
| **Nom** | Titre | Titre du projet |
| **Résumé** | Texte | La phrase affichée sur la carte du projet |
| **Année** | Texte | Affichée à côté de l'entreprise (par exemple « 2025 » ou « 2024–2025 ») |
| **Entreprise** | Sélection | Sous le titre (EPFL, Action Située…) |
| **Description** | Texte | Texte de la page du projet, si la page Notion est vide ; une ligne vide = un nouveau paragraphe |
| **Tags** | Sélection multiple | Étiquettes saumon sous le titre, cliquables |
| **thèmes** | Sélection multiple | Non affichés (voir `afficher_themes` dans `site.toml`) |
| **Catégorie** | Sélection multiple | Domaines du projet : les filtres de la page Projets (un projet peut en avoir plusieurs) |
| **Images** | Texte | Noms des fichiers du dossier `images/`, séparés par des virgules |
| **Mosaïque** | Texte | Photos de la mosaïque d'accueil qui mènent à ce projet (par exemple `mosaique-1-pelouse.jpg`) |
| **Lien** | URL | Lien sous la description |
| **Texte du lien** | Texte | Texte de ce lien (« Voir le projet » par défaut) |
| **Collaboration, propriété intellectuelle** | Texte | Ligne « En collaboration avec … » sous la description |
| **Brouillon** | Case à cocher | Cochée : le projet est caché |
| **Type** | Sélection | Professionnel, Recherche, Master… : affiché au-dessus du titre |
| **À la une** | Case à cocher | Cochée : le projet apparaît en grand en haut de la page Projets |
| **Ordre** | Nombre | Ordre d'affichage sur la page Projets : 1 = en premier. Mets tes meilleurs projets en tête |

Toute autre colonne est ignorée : tu peux en garder pour toi (dates, notes…).

Les options de **Catégorie** doivent être écrites exactement comme les `nom` de `site.toml`. Un projet dont la catégorie n'y est pas apparaît dans « Tous », mais dans aucun filtre.

Chaque étiquette est cliquable : elle ouvre une page qui regroupe tous les projets portant cette étiquette, quelle que soit leur catégorie. Ces pages sont créées automatiquement. Pour regrouper des projets, il suffit de leur donner la même étiquette, écrite exactement pareil.

## Organisation du site

- **Accueil** : la mosaïque de 9 photos et sa légende (bloc `[accueil]` de `site.toml`). Les photos apparaissent une par une ; chacune mène au projet qui la cite dans la colonne **Mosaïque** de Notion, ou, par défaut, à la page Projets. Les photos sont dans `images/`, nommées `mosaique-1-…` à `mosaique-9-…` : pour en changer une, remplace le fichier en gardant le nom, ou change le nom dans `site.toml`. Une photo carrée d'environ 700 px suffit.
- **Projets** : tous les projets en cartes, dans l'ordre de la colonne **Ordre**. En haut, des boutons filtrent par domaine : « Adaptation au climat », « Mobilités », etc. Les étiquettes (colonne **Tags**) indiquent les compétences et méthodes.
- **A propos** : ta présentation, sur fond bleu.
- **CV** : ouvre ton CV en PDF.

## Cartes et pages de projet

Sur chaque page de catégorie, un projet apparaît sous forme de **carte** : sa première image, son titre, l'entreprise et l'année, le résumé et les étiquettes. Un clic sur la carte ouvre la **page du projet**.

Le texte de la page du projet s'écrit **dans la page Notion du projet** : ouvre la ligne du projet dans Notion comme un document, et écris en dessous des propriétés. Utilise des intertitres (`/titre 2` dans Notion) pour structurer, par exemple :

- **Contexte** : quel problème, pour qui, où ;
- **Mon rôle** : ce que tu as fait toi-même, et avec qui ;
- **Méthode** : données, outils, ateliers, enquêtes ;
- **Résultats** : ce que ça a produit ou permis de décider.

Les listes à puces, le gras, l'italique, les liens et les images collées dans la page sont repris sur le site. Si la page Notion est vide, le site utilise la colonne **Description**.

Le dossier `donnees/pages/` contient une première version de ces textes, un fichier par projet. Copie le contenu de chaque fichier dans la page Notion correspondante : Notion le met en forme tout seul. Une fois tes pages remplies et exportées, les textes de Notion remplacent ces brouillons.

## Mettre le site à jour après une modification dans Notion

1. Dans Notion, ouvre la base Portfolio, clique sur **•••** en haut à droite, puis **Exporter**.
2. Choisis **Markdown & CSV**, puis **Exporter**. Dézippe le fichier téléchargé.
3. Sur GitHub, ouvre le dossier `donnees/`, clique sur **Add file › Upload files**, glisse **tout le contenu** du dossier exporté (les fichiers `.csv` et le dossier qui contient les pages des projets) et valide avec **Commit changes**.

Les fichiers exportés ont toujours le même nom : ils remplacent les anciens. Le site est en ligne une à deux minutes plus tard.

## Ajouter une image

1. Ouvre le dossier `images/` sur GitHub, puis **Add file › Upload files** et glisse ton image.
2. Donne-lui un nom simple, sans espaces ni accents, par exemple `film-lignon.jpg`.
3. Dans Notion, écris ce nom dans la colonne **Images** du projet (plusieurs images : `a.jpg, b.jpg`).

Conseil : garde des images de moins de 500 Ko (1600 px de large suffisent). Pour réduire une image : squoosh.app.

## Modifier la page « A propos »

Tout est dans le bloc `[a_propos]` de `site.toml` : texte, téléphone, email, LinkedIn, photo, CV et les bulles de thématiques (liste `thematiques`). La couleur des bulles se règle avec `--bulle` en haut de `style.css`. Pour ne pas afficher un élément, remplace sa valeur par `""`.

Pour mettre à jour ton CV, dépose le nouveau PDF dans `documents/` avec le même nom, `CV_Anouck_Blouin.pdf`. Il remplace l'ancien.

## Ajouter ou renommer un domaine (filtre)

1. Dans `site.toml`, ajoute ou modifie un bloc :

```toml
[[categorie]]
nom = "Faire participer les habitant·es"
onglet = "Faire participer"
titre = "Une phrase qui présente cet axe"
```

- `nom` : écrit exactement comme l'option de la colonne **Catégorie** dans Notion ;
- `onglet` : texte du bouton de filtre (facultatif) ;
- `titre` : phrase affichée sous les filtres quand l'axe est sélectionné (facultatif).

2. Dans Notion, ajoute la même option à la colonne **Catégorie**.

L'ordre des blocs dans `site.toml` est l'ordre des boutons.

## Couleurs des étiquettes

Les étiquettes sont saumon. Pour en colorer certaines autrement, ajoute une ligne dans le bloc `[etiquettes.couleurs]` de `site.toml` :

```toml
"Publication" = "#2bb5a5"
```

## Changer l'apparence

Ouvre `style.css` : les couleurs, la police, les largeurs et les tailles de texte se règlent dans les premières lignes (`--bleu`, `--tag`, `--largeur`, `--colonne`, `--taille-texte`, `--taille-titre-page`…). Les tailles suivent une échelle régulière à partir de 16 px : pour garder un ensemble harmonieux, change-les toutes dans la même proportion. `--colonne` est la largeur minimale d'un bloc projet : plus elle est petite, plus il y a de projets par ligne.

## Si le site ne se met pas à jour

1. Ouvre l'onglet **Actions** du dépôt. Clique sur la dernière exécution, puis sur l'étape **Générer le site**.
2. Lis les lignes « Attention : … ». Elles signalent une image introuvable ou une catégorie mal orthographiée. Le site est quand même publié, sans l'élément en cause.
3. Une croix rouge signale une erreur bloquante, le plus souvent un guillemet oublié dans `site.toml` : le message indique la ligne.
4. Le navigateur garde parfois l'ancienne version en mémoire : recharge la page avec `Ctrl+Maj+R` (`Cmd+Maj+R` sur Mac).

## Voir le site sur ton ordinateur avant de publier (facultatif)

Avec Python 3.11 ou plus récent, ouvre un terminal dans le dossier du site et lance `python build.py`, puis ouvre `_site/index.html` dans ton navigateur.
