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


## Enregistrement des réunions

Le bouton **● Réunion** de Waybar capture le microphone par défaut et le son de la
sortie par défaut au moment du démarrage. Un clic démarre la capture ; le bouton
rouge affiche la durée. Un second clic arrête et propose **Transcrire maintenant
(français)**, **Ouvrir le dossier** ou **Plus tard**. Le clic droit retrouve les
réunions précédentes pour les ouvrir ou les transcrire. Échap ferme le menu sans
supprimer l'audio.

Les fichiers restent dans `~/Documents/Reunions/AAAA-MM-JJ_HH-MM-SS/` :
`micro.wav`, `interlocuteurs.wav`, `reunion.wav` (mixage), puis
`transcription.txt`, `.srt` et `.md`. Le son reçu comprend tous les sons de la sortie
choisie, y compris les notifications. Le microphone sélectionné doit être celui
du casque ; relever sa perche coupe ta voix mais laisse enregistrer les interlocuteurs.
Les sources restent fixes pendant la capture : arrêter et recommencer après un
changement de casque/sortie. Prévenir les participants de l'enregistrement.

Après installation des configurations, charger le service avec
`systemctl --user daemon-reload` et recharger Waybar. La capture utilise `parec`
(paquet `pulseaudio-utils`), Python 3 et le serveur PipeWire/PulseAudio existant.
Il n'y a pas d'enregistrement automatique à la connexion.

Pour préparer la transcription une fois :

```bash
sudo apt install cmake g++ make git curl
~/.local/bin/installer-whisper-reunion
```

L'installateur compile whisper.cpp v1.9.5 et télécharge le modèle multilingue
`small` (~466 Mio). Ensuite, la transcription est locale, en français, avec quatre
threads CPU et une priorité réduite. Le temps de traitement dépend de la durée
et du processeur ; les intervenants ne sont pas identifiés automatiquement.
L'audio reste disponible si une transcription échoue. `whisper.log` contient les
détails et le clic droit permet de réessayer. Les données ne sont jamais ajoutées
au dépôt.

La capture conserve les deux pistes et le mixage (environ 350 Mo par heure).
Elle s'arrête si l'espace libre devient inférieur à 256 Mio ou après 12 heures.
Un arrêt normal du service finalise les WAV ; une coupure brutale peut empêcher
la création du mixage, mais les pistes déjà écrites restent dans le dossier.

Validation : `python3 tests/check_reunion.py` teste deux sources synthétiques,
l'arrêt propre, le mixage et l'export de transcription, sans capter un micro réel.


### Compte rendu sur le serveur IA local

Après une transcription, un menu propose **Générer le compte rendu**, **Ouvrir le
dossier** ou **Plus tard**. Le clic droit sur le bouton Réunion permet aussi de
sélectionner une réunion déjà transcrite et de demander son compte rendu.
Le texte transcrit est envoyé uniquement après ce choix au serveur configuré dans
`~/.config/reunion-audio/ai.json` (par défaut `http://192.168.80.109:1234/v1`, modèle
`Qwen3.8-27B`). L'audio reste sur le poste. La configuration est préservée lors des
réinstallations ; adapter `base_url`, `model` et `timeout` si nécessaire.

Le résultat est écrit dans **CR.md**, dans le dossier de la réunion : synthèse,
points abordés, décisions, tableau des actions et questions ouvertes. Relire le
compte rendu, notamment les décisions et les noms. En cas de régénération, l'ancien
CR est sauvegardé sous `CR.DATE-HEURE.bak.md`. En cas de serveur indisponible ou de
réponse tronquée, l'ancien CR et la transcription sont conservés ; réessayer depuis
le clic droit. La barre affiche « Compte rendu » pendant la génération. Le délai
maximal d'attente réseau est de 600 secondes, et les transcriptions de plus de
500 000 caractères sont refusées explicitement, sans troncature silencieuse.

Validation : `python3 tests/check_reunion_report.py` vérifie la requête, l'écriture,
la sauvegarde et la conservation du CR en cas d'échec ou de réponse incomplète.


## Emails Outlook dans Chrome

`outlook-flottant` écoute les événements Hyprland : une fenêtre Chrome créée avec
le titre `about:blank - Google Chrome`, puis portant un titre terminé par
` – Outlook - Google Chrome`, est rendue flottante et centrée (1100 × 900 au maximum,
adapté à l'écran). La boîte de réception principale reste en mosaïque. Chaque
fenêtre est traitée une seule fois pour respecter les changements manuels ultérieurs.
Le programme démarre avec Hyprland ; après une installation sans reconnexion,
lancer `~/.local/bin/outlook-flottant`. Super + Maj + V permet toujours de changer
manuellement le mode d'une fenêtre. Si Chrome ou Outlook modifie ses titres,
le critère devra être adapté.
