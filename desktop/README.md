# Bureau Hyprland

Configuration du poste Debian 13 mise en place le 13 novembre 2026. Ce module est indépendant de l'installateur terminal à la racine : il ne s'installe donc pas sur les serveurs SSH avec `./install.sh --all`.

## Installer

Avec votre utilisateur, sans `sudo` devant le script :

```bash
./desktop/install.sh
```

Le dépôt Debian `trixie-backports` avec le composant `main` doit être actif. L'installateur le vérifie, mais ne modifie pas les sources APT. Les paquets du bureau sont installés depuis Debian et ses backports ; les pilotes NVIDIA et Google Chrome ne sont pas installés par ce script. Chrome déjà présent est utilisé ; sinon Chromium est installé.

Pour retrouver aussi l'écran de connexion et l'agencement du poste à trois écrans :

```bash
./desktop/install.sh --sddm --monitors-paul
```

`--sddm` installe le thème Qt6 bleu nuit/lavande, le clavier français du greeter et active SDDM au prochain démarrage. Le gestionnaire n'est pas démarré ni redémarré pendant l'installation. Cette option sert à choisir SDDM comme gestionnaire de connexion ; ne pas l'utiliser pour conserver un autre gestionnaire.

`--monitors-paul` applique, de gauche à droite, **DP-7 → DP-4 → DP-6**, en 3840×2160 à 60 Hz avec une échelle de 150 %. Sans cette option, une disposition automatique est créée uniquement si `~/.config/hypr/monitors.conf` n'existe pas. Adapter ce fichier aux connecteurs du nouveau poste.

Pour copier uniquement les configurations, sans paquets ni modification système :

```bash
./desktop/install.sh --configure-only
```

Les fichiers remplacés sont sauvegardés avec un suffixe `.bak.DATE-HEURE-PID`. Les chemins sont adaptés à votre HOME. Reconnectez-vous ensuite pour lancer les services et le fond d'écran. Sous une autre distribution, installez préalablement les programmes utilisés avant de choisir `--configure-only`.

## Contenu

- Hyprland : AZERTY français `fr/latin9`, Verr Num activé au démarrage de la session, raccourcis fenêtres, suppression du texte sur le fond par défaut.
- Keychron Q6 Max : **sélecteur matériel sur Win**, sans échange logiciel Alt/Super ; AltGr donne `@` avec `0`, `[` avec `5` et `]` avec `)`.
- Fuzzel : Super + Espace, thème bleu nuit/lavande, police Noto Sans et coins arrondis. Marges intérieures de 28 px à gauche/droite et 24 px en haut/bas, avec 16 px entre recherche et résultats ; réglables dans `~/.config/fuzzel/fuzzel.ini`.
- Waybar : thème sombre lavande, liste des fenêtres propres à chaque écran, horloge, CPU, mémoire, réseau, volume, zone de notification et menu de session.
- Fond voie lactée, affiché par swaybg et repris avec flou par hyprlock.
- Hyprlock : déverrouillage avec le mot de passe Linux, via PAM.
- Hypridle : verrouillage à **180 secondes**, extinction des écrans à **300 secondes**, rallumage à la reprise d'activité. Modifier `~/.config/hypr/hypridle.conf` pour changer les délais. Les applications qui inhibent l'inactivité peuvent retarder ces actions.
- Thunar, gestion des archives et des emplacements réseau ; PipeWire et contrôle du volume.
- Grim/Slurp : captures PNG dans `~/Images/Captures`, également copiées dans le presse-papiers. Échap annule la sélection d'une zone.
- SDDM : thème léger `paul-midnight`, en option.

Le kit ne contient ni `.env`, ni base KeePass, ni clés SSH, ni profils de navigateur. L'ancien fichier XKB créé pour compenser le mode Mac du clavier n'est plus nécessaire et n'est pas installé.

## Raccourcis

Super correspond à la touche Windows.

| Raccourci | Action |
|---|---|
| Super + T | Kitty |
| Super + Q | Fermer la fenêtre active |
| Super + C | Chrome, sinon Chromium ou Firefox |
| Super + E | Thunar |
| Super + Espace | Ouvrir / fermer le lanceur d’applications |
| Super + R | Lanceur Fuzzel |
| Super + M | Menu de sortie Hyprland, ou fin de session |
| Super + L | Verrouiller |
| Super + V | Historique du presse-papiers |
| Super + Maj + V | Flottante / mosaïque |
| Super + F | Plein écran |
| Super + flèches | Sélectionner une fenêtre voisine |
| Super + Maj + flèches | Déplacer une fenêtre |
| Super + Ctrl + flèches | Redimensionner par pas de 40 pixels |
| Super + glisser avec clic gauche / droit | Déplacer / redimensionner |
| Impr. écran | Capturer tous les écrans |
| Super + Maj + S | Capturer une zone |

Pour tmux via SSH, **F2/F3/F4 fonctionnent directement lorsque le Q6 Max est en mode Win**.

## Validation

```bash
bash -n desktop/install.sh desktop/bin/*
python3 tests/check_desktop.py
```

Le test installe les fichiers dans un HOME temporaire, vérifie les sauvegardes, les chemins, le clavier, la sélection des écrans et la liste de fenêtres Waybar. Il ne lance aucun service et n'installe aucun paquet. L'affichage a été utilisé sur Hyprland 0.55.2, Waybar 0.12 et Debian 13 ; l'installation complète sur un poste vierge reste à valider.

## Presse-papiers

Cliphist conserve les copies de texte et d’images ; Super + V ouvre leur historique dans Fuzzel. Sélectionner un élément le remet dans le presse-papiers, puis Ctrl + V (Ctrl + Maj + V dans Kitty) le colle. La sélection seule à la souris n’est pas surveillée. Le service ignore les contenus marqués confidentiels et les copies lorsque KeePassXC est la fenêtre active ; les applications ne marquant pas leurs secrets peuvent néanmoins les laisser dans cet historique local. `cliphist wipe` efface l’historique.

## Réveil des écrans

Le réveil DPMS est activé directement dans Hyprland pour le clavier et la souris, en plus des commandes `on-resume` des deux règles hypridle. Cela évite de dépendre uniquement du listener d’extinction, dont l’événement de reprise peut être manqué après une inhibition. Les délais de verrouillage et d’extinction restent à 3 et 5 minutes.
