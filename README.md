# Portfolio d'Anouck Blouin

Site en ligne : https://anouckbln.github.io

## Comment ça marche

Tous les projets sont dans un seul tableau, `donnees/projets.csv`, que l'on ouvre avec Excel. À chaque modification enregistrée sur GitHub, le site est regénéré et publié automatiquement en une ou deux minutes.

| Fichier | Rôle | À modifier ? |
|---|---|---|
| `donnees/projets.csv` | Le tableau des projets | Oui, pour toute modification de projet |
| `images/` | Les images des projets, la mosaïque d'accueil, ta photo | Oui, pour en ajouter |
| `documents/` | Ton CV en PDF | Pour le mettre à jour |
| `site.toml` | Accueil, page « A propos », menu, filtres, couleurs des étiquettes | De temps en temps |
| `style.css` | Couleurs, police, tailles, marges | Pour changer l'apparence |
| `polices/`, `icones/` | La police Hanken Grotesk et l'icône LinkedIn | Non |
| `build.py` | Le script Python qui fabrique le site à partir du tableau | Non |
| `.github/workflows/publier.yml` | Lance `build.py` et publie le site | Non |

---

## Modifier le tableau avec Excel

1. Sur GitHub, ouvre `donnees/projets.csv` et clique sur l'icône de téléchargement (**Download raw file**).
2. Ouvre le fichier dans Excel et fais tes modifications.
3. Enregistre avec **Fichier › Enregistrer sous**, format **CSV UTF-8 (délimité par des virgules)**, sous le même nom `projets.csv`. Ce format garde les accents.
4. Sur GitHub, ouvre le dossier `donnees`, puis **Add file › Upload files**, glisse `projets.csv` et valide avec **Commit changes**. Il remplace l'ancien.

Pour aller plus vite, garde ce fichier sur ton ordinateur et reprends-le à chaque fois depuis l'étape 2.

Dans une cellule, **Alt + Entrée** (Option + Entrée sur Mac) passe à la ligne. Une ligne vide sépare deux paragraphes, et une ligne qui commence par `- ` devient une puce. `**mot**` met un mot en gras.

## Les colonnes du tableau

L'ordre des colonnes n'a pas d'importance, seul leur nom compte. Toute autre colonne est ignorée : tu peux en ajouter pour toi.

| Colonne | Ce qu'elle devient sur le site |
|---|---|
| **Nom** | Titre du projet |
| **Résumé** | La phrase affichée sur la carte du projet |
| **Année** | À côté de l'entreprise, sous le titre |
| **Ordre** | Ordre d'affichage : 1 = en premier |
| **À la une** | `oui` : le projet apparaît en grand en haut de la page Projets |
| **Type** | Professionnel, Recherche, Master… : en saumon sous le titre |
| **Entreprise** | Sous le titre (EPFL, Action Située…) |
| **Collaboration, propriété intellectuelle** | Sur la page du projet. Des noms (« Lou Mandonnet, Vincent Viguié ») deviennent « Avec Lou Mandonnet, Vincent Viguié » (mot réglable avec `texte_collaboration` dans `site.toml`) ; une phrase (« Travail réalisé en groupe ») est affichée telle quelle |
| **Description** | Texte de la page du projet, si les quatre colonnes suivantes sont vides |
| **Contexte**, **Mon rôle**, **Méthode**, **Résultats** | Les parties de la page du projet, dans cet ordre. Une colonne vide n'est pas affichée |
| **Tags** | Étiquettes cliquables (compétences et méthodes), séparées par des virgules |
| **thèmes** | Non affichés (voir `afficher_themes` dans `site.toml`) |
| **Catégorie** | Domaines du projet : les filtres de la page Projets, séparés par des virgules |
| **Images** | Noms des fichiers du dossier `images/`, séparés par des virgules. La première est celle de la carte |
| **Mosaïque** | Photos de la mosaïque d'accueil qui mènent à ce projet (par exemple `mosaique-1-pelouse.jpg`) |
| **Lien** et **Texte du lien** | Un lien sur la page du projet (« Voir le projet » par défaut) |
| **Brouillon** | `oui` : le projet est caché |

Les noms de **Catégorie** doivent être écrits exactement comme dans `site.toml` : Adaptation au climat, Mobilités, Espaces publics et santé, Données et politiques publiques.

Pour ajouter un projet, ajoute une ligne. Pour en supprimer un, supprime sa ligne ou mets `oui` dans **Brouillon**.

## Organisation du site

- **Accueil** : la mosaïque de 9 photos et sa légende (bloc `[accueil]` de `site.toml`). Les photos apparaissent une par une ; chacune mène au projet qui la cite dans la colonne **Mosaïque**, sinon à la page Projets. Pour changer une photo, remplace le fichier `images/mosaique-…` en gardant son nom (une photo carrée d'environ 700 px suffit).
- **Projets** : les projets « À la une » en grand, puis tous les autres, dans l'ordre de la colonne **Ordre**. En haut, des boutons filtrent par domaine. Chaque carte ouvre la page du projet, et chaque étiquette ouvre la liste des projets qui la portent.
- **A propos** : ta présentation et les bulles de thématiques (bloc `[a_propos]` de `site.toml`).
- **CV** : ouvre ton CV en PDF. Pour le mettre à jour, dépose le nouveau PDF dans `documents/` sous le nom `CV_Anouck_Blouin.pdf`.

## Ajouter une image

1. Ouvre le dossier `images/` sur GitHub, puis **Add file › Upload files** et glisse ton image.
2. Donne-lui un nom simple, sans espaces ni accents, par exemple `film-lignon.jpg`.
3. Dans le tableau, écris ce nom dans la colonne **Images** du projet.

Conseil : garde des images de moins de 500 Ko (1600 px de large suffisent). Pour réduire une image : squoosh.app.

## Changer l'apparence

Ouvre `style.css` : les couleurs, la police, les largeurs et les tailles de texte se règlent dans les premières lignes (`--bleu`, `--tag`, `--taille-texte`, `--taille-titre-page`…).

## Si le site ne se met pas à jour

1. Ouvre l'onglet **Actions** du dépôt et clique sur la dernière exécution, puis sur l'étape **Générer le site**.
2. Les lignes « Attention : … » signalent une image introuvable ou une catégorie mal orthographiée. Le site est quand même publié, sans l'élément en cause.
3. Une croix rouge signale une erreur bloquante, le plus souvent un guillemet oublié dans `site.toml` : le message indique la ligne. Si l'erreur parle de « artifact » ou de GitHub, c'est un problème passager : clique sur **Re-run jobs**.
4. Le navigateur garde parfois l'ancienne version en mémoire : recharge la page avec `Ctrl+Maj+R` (`Cmd+Maj+R` sur Mac).
