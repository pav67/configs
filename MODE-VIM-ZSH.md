# Le mode Vim dans ton terminal Zsh

Le plugin `zsh-vi-mode`, activé dans ton `.zshrc`, permet de modifier la **commande en cours de saisie** avec les gestes de Vim. Il ne lance pas Neovim et ne change pas les raccourcis de toutes les applications. Il agit lorsque Zsh attend une commande.

Son intérêt : corriger un argument, remplacer un chemin, réutiliser une commande longue ou modifier du texte entre guillemets sans maintenir les flèches ni reprendre la souris.

## Pourquoi il se déclenche

`Échap` ou `Ctrl-[` quitte la saisie et passe en **mode normal**. Les lettres deviennent alors des actions : `h` déplace le curseur, `x` supprime un caractère, etc. Ce n'est pas un blocage du terminal.

**Pour reprendre la saisie immédiatement : appuie sur `i`.** Pour écrire à la fin de la commande : `A` (majuscule).

Le plugin conserve par défaut le dernier mode utilisé entre deux lignes de commande. Si tu valides une commande en mode normal, tu peux donc retrouver ce mode au prompt suivant. Ta configuration ne force pas un retour systématique en insertion.

| Mode | Comment y entrer | Comportement / repère |
|---|---|---|
| Insertion | `i`, `a`, `I` ou `A` depuis le mode normal | Saisie habituelle ; curseur fin ; chevron `❯` |
| Normal | `Échap` ou `Ctrl-[` | Déplacement et édition ; curseur bloc ; chevron `❮` ambre |
| Visuel | `v` depuis le mode normal | Sélection avec les mouvements, puis action ; chevron `❮` mauve |
| Remplacement | `R` depuis le mode normal | Remplacer plusieurs caractères ; `Échap` pour sortir ; chevron `❮` orange |

En insertion, le chevron est vert après une commande réussie et rouge après un échec. La forme du curseur dépend aussi du terminal. Ta configuration désactive la mise en évidence supplémentaire du plugin : ne compte pas uniquement sur un fond coloré pour reconnaître le mode.

## Les touches qui suffisent pour commencer

Dans les tableaux suivants, les actions sont en **mode normal**, donc après `Échap`. Les séquences comme `ciw` se tapent successivement, pas simultanément.

| Touche | Action |
|---|---|
| `h` / `l` | Reculer / avancer d'un caractère |
| `w` / `b` | Mot suivant / précédent |
| `W` / `B` | Élément suivant / précédent séparé par des espaces ; pratique pour les chemins |
| `0` / `^` / `$` | Début de ligne / premier caractère non blanc / fin de ligne |
| `f/` | Aller au prochain `/` ; `;` répète le mouvement |
| `i` / `a` | Insérer avant / après le curseur |
| `I` / `A` | Insérer au début / à la fin de la ligne |
| `x` | Supprimer le caractère sous le curseur |
| `dw` | Supprimer jusqu'au début du mot suivant |
| `ciw` | Remplacer le mot sous le curseur et passer en insertion |
| `ciW` | Remplacer l'élément entier délimité par des espaces |
| `ci"` | Remplacer le contenu entre guillemets doubles |
| `D` / `C` | Supprimer / remplacer jusqu'à la fin de la ligne |
| `dd` / `cc` | Supprimer / remplacer la ligne |
| `u` / `Ctrl-R` | Annuler / rétablir une modification en mode normal |
| `yy` / `p` | Copier la ligne / coller après le curseur |
| `.` | Répéter la dernière modification |

Ces suppressions et annulations concernent le texte du prompt. `u` n'annule pas une commande déjà exécutée. Le tampon de copie Vim du shell n'est pas automatiquement le presse-papiers du système.

La logique est composable : **action + cible**, éventuellement avec un nombre. `d` supprime, `c` remplace, `y` copie ; `w` désigne un mouvement de mot, `iw` l'intérieur d'un mot. Par exemple `3w` avance de trois mots et `d2w` supprime sur deux mouvements de mot.

## Cas d'usage

### 1. Corriger un hôte sans retaper la commande

Tu as saisi, sans valider :

```text
ssh codexops@klcentral
```

Appuie sur `Échap`, puis `0`, `f@`, `l`, `C`, et saisis `ainode`.

Résultat : `ssh codexops@ainode`. `f@` trouve le séparateur, `l` avance après lui et `C` remplace la fin de ligne. Vérifie puis valide avec Entrée.

### 2. Remplacer le dernier chemin

Tu as saisi :

```text
ls -lah /var/log/nginx
```

Depuis la fin de la commande : `Échap`, `$`, `B`, `c$`, puis `/var/log/apache2`.

