# Configurations du poste

Kit personnel pour retrouver Zsh, tmux, Starship et les préférences Codex sur un nouveau poste Linux. Le README sert de spécification du comportement et des raccourcis.

## Installation

```bash
git clone https://github.com/pav67/configs.git ~/configs
cd ~/configs
./install.sh
```

Exécuter avec l'utilisateur final, sans `sudo` devant le script. Il utilise `sudo` pour les paquets, le shell par défaut et le linger systemd. Il faut un accès Internet et une session utilisateur systemd active. La cible de référence est Debian 13 ; des branches d'installation sont également prévues pour Fedora et Arch (non validées sur un poste réel). Les anciennes distributions peuvent ne pas fournir tous les paquets ; leur installation échoue explicitement dans ce cas. Sur Arch, le script effectue une mise à jour complète avec `pacman -Syu`.

Sélectionner une **Nerd Font dans le terminal client**, y compris pour les connexions SSH, pour afficher les icônes du prompt et de tmux.

Pour mettre à jour :

```bash
cd ~/configs
git pull
./install.sh
```

Les fichiers remplacés sont sauvegardés avec le suffixe `.bak.DATE-HEURE-PID`, notamment `.profile`, la configuration Codex et le service systemd. Les installations existantes de Starship, Leaf, Oh My Zsh et de ses plugins sont conservées. Les paquets suivent le gestionnaire de la distribution.

## Dépendances et fichiers

| Outil | Utilisation |
|---|---|
| Zsh, Oh My Zsh | Shell interactif ; plugins `git`, `zsh-vi-mode`, `zsh-autosuggestions`, `history-substring-search` |
| tmux | Session persistante partagée et souris |
| Starship | Prompt gris avec utilisateur, hôte, dossier, Git et durée |
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

Starship et Leaf sont téléchargés via leurs installateurs officiels dans `~/.local/bin` lorsqu'ils sont absents. Neovim et les autres outils viennent des paquets système. Les plugins externes sont clonés depuis `jeffreytse/zsh-vi-mode` et `zsh-users/zsh-autosuggestions`. `git` et `history-substring-search` sont inclus dans Oh My Zsh.

| Source | Destination |
|---|---|
| `zshrc` | `~/.zshrc` |
| `tmux.conf` | `~/.tmux.conf` |
| `starship.toml` | `~/.config/starship.toml` |
| `codex-config.toml` | `~/.codex/config.toml` (permissions 600) |
| `vimrc` | `~/.vimrc` |
| `profile-snippet.sh` | Bloc géré dans `~/.profile` et `~/.zshrc` |
| `tmux-shared.service` | `~/.config/systemd/user/tmux-shared.service` |

Neovim est installé sans configuration personnalisée ; `vimrc` reste réservé à Vim. L'ancien `headline.zsh-theme` reste archivé dans le dépôt mais n'est plus installé ni chargé. L'alias `dotfiles` suppose un dépôt bare personnel dans `~/.dotfiles` : le script ne le crée pas. Le chemin optionnel `~/.opencode/bin` est conservé ; OpenCode n'est pas installé par ce kit.

## Codex

Le fichier reprend les préférences du poste : modèle `gpt-6-astra`, raisonnement `medium`, `approval_policy = "never"`, sandbox `workspace-write` et accès réseau activé. Les animations, le titre avec spinner et les notifications BEL sont activés. La disponibilité du modèle dépend du compte utilisé.

Le kit copie uniquement les préférences : aucun jeton, historique, session, cache, plugin ni autorisation de confiance liée aux projets du poste source. Il remplace le fichier de préférences existant après sauvegarde. Codex CLI doit être installé et authentifié séparément. Les paramètres de référence sont décrits dans la [documentation officielle OpenAI](https://developers.openai.com/codex/config-reference/).

Dans tmux, les fenêtres Codex affichent le spinner du titre fourni par l'application. Une cloche marque les alertes des fenêtres inactives, sans son ; visiter la fenêtre acquitte l'alerte.

## Session persistante et SSH

Le service `systemd --user` crée la session `shared`. Le linger permet son démarrage au boot. Les connexions SSH interactives s'y attachent automatiquement, sauf si elles sont déjà dans tmux. Les transferts SCP/SFTP et les commandes SSH non interactives ne déclenchent pas cet attachement. Plusieurs appareils peuvent partager la session.

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
shellcheck install.sh profile-snippet.sh
python3 tests/check_install.py
```

Le test Python nécessite Python 3.11+ et Zsh. Il simule les opérations système et réseau dans un HOME temporaire : il vérifie la réinstallation, les sauvegardes, les permissions et le nom de session, sans installer de paquets. Il ne remplace pas un essai complet sur une machine vierge.

Les installateurs officiels sont documentés par [Starship](https://starship.rs/guide/) et [Leaf](https://github.com/RivoLink/leaf#install).
