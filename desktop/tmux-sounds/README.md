# Sons par fenêtre tmux distante

Le poste joue une mélodie courte parmi 20 WAV générés localement. Un tirage
aléatoire est effectué au premier signal d’une fenêtre ; cette attribution reste
stable pendant la vie de la fenêtre, même après reconnexion SSH ou redémarrage
du lecteur. Renommer la fenêtre ne change pas le son. Les 20 premières
attributions utilisent des sons différents ; au-delà, des réutilisations sont
possibles. Un nouveau serveur tmux crée de nouvelles identités de fenêtres.

Sur `codexops@192.168.80.120` :

- `events.py` est installé dans `~/.local/lib/tmux-sound-events.py`.
- `sounds.conf` est installé dans `~/.config/tmux/sounds.conf`, puis chargé à la
  fin de `~/.tmux.conf` avec `source-file ~/.config/tmux/sounds.conf`.
- Le hook `alert-bell[90]` transmet les identifiants des fenêtres via une file
  SQLite privée et bornée à 1 000 événements. Il ne lit aucun contenu de terminal.
- Les notifications BEL de Codex restent actives. `visual-bell on` empêche le
  son terminal standard de doubler la mélodie et conserve l’indication tmux.

Sur le poste Debian :

- `../lib/tmux_sounds.py` est installé dans `~/.local/lib/tmux_sounds.py`.
- `../systemd/tmux-sounds.service` est installé dans
  `~/.config/systemd/user/tmux-sounds.service`, puis activé avec
  `systemctl --user enable --now tmux-sounds.service` après `daemon-reload`.
- La connexion SSH utilise l’authentification par clé. Aucun sudo ni port
  entrant supplémentaire n’est nécessaire. Ajuster `--host` dans le service
  pour utiliser un autre serveur.
- Les sons se trouvent dans `~/.local/share/tmux-sounds/01.wav` à `20.wav`.
  On peut remplacer un fichier WAV pour personnaliser le catalogue.
- Les attributions sont dans `~/.local/state/tmux-sounds/assignments.json`.
- Pour écouter un son : `python3 ~/.local/lib/tmux_sounds.py --preview 8`.

Le relais démarre avec la session graphique et se reconnecte après une rupture
SSH. Il fonctionne également pour les fenêtres tmux détachées tant que le PC et
le relais restent actifs. Les événements antérieurs à une connexion ne sont pas
rejoués. Plusieurs fenêtres liées à des sessions différentes sont dédoublonnées
sur une fenêtre de 500 ms. Les confirmations de permission produisent aussi un
son si elles sont activées dans les notifications Codex.

Pour revenir à la cloche standard : arrêter/désactiver le service local,
retirer la ligne de chargement distante, puis exécuter dans tmux
`set-hook -gu 'alert-bell[90]'` et `set -g visual-bell off`.

Test sans réseau ni son : `python3 tests/check_tmux_sounds.py` depuis le dépôt.