`B` traite le chemin comme un bloc délimité par des espaces ; `c$` remplace jusqu'au bout. Avec `b`, les `/` découpent le chemin en plusieurs mots.

### 3. Modifier un message entre guillemets

Sur cette ligne non exécutée :

```text
git commit -m "ancien message"
```

Appuie sur `Échap`, `0`, `f"`, `l`, puis `ci"`. Saisis `nouveau message` : les guillemets sont conservés.

### 4. Ajouter une option à une commande retrouvée

En insertion, `Ctrl-R` ouvre la recherche fzf de l'historique. Sélectionne une commande : elle revient dans la ligne d'édition. Appuie sur `Échap`, puis `A`, et ajoute l'option voulue.

Exemple : compléter `ls /var/log` avec ` -lah`. La recherche fzf et les mouvements Vim se complètent très bien.

Tu peux également rechercher en mode normal avec `/`, saisir un fragment, puis Entrée pour terminer la recherche ; `n` cherche l'occurrence suivante. Relis la ligne avant de l'exécuter.

### 5. Éditer une longue commande dans Neovim

Depuis le mode normal, tape `vv`. Le plugin ouvre la ligne dans l'éditeur indiqué par `ZVM_VI_EDITOR`, sinon `$EDITOR`. Le kit définit désormais `EDITOR=nvim` ; sur une ancienne configuration, tu peux lancer `export EDITOR=nvim`.

Dans Neovim, modifie la commande, puis utilise `:wq` pour revenir au prompt. Relis la ligne et valide ensuite dans Zsh. C'est pratique pour une commande comportant plusieurs pipes, des conditions ou de nombreux arguments.

## Tes raccourcis existants

Les raccourcis personnalisés sont installés dans `zvm_after_init()`, après ceux du plugin, pour éviter qu'ils soient écrasés.

La touche **Insert est neutralisée en mode insertion** (`viins`) : sa séquence complète déclenche une action vide, enregistrée via `zvm_bindkey`. Il ne faut pas simplement désassigner la touche : le lecteur NEX du plugin peut alors interpréter `Esc [ 2 ~` comme Échap suivi de commandes Vim, dont `~` qui inverse la casse. La séquence standard, celle du terminal (`terminfo[kich1]`) et la variante `Esc [ 2 ; 2 ~` de Shift-Insert sont consommées sans modifier le texte ni le mode. `Échap` seul reste actif. Le collage par `Shift-Insert` reste géré par le terminal ; s'il transmet seulement une séquence de touche, Zsh n'a pas accès au presse-papiers. Le collage encadré (*bracketed paste*) est conservé.

Le test `python3 tests/check_zsh_keys.py` exerce les vraies frappes dans un pseudo-terminal avec les plugins installés sur le poste : Échap, retour en insertion, Insert, Shift-Insert et collage avec conservation de la casse.

En **insertion** :

| Raccourci | Fonction |
|---|---|
| `Ctrl-R` | Historique avec fzf |
| `Ctrl-T` | Sélection de fichier avec aperçu, fichiers cachés inclus |
| `Ctrl-F` | Sélection de fichier non caché |
| `Alt-C` | Choix d'un dossier avec fzf |
| `↑` / `↓` | Historique filtré par le texte saisi |
| `Ctrl-←` / `Ctrl-→` | Mot précédent / suivant |
| `Ctrl-\` | Activer / désactiver les suggestions |

Attention au contexte : `Ctrl-R` signifie **historique fzf en insertion**, mais **rétablir en mode normal**. Reviens avec `i` avant d'utiliser les raccourcis fzf.

Le mode copie tmux, ouvert avec `Ctrl-b [`, est indépendant : il parcourt les sorties déjà affichées. `q` quitte ce mode copie. Le mode Vim de Zsh édite la commande que tu vas lancer.

## Si tu préfères toujours démarrer en saisie

Ajoute ceci après le chargement d'Oh My Zsh dans `.zshrc` :

```zsh
ZVM_LINE_INIT_MODE=$ZVM_MODE_INSERT
```

Tu gardes `Échap` pour utiliser Vim ponctuellement, mais chaque nouvelle commande commence en insertion. Ce réglage est proposé ici, il n'est pas activé par cette personnalisation des thèmes.

Pour désactiver complètement le mode Vim, retire `zsh-vi-mode` de `plugins=(...)`, retire ses réglages et déplace les raccourcis utiles hors de son hook avant de relancer Zsh. Retirer seulement le plugin laisserait les raccourcis définis dans `zvm_after_init()` sans initialisation.

Référence : README du plugin installé, également disponible dans le [dépôt zsh-vi-mode](https://github.com/jeffreytse/zsh-vi-mode#-usage).
