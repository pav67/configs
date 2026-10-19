# Configurations du poste

Kit personnel pour retrouver Zsh, tmux, Starship et les préférences Codex sur un nouveau poste Linux ou macOS. Le README sert de spécification du comportement et des raccourcis.

## Installation

```bash
git clone https://github.com/pav67/configs.git ~/configs
cd ~/configs
./install.sh
```

Exécuter avec l'utilisateur final, sans `sudo` devant le script. Il utilise `sudo` pour les paquets, le shell par défaut et le linger systemd. Il faut un accès Internet ; sur Linux, une session utilisateur systemd active est nécessaire. Sur macOS, voir le parcours ci-dessous. La cible de référence est Debian 13 ; des branches d'installation sont également prévues pour Fedora et Arch (non validées sur un poste réel). Les anciennes distributions peuvent ne pas fournir tous les paquets ; leur installation échoue explicitement dans ce cas. Sur Arch, le script effectue une mise à jour complète avec `pacman -Syu`.

Sélectionner une **Nerd Font dans le terminal client**, y compris pour les connexions SSH, pour afficher les icônes du prompt et de tmux.

Pour mettre à jour :

```bash
cd ~/configs
git pull
./install.sh
```

Les fichiers remplacés sont sauvegardés avec le suffixe `.bak.DATE-HEURE-PID`, notamment `.profile`, la configuration Codex et le service systemd. Les installations existantes de Starship, Leaf, Oh My Zsh et de ses plugins sont conservées. Les paquets suivent le gestionnaire de la distribution.

## V2 : wizard plein ecran

`./install.sh` ouvre un assistant natif Bash, sans outil d'interface supplémentaire à installer. Un écran ASCII présente les composants ; le récapitulatif permet de revenir à la sélection avant toute installation.

- **Flèches / j / k** : se déplacer ; **Espace** : cocher/décocher.
- **A** : tout sélectionner ; **N** : tout désélectionner.
- **Entrée** : récapitulatif, puis lancement ; **R** : revenir depuis le récapitulatif.
- **Q** : quitter sans installer. Un journal peut être créé, mais aucun composant n'est modifié.

Le terminal doit faire au moins **70 colonnes × 24 lignes**. L'écran alternatif est restauré à la fin, en cas d'erreur ou d'interruption. Pendant l'installation, les cinq dernières étapes terminées et l'étape animée restent visibles. Les mots de passe restent demandés au premier plan.

| Identifiant | Ce qui est installé / configuré |
|---|---|
| `zsh` | Zsh, Oh My Zsh, plugins et remplacement de `.zshrc` |
| `tools` | eza, bat, ripgrep, fd, fzf, lf, less, diffutils |
| `starship` | Starship et son thème ; activé par le `.zshrc` du kit |
| `tmux` | tmux, thème et script d'identité réseau |
| `session` | Service persistant, session et auto-attachement dans `.profile` / `.zshrc` |
| `neovim` | Neovim, sans configuration personnalisée |
| `vim` | Vim et `.vimrc` |
| `leaf` | Lecteur Markdown Leaf |
| `codex` | Préférences Codex uniquement, sans CLI ni authentification |
| `default-shell` | Passage de l'utilisateur à Zsh comme shell de connexion |

Les dépendances automatiques apparaissent avec `[+]` : **Zsh → tools**, **session → tmux**, **default-shell → Zsh → tools**. Pour supprimer une dépendance, désélectionner aussi le composant qui la requiert. Python reste une dépendance technique commune. Les composants ignorés ne sont pas désinstallés ; leurs fichiers ne sont pas modifiés, sauf les fichiers explicitement partagés indiqués dans le tableau (`.zshrc` pour `zsh` et `session`).

Sans Starship, le `.zshrc` dispose d'un prompt simple. Sans Neovim, l'éditeur choisi est Vim s'il existe, sinon vi. Installer Starship seul ne réécrit pas ton shell existant : il faut déjà son initialisation, ou choisir aussi Zsh. Choisir Zsh sans session installe un `.zshrc` sans bloc d'auto-attachement ; cela ne désactive pas un service tmux déjà installé.

### Automatisation et installations ciblées

Sans terminal, le script exige un choix explicite et ne lance rien par défaut :

```bash
./install.sh --all
./install.sh --components zsh,starship,tmux,neovim
./install.sh --components codex
./install.sh --list
./install.sh --help
```

