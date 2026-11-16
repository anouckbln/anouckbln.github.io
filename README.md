# Portfolio d'Anouck Blouin

Site en ligne : https://anouckbln.github.io

Le site tient en trois éléments :

- `index.html` : tout le contenu (textes, projets, liens) ;
- `style.css` : la mise en forme (couleurs, police, tailles) ;
- `images/` : les images des projets.

Chaque modification enregistrée sur GitHub est en ligne une ou deux minutes plus tard.

---

## Modifier un texte

1. Sur GitHub, ouvre `index.html` puis clique sur l'icône **crayon** (Edit this file).
2. Avec `Ctrl+F` (`Cmd+F` sur Mac), cherche le texte à changer.
3. Modifie-le **entre les balises** (par exemple entre `<p>` et `</p>`), sans toucher aux balises elles-mêmes.
4. Clique sur **Commit changes…** puis à nouveau sur **Commit changes**.

## Ajouter un projet

1. Dans `index.html`, repère la section voulue grâce aux grands commentaires `SECTION 1`, `SECTION 2`…
2. Copie un bloc existant, de `<article class="projet">` jusqu'à `</article>`, ou le modèle commenté en haut du fichier.
3. Colle-le juste avant la ligne `</div>` qui ferme la liste de projets de cette section.
4. Change le titre, le cadre, la description et le nom de l'image.

Pour supprimer un projet, efface son bloc entier, de `<article class="projet">` jusqu'à `</article>`.

## Ajouter ou remplacer une image

1. Ouvre le dossier `images/`, puis **Add file › Upload files** et glisse ton image.
2. Donne-lui un nom simple, sans espaces ni accents, par exemple `film-lignon.jpg`.
3. Dans `index.html`, écris ce nom aux deux endroits de la ligne :

```html
<a href="images/film-lignon.jpg" target="_blank"><img src="images/film-lignon.jpg" alt="Ce que montre l'image"></a>
```

Conseil : garde des images de moins de 500 Ko (1600 px de large suffisent) pour que le site reste rapide. Pour réduire une image, tu peux utiliser squoosh.app.

## Ajouter une section

1. Copie une section entière, de `<section class="theme" id="…">` jusqu'à `</section>`.
2. Donne-lui un nouvel `id`, court et sans accents, par exemple `id="participer"`.
3. Ajoute l'onglet correspondant dans la barre d'onglets (bloc `<nav class="onglets">`), en reprenant le même id précédé de `#` :

```html
<a href="#participer">Faire participer les habitant·es</a>
```

L'onglet affiché à l'arrivée sur le site est la première section de la page. Pour en changer, déplace la section voulue en premier.

## Changer les couleurs, la police ou les marges

Ouvre `style.css` : tout se règle dans les premières lignes (`--bleu`, `--texte`, `--largeur`…). Par exemple, remplace `#0a27a8` par un autre code couleur. Les marges sur les côtés se règlent dans le bloc `.conteneur`, et la largeur minimale des blocs projets dans le bloc `.projets` (`360px`).

## Si quelque chose ne s'affiche plus

- Va dans l'onglet **Actions** du dépôt pour vérifier que la publication a réussi (coche verte).
- Le plus souvent, une balise a été effacée ou un guillemet `"` oublié. Ouvre l'onglet **History** de `index.html` pour voir ta dernière modification, et revenir à la version précédente si besoin.
- Le navigateur garde parfois l'ancienne version en mémoire : recharge la page avec `Ctrl+Maj+R` (`Cmd+Maj+R` sur Mac).
