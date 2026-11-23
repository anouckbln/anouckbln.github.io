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
| `build.py` | Le script Python qui transforme le CSV en site | Non |
| `.github/workflows/publier.yml` | Lance `build.py` et publie le site à chaque modification | Non |

---

## La base Notion

Colonnes reconnues (le nom compte, pas l'ordre ; majuscules et accents ignorés) :

| Colonne Notion | Type conseillé | Ce qu'elle devient sur le site |
|---|---|---|
| **Nom** | Titre | Titre du projet |
| **Entreprise** | Sélection | Ajoutée après le titre : « Titre - Entreprise ». Laisse vide si le titre la contient déjà |
| **Description** | Texte | Texte du projet ; une ligne vide = un nouveau paragraphe |
| **Tags** | Sélection multiple | Étiquettes saumon sous le titre, cliquables |
| **thèmes** | Sélection multiple | Non affichés (voir `afficher_themes` dans `site.toml`) |
| **Catégorie** | Sélection | Page où le projet apparaît |
| **Images** | Texte | Noms des fichiers du dossier `images/`, séparés par des virgules |
| **Lien** | URL | Lien sous la description |
| **Texte du lien** | Texte | Texte de ce lien (« Voir le projet » par défaut) |
| **Collaboration, propriété intellectuelle** | Texte | Ligne « En collaboration avec … » sous la description |
| **Brouillon** | Case à cocher | Cochée : le projet est caché |
| **Ordre** | Nombre (facultatif) | Ordre d'affichage ; sinon, l'ordre de l'export |

Toute autre colonne est ignorée : tu peux en garder pour toi (dates, notes…).

Les options de **Catégorie** doivent être écrites exactement comme les `nom` de `site.toml`. Un projet dont la catégorie n'y est pas (par exemple « Autres projets ») n'apparaît nulle part.

Chaque étiquette est cliquable : elle ouvre une page qui regroupe tous les projets portant cette étiquette, quelle que soit leur catégorie. Ces pages sont créées automatiquement. Pour regrouper des projets, il suffit de leur donner la même étiquette, écrite exactement pareil.

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

## Modifier la page « A propos »

Tout est dans le bloc `[a_propos]` de `site.toml` : texte, téléphone, email, LinkedIn, photo et CV. Pour ne pas afficher un élément, remplace sa valeur par `""`.

Pour mettre à jour ton CV, dépose le nouveau PDF dans `documents/` avec le même nom, `CV_Anouck_Blouin.pdf`. Il remplace l'ancien.

## Ajouter ou renommer une catégorie

1. Dans `site.toml`, ajoute ou modifie un bloc :

```toml
[[categorie]]
nom = "Faire participer"
onglet = "Faire participer les habitant·es"
titre = "Faire participer les habitant·es"
```

- `nom` : écrit exactement comme l'option de la colonne **Catégorie** dans Notion ;
- `onglet` : texte du menu (facultatif) ;
- `titre` : titre de la page (facultatif).

2. Dans Notion, ajoute la même option à la colonne **Catégorie**.

L'ordre des blocs dans `site.toml` est l'ordre du menu, après « A propos ».

## Couleurs des étiquettes

Les étiquettes sont saumon. Pour en colorer certaines autrement, ajoute une ligne dans le bloc `[etiquettes.couleurs]` de `site.toml` :

```toml
"Publication" = "#2bb5a5"
```

## Changer l'apparence

Ouvre `style.css` : les couleurs, la police et les largeurs se règlent dans les premières lignes (`--bleu`, `--tag`, `--largeur`, `--colonne`…). `--colonne` est la largeur minimale d'un bloc projet : plus elle est petite, plus il y a de projets par ligne.

## Si le site ne se met pas à jour

1. Ouvre l'onglet **Actions** du dépôt. Clique sur la dernière exécution, puis sur l'étape **Générer le site**.
2. Lis les lignes « Attention : … ». Elles signalent une image introuvable ou une catégorie mal orthographiée. Le site est quand même publié, sans l'élément en cause.
3. Une croix rouge signale une erreur bloquante, le plus souvent un guillemet oublié dans `site.toml` : le message indique la ligne.
4. Le navigateur garde parfois l'ancienne version en mémoire : recharge la page avec `Ctrl+Maj+R` (`Cmd+Maj+R` sur Mac).

## Voir le site sur ton ordinateur avant de publier (facultatif)

Avec Python 3.11 ou plus récent, ouvre un terminal dans le dossier du site et lance `python build.py`, puis ouvre `_site/index.html` dans ton navigateur.