`--all` retrouve le comportement complet de la v1, avec la progression en ligne et les journaux. `--components` applique la sélection sans ouvrir le wizard ; les dépendances sont ajoutées automatiquement. Les sauvegardes et la gestion des erreurs sont identiques dans les deux modes.

## Progression et journaux d'installation

L'installateur affiche les étapes avec une animation discrète, puis une coche et leur durée :

```text
  SHELL KIT
  Ton environnement, prêt à travailler.

  ✓ 01 · Installation des dépendances (12s)
  ✓ 02 · Starship, Leaf et vérification des outils (3s)
  ⠹ 03 · Configuration de Starship et Codex (1s)
```

Les sorties standard et d'erreur des sous-commandes, les sauvegardes et le récapitulatif détaillé sont écrits dans un journal distinct pour chaque exécution :

```text
${XDG_STATE_HOME:-$HOME/.local/state}/shell-kit/install-DATE-HEURE-XXXXXX
```

Son chemin exact est affiché au début et à la fin. Le dossier est privé (700) et les fichiers sont lisibles uniquement par leur propriétaire (600). Pour suivre le détail depuis un autre terminal : `tail -f /chemin/affiché/du/journal`.

En cas d'échec, l'animation s'arrête, l'étape et le code d'erreur sont affichés, ainsi qu'une indication lorsque l'erreur est connue (Homebrew absent, par exemple). Les diagnostics complets restent dans le journal ; l'installateur s'arrête avec le code d'erreur de la commande. Une interruption arrête également l'animation. Les fichiers déjà installés ne sont pas annulés automatiquement ; leurs sauvegardes sont conservées.

Les demandes de mot de passe sudo ou de changement de shell macOS restent visibles, animation suspendue. Les commandes d'installation restent au premier plan : leurs changements de variables et leurs erreurs ne sont pas perdus dans un processus séparé.

Sans terminal interactif (redirection ou CI), l'affichage devient une liste statique, sans séquences de contrôle. `NO_COLOR=1 ./install.sh` désactive les couleurs. Le journal n'est ni ajouté au dépôt ni envoyé à un service externe.

## Installation sur MacBook

Le même kit gère les chemins Homebrew Apple Silicon (`/opt/homebrew`) et Intel (`/usr/local`). Il faut une version de macOS prise en charge par Homebrew ; la disponibilité de certains paquets sur Intel dépend de Homebrew.

