# tmux-shared-kit

Kit de configuration personnel pour déployer rapidement un environnement shell homogène sur un serveur Linux.

Il installe et configure :

- `tmux`
- `vim`
- `zsh`
- [Oh My Zsh](https://ohmyz.sh/)
- un thème Zsh personnalisé (`headline.zsh-theme`)
- une session tmux persistante créée automatiquement au boot
- l'attachement automatique à cette session lors d'une connexion SSH interactive

Le kit est conçu pour retrouver la même session de travail depuis plusieurs appareils : PC fixe, portable, téléphone, etc.

---

## Installation


```bash
git clone https://github.com/pav67/configs.git ~/configs \
  && cd ~/configs \
  && chmod +x install.sh \
  && ./install.sh
```

> Ne pas lancer `install.sh` avec `sudo`.
>
> Le script doit être exécuté avec l'utilisateur qui utilisera Zsh et tmux.
> Il demandera ponctuellement `sudo` pour installer les paquets, changer le shell par défaut et activer le `linger` systemd.


---

## Ce qui est installé

Les paquets suivants sont installés si nécessaire :

```text
tmux
vim
zsh
git
curl
python3
```

Oh My Zsh est cloné dans :

```text
~/.oh-my-zsh
```

Les fichiers de configuration sont installés dans :

```text
~/.tmux.conf
~/.vimrc
~/.zshrc
~/headline.zsh-theme
~/.config/systemd/user/tmux-shared.service
```

Les anciens fichiers sont sauvegardés avant remplacement :

```text
~/.tmux.conf.bak.YYYYMMDD-HHMMSS
~/.vimrc.bak.YYYYMMDD-HHMMSS
~/.zshrc.bak.YYYYMMDD-HHMMSS
~/headline.zsh-theme.bak.YYYYMMDD-HHMMSS
```

---

## Session tmux persistante

Par défaut, le script crée une session :

```text
shared
```

Elle est lancée via un service `systemd --user`.

Vérification :

```bash
systemctl --user status tmux-shared.service
```

Lister les sessions tmux :

```bash
tmux ls
```

Attachement manuel :

```bash
tmux attach -t shared
```

---

## Démarrage automatique au boot

Le script active :

```bash
sudo loginctl enable-linger "$USER"
```

Cela permet au service systemd utilisateur de démarrer dès le boot, même si l'utilisateur ne s'est pas encore connecté en SSH.

La session tmux `shared` est donc normalement déjà disponible lorsqu'une première connexion SSH arrive.

---

## Attachement automatique en SSH

Lors d'une connexion SSH interactive :

```bash
ssh user@serveur
```

le shell s'attache automatiquement à la session :

```text
shared
```

L'auto-attach n'est volontairement pas déclenché pour :

```bash
scp ...
rsync ...
sftp ...
ssh serveur "commande"
```

Il n'est pas non plus déclenché si le shell se trouve déjà dans une session tmux.

Plusieurs appareils peuvent être attachés simultanément à la même session.

---

## Bindings tmux supplémentaires

Les bindings tmux standards sont conservés.

Les raccourcis suivants sont ajoutés sans préfixe :

| Touche | Action |
|---|---|
| `F2` | Nouvelle fenêtre |
| `F3` | Fenêtre précédente |
| `F4` | Fenêtre suivante |
| `F10` | Fermer la fenêtre courante avec confirmation |

Les raccourcis standards restent disponibles, par exemple :

```text
Ctrl-b c    Nouvelle fenêtre
Ctrl-b n    Fenêtre suivante
Ctrl-b p    Fenêtre précédente
Ctrl-b [    Mode scroll / copie
Ctrl-b d    Détacher la session
```

La souris est activée dans tmux, ce qui permet notamment de remonter directement dans le scrollback avec la molette.

---

## Historique tmux

Chaque pane conserve jusqu'à :

```text
100000 lignes
```

Le scrollback peut être parcouru :

- à la molette ;
- avec `Ctrl-b [` ;
- avec les touches de navigation du mode copie.

---

## Zsh / Oh My Zsh

Le script configure Zsh comme shell par défaut :

```bash
chsh -s "$(command -v zsh)"
```

Le `.zshrc` fourni utilise Oh My Zsh et le thème :

```text
~/headline.zsh-theme
```

Plugins configurés :

```zsh
plugins=(git thefuck)
```

### Plugin `thefuck`

Le plugin Oh My Zsh est activé dans `.zshrc`, mais l'application `thefuck` elle-même n'est pas installée par ce kit.

Si elle est souhaitée, elle doit être installée séparément selon la distribution utilisée.

---

## Utiliser un autre nom de session tmux

Le nom par défaut est :

```text
shared
```

Pour utiliser par exemple `main` :

```bash
TMUX_SHARED_SESSION=main ./install.sh
```

Le service systemd et la session persistante utiliseront alors ce nom.

---

## Mise à jour sur un serveur

Depuis le dépôt cloné :

```bash
cd ~/tmux-shared-kit
git pull
./install.sh
```

Les fichiers existants seront sauvegardés avant réinstallation.

---

## Structure du dépôt

```text
.
├── README.md
├── install.sh
├── tmux.conf
├── vimrc
├── zshrc
├── headline.zsh-theme
├── profile-snippet.sh
└── tmux-shared.service
```

---

## Désactiver l'auto-attach tmux temporairement

Après connexion, il est possible de détacher la session avec :

```text
Ctrl-b d
```

Pour ouvrir ponctuellement un shell sans tmux :

```bash
ssh -t user@serveur 'TMUX=disabled zsh'
```

---

## Licence

Configuration personnelle, librement réutilisable et adaptable.