1. Installer les outils de développement si Git n'est pas disponible : `xcode-select --install`, puis terminer la boîte de dialogue macOS.
2. Installer [Homebrew](https://brew.sh/) s'il est absent et suivre les instructions affichées. Le kit détecte une installation existante mais ne déclenche pas son installation silencieusement.
3. Cloner le dépôt puis exécuter le même `./install.sh`, sans sudo :

```bash
git clone https://github.com/pav67/configs.git ~/configs
cd ~/configs
./install.sh
```

Les paquets sont installés par Homebrew, notamment Starship et `leaf-markdown-viewer` (commande `leaf`). Le shell de connexion reste `/bin/zsh`, déjà autorisé par macOS. Homebrew est chargé dans `.zshrc`, y compris pour les shells non-login ouverts par tmux. L'alias `diff` utilise `gdiff` de GNU diffutils ; `fd`, `bat` et les scripts fzf utilisent leurs emplacements Homebrew.

### Session partagée sur macOS

Un LaunchAgent `~/Library/LaunchAgents/net.pav67.tmux-shared.plist` crée la session à l'ouverture de session macOS. Il remplace systemd/linger et ne nécessite pas de service root. Le script `~/.config/tmux/start-shared.sh` conserve une session existante. Sans session graphique pendant l'installation (par exemple via SSH), le LaunchAgent attend la prochaine ouverture de session graphique ; la session tmux est néanmoins créée immédiatement.

Les terminaux locaux interactifs et les connexions SSH s'attachent automatiquement à `shared`. Linux conserve l'attachement automatique en SSH uniquement. Pour ouvrir un shell sans attachement :

```bash
TMUX_AUTO_ATTACH=0 zsh
```

Fermer un terminal ou détacher tmux laisse les programmes tourner tant que le serveur tmux reste actif. Une déconnexion complète du compte ou un redémarrage ne garantit pas leur survie : le LaunchAgent recrée une session vide, il ne restaure pas les processus. Le Mac n'est pas maintenu éveillé par le kit.

```bash
launchctl print "gui/$(id -u)/net.pav67.tmux-shared"
tmux ls
cat ~/Library/Logs/tmux-shared.log
```

### Affichage et clavier Mac

Sélectionner une Nerd Font dans le profil du terminal. Par exemple, `brew install --cask font-meslo-lg-nerd-font`, puis sélectionner **MesloLGS Nerd Font** dans les réglages du terminal. Les deux bulles tmux restent identiques ; un MacBook non listé dans la palette utilise le gris bleuté de repli.

Les touches tmux `F2/F3/F4/F10` nécessitent parfois `Fn`/🌐 ou le réglage macOS « Utiliser les touches F1, F2, etc. comme des touches de fonction standard ». Les équivalents `Ctrl-b c/p/n` restent disponibles. Activer « Utiliser Option comme touche Meta » dans Terminal pour `Alt-C` (Option-C). Les raccourcis Mission Control peuvent intercepter `Ctrl-←/→` : les mouvements Vim `Échap`, puis `b/w` évitent ce conflit.

Voir les [conditions Homebrew](https://docs.brew.sh/Installation), la [formule Leaf](https://formulae.brew.sh/formula/leaf-markdown-viewer) et la documentation Apple sur les [LaunchAgents](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html).

## Dépendances et fichiers

| Outil | Utilisation |
|---|---|
| Zsh, Oh My Zsh | Shell interactif ; plugins `git`, `zsh-vi-mode`, `zsh-autosuggestions`, `history-substring-search` |
| tmux | Session persistante partagée et souris |
| Starship | Prompt épuré : dossier, Git, durée et indicateur du mode Vim |
| `eza` | Alias `ls`, `ll`, `la`, `tree` |
| `bat` (`batcat` sur Debian) | Alias `cat` et prévisualisation fzf |
| `ripgrep` (`rg`) | Alias `grep` |
| `fd-find` (`fdfind` ou `fd`) | Recherche de fichiers pour fzf |
| `fzf` | Recherche interactive de fichiers, dossiers et historique |
| `lf` | Gestionnaire de fichiers ; sa fonction shell conserve le dernier dossier |
| `less`, Git | Alias `glog`, `gadog` et plugin Git |
| `diffutils`, coreutils | Alias `diff --color=auto`, `df -h` et utilitaires système |
| Vim, Neovim (`nvim`) | Éditeurs ; `EDITOR` et `VISUAL` pointent vers Neovim |
| Leaf (`RivoLink/leaf`) | Lecture Markdown : `leaf README.md` |
| curl, certificats CA, Python 3, tar, xz, unzip | Téléchargements et installation |

Sur Linux, Starship et Leaf sont téléchargés via leurs installateurs officiels dans `~/.local/bin` lorsqu'ils sont absents. Neovim et les autres outils viennent des paquets système. Sur macOS, tous ces outils viennent de Homebrew. Les plugins externes sont clonés depuis `jeffreytse/zsh-vi-mode` et `zsh-users/zsh-autosuggestions`. `git` et `history-substring-search` sont inclus dans Oh My Zsh.

| Source | Destination |
|---|---|
| `zshrc` | `~/.zshrc` |
| `tmux.conf` | `~/.tmux.conf` |
| `tmux/status-identity.sh` | `~/.config/tmux/status-identity.sh` |
| `starship.toml` | `~/.config/starship.toml` |
| `codex-config.toml` | `~/.codex/config.toml` (permissions 600) |
| `vimrc` | `~/.vimrc` |
| `profile-snippet.sh` | Bloc géré dans `~/.profile` et `~/.zshrc` |
| `tmux-shared.service` (Linux) | `~/.config/systemd/user/tmux-shared.service` |
| LaunchAgent généré (macOS) | `~/Library/LaunchAgents/net.pav67.tmux-shared.plist` |
| `tmux/start-shared.sh` (macOS) | `~/.config/tmux/start-shared.sh` |

Neovim est installé sans configuration personnalisée ; `vimrc` reste réservé à Vim. L'ancien `headline.zsh-theme` reste archivé dans le dépôt mais n'est plus installé ni chargé. L'alias `dotfiles` suppose un dépôt bare personnel dans `~/.dotfiles` : le script ne le crée pas. Le chemin optionnel `~/.opencode/bin` est conservé ; OpenCode n'est pas installé par ce kit.

## Codex

Le fichier reprend les préférences du poste : modèle `gpt-6-astra`, raisonnement `medium`, `approval_policy = "never"`, sandbox `workspace-write` et accès réseau activé. Les animations, le titre avec spinner et les notifications BEL sont activés. La disponibilité du modèle dépend du compte utilisé.

Le kit copie uniquement les préférences : aucun jeton, historique, session, cache, plugin ni autorisation de confiance liée aux projets du poste source. Il remplace le fichier de préférences existant après sauvegarde. Codex CLI doit être installé et authentifié séparément. Les paramètres de référence sont décrits dans la [documentation officielle OpenAI](https://developers.openai.com/codex/config-reference/).

Dans tmux, les fenêtres Codex affichent le spinner du titre fourni par l'application. Une cloche marque les alertes des fenêtres inactives, sans son ; visiter la fenêtre acquitte l'alerte.

## Session persistante et SSH

Sur Linux, le service `systemd --user` crée la session `shared`. Le linger permet son démarrage au boot. Les connexions SSH interactives s'y attachent automatiquement, sauf si elles sont déjà dans tmux. Les transferts SCP/SFTP et les commandes SSH non interactives ne déclenchent pas cet attachement. Plusieurs appareils peuvent partager la session.

```bash
systemctl --user status tmux-shared.service
tmux ls
tmux attach -t shared
```

Pour choisir un autre nom, composé uniquement de lettres, chiffres, tirets et underscores :

```bash
TMUX_SHARED_SESSION=main ./install.sh
```

Le nom est enregistré dans le service et les deux blocs d'auto-attachement. Pour ouvrir ponctuellement un shell sans attachement :

```bash
ssh -t user@serveur 'TMUX=disabled zsh'
```

## Thèmes et identité réseau

Le prompt Starship tient sur une ligne, sans bulles ni utilisateur/hôte :

```text
…/work/configs on main !2 ?1 · 3s ❯
```

Dossier bleu, branche mauve, état Git ambre et durée grise (à partir de 2 secondes). Le chevron est vert après succès, rouge après erreur ; en mode Vim il devient `❮`, ambre en normal, mauve en visuel et orange en remplacement. Les segments Git et durée disparaissent lorsqu'ils ne s'appliquent pas.

Deux bulles séparées se trouvent à gauche dans tmux : `user hôte`. La bulle utilisateur a un fond gris ; celle de l'hôte utilise un fond coloré avec un texte sombre. Le nom système court détermine la couleur, sans distinction de majuscules/minuscules :

| Hôte | Couleur | Hex |
|---|---|---|
| `KL-central` (alias `klcentral`) | Bleu | `#89b4fa` |
| `codexops`, `kl-codex-runner` | Vert | `#a6e3a1` |
| `ai-node` (alias `ainode`) | Mauve | `#cba6f7` |
| `Debian-containers` | Cyan | `#89dceb` |
| `kl-ca` | Jaune | `#f9e2af` |
| `infra-core` | Pêche | `#fab387` |
| `kl-clients*` | Rose | `#f5c2e7` |
| Autres | Gris bleuté | `#a6adc8` |

Les noms ont été rapprochés des clients Omada le 16 octobre 2026. `KL-central`, `infra-core` et `kl-ca` sont annoncés comme noms d'hôtes ; `Debian-containers`, `ai-node` et `codexops` sont des libellés clients Omada. La correspondance entre `codexops` et le nom système local `kl-codex-runner` a été confirmée par l'adresse locale. Le nom système reste affiché dans la bulle. Aucun client `kl-clients*` n'était annoncé ; la règle demandée reste en place. Aucun appel Omada ni identifiant de connexion n'est nécessaire au thème.

L'utilisateur est blanc doux, **rouge pour root** (`#f38ba8`). Le script utilise `ps` (natif sur macOS ; paquet `procps` / `procps-ng` sur Linux) pour lire l'utilisateur du groupe de processus au premier plan du panneau actif, plutôt que celui mémorisé au démarrage de tmux. Un processus exécuté avec sudo peut donc faire apparaître root temporairement. En l'absence de processus détectable, `?` est affiché.

L'identité est locale au serveur tmux : un `ssh ainode` dans un panneau local ne transforme pas ce serveur en ainode. Pour afficher l'identité d'ainode, utiliser tmux sur ainode, avec ce kit installé. Hors tmux, le prompt ne contient pas d'identité, conformément au thème choisi.

Pour appliquer uniquement le thème sans réinstaller les dépendances :

```bash
# Sauvegarder d'abord les fichiers existants si besoin.
mkdir -p ~/.config/tmux
install -m 0755 tmux/status-identity.sh ~/.config/tmux/status-identity.sh
install -m 0644 tmux.conf ~/.tmux.conf
install -m 0644 starship.toml ~/.config/starship.toml
tmux source-file ~/.tmux.conf
```

Starship lit son fichier au prochain prompt. La palette tmux est modifiable dans `tmux/status-identity.sh`. Guide pratique : [le mode Vim dans Zsh](MODE-VIM-ZSH.md).

## Raccourcis Zsh

Les raccourcis personnalisés sont enregistrés après l'initialisation de `zsh-vi-mode` afin qu'il ne les écrase pas.

| Touche | Action |
|---|---|
| `Échap` | Passer en mode normal vi |
| `i` / `a` en mode normal | Insérer avant / après le curseur |
| `h`, `j`, `k`, `l`, `w`, `b` en mode normal | Déplacements vi |
| `Ctrl` + `→` / `←` | Mot suivant / précédent en mode insertion |
| `↑` / `↓` | Chercher dans l'historique selon le texte saisi |
| `Ctrl-R` | Recherche fzf dans l'historique |
| `Ctrl-T` | Choisir un fichier, y compris caché, avec aperçu bat |
| `Ctrl-F` | Choisir un fichier non caché avec aperçu bat |
| `Alt-C` | Choisir un dossier avec fzf |
| `Ctrl-\` | Activer / désactiver les autosuggestions |
| `Tab` | Complétion avec menu, sans distinction de casse |

L'historique partagé entre shells conserve jusqu'à 100 000 entrées dans `~/.cache/zsh/history`. La recherche fd respecte les exclusions Git par défaut, même avec l'option fichiers cachés.

## Raccourcis tmux

Les touches F2–F10 ci-dessous fonctionnent directement. Pour les autres, appuyer sur `Ctrl-b`, relâcher, puis sur la touche indiquée.

| Touche | Action |
|---|---|
| `F2` | Nouvelle fenêtre |
| `F3` / `F4` | Fenêtre précédente / suivante |
| `F10` | Fermer la fenêtre avec confirmation |
| `Ctrl-b c` | Nouvelle fenêtre |
| `Ctrl-b n` / `p` | Fenêtre suivante / précédente |
| `Ctrl-b 1`…`9` | Choisir une fenêtre |
| `Ctrl-b %` / `"` | Diviser en panneaux côte à côte / superposés |
| `Ctrl-b` puis flèche | Changer de panneau |
| `Ctrl-b z` | Agrandir / restaurer le panneau |
| `Ctrl-b [` | Mode copie et défilement, navigation vi |
| Espace puis Entrée en mode copie | Commencer la sélection puis copier dans le tampon tmux |
| `q` en mode copie | Quitter le mode copie |
| `Ctrl-b ]` | Coller le tampon tmux |
| `Ctrl-b d` | Détacher sans arrêter la session |
| `Ctrl-b ?` | Afficher tous les raccourcis |

La souris permet de sélectionner/redimensionner les panneaux et de parcourir l'historique (100 000 lignes par panneau). Fenêtres et panneaux sont numérotés à partir de 1. Les fenêtres sont renumérotées après fermeture. Le délai Escape reste à 100 ms pour les terminaux Windows.

## Vérification locale

```bash
bash -n install.sh
zsh -n zshrc
shellcheck -x install.sh lib/*.sh profile-snippet.sh tmux/*.sh
python3 tests/check_install.py
python3 tests/check_theme.py
python3 tests/check_native_identity.py
python3 tests/check_auto_attach.py
python3 tests/check_install_ui.py
python3 tests/check_wizard.py
```

Le test Python nécessite Python 3.11+ et Zsh. Il simule les opérations système et réseau Linux/macOS dans un HOME temporaire : il vérifie la réinstallation, les sauvegardes, les permissions et le nom de session, sans installer de paquets. Le test natif vérifie également la détection du premier plan avec le vrai `ps` dans un pseudo-terminal. Ces contrôles sont exécutés par GitHub Actions sur Linux et macOS ; ils ne remplacent pas un essai complet du LaunchAgent dans une session graphique réelle.

Les installateurs officiels sont documentés par [Starship](https://starship.rs/guide/) et [Leaf](https://github.com/RivoLink/leaf#install).
