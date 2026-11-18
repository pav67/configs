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
| Molette / touches volume | Volume ±5 %, maximum 100 % |
| Bouton muet / pression sur la molette (si configurée en Mute) | Couper / rétablir le son |
| Super + T | Kitty |
| Super + Q | Fermer la fenêtre active |
| Super + C | Chrome, sinon Chromium ou Firefox |
| Super + E | Thunar |
| Super + Espace | Ouvrir / fermer le lanceur d’applications |
| Super + R | Lanceur Fuzzel |
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

Cliphist conserve jusqu’à 2 000 copies de texte et d’images ; Super + V ouvre un panneau GTK sombre, avec recherche et défilement de tout l’historique. La hauteur des lignes suit le contenu : texte sur une à quatre lignes, miniature PNG/JPEG jusqu’à 320 × 160 pixels. Le panneau réserve une surface allant jusqu’à 1 000 × 1 000 pixels, selon l’écran, pour afficher plusieurs éléments à la fois. Le service reprend automatiquement après une interruption de la session ; les captures sont aussi ajoutées directement à l’historique. Sélectionner un élément le remet dans le presse-papiers et le colle automatiquement dans la fenêtre d’origine (Ctrl + V, ou Ctrl + Maj + V dans Kitty). Si la fenêtre active a changé, seul le presse-papiers est mis à jour. La sélection seule à la souris n’est pas surveillée. Le service ignore les contenus marqués confidentiels et les copies lorsque KeePassXC est la fenêtre active ; les applications ne marquant pas leurs secrets peuvent néanmoins les laisser dans cet historique local. `cliphist wipe` efface l’historique, mais conserve les favoris.

L’étoile ☆ (ou Ctrl + P) épingle un élément ; ★ le désépingle. Les favoris apparaissent en tête et leur contenu est conservé dans `~/.local/share/clipboard-pins` (ou `$XDG_DATA_HOME/clipboard-pins`), indépendamment de la rotation de l’historique. Épingler ne déclenche pas de collage. Entrée ou un clic sur la ligne colle ; Échap ferme le panneau.

Le panneau nécessite `python3-gi`, `gir1.2-gtk-3.0` et `gir1.2-gtklayershell-0.1`, inclus dans l’installateur Debian. Le lanceur accepte aussi les bibliothèques Debian extraites dans `~/.local/opt/clipboard-gtk`, pour une installation utilisateur sans droits administrateur.

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


## Thème sombre et panneau audio

Le clic sur le volume dans Waybar ouvre Pavucontrol en thème Adwaita sombre,
dans une fenêtre flottante centrée de 900 × 650. Thunar utilise le même thème
via Super + E, le lanceur et les ouvertures de dossiers par D-Bus/systemd.
L'installateur déploie les entrées utilisateur correspondantes, sans modifier
les fichiers système. Après réinstallation dans une session ouverte, exécuter
`systemctl --user daemon-reload` et rouvrir Thunar pour appliquer le thème.


### Classement des CR dans Obsidian et gestion des réunions

La liste du clic droit affiche `[Audio] Réunion du jj/mm/aaaa à hh:mm (durée)`
ou `[Transcript]` quand une transcription existe. La durée provient du WAV ; les
anciens enregistrements sont reconnus sans migration. Le sous-menu propose
**Supprimer la réunion**, avec confirmation explicite ; une réunion en cours de
capture ou de traitement ne peut pas être supprimée.

Après génération du CR, la fenêtre **Classer le CR dans Obsidian — Projet** propose
une liste de projets recherchable. Par défaut, elle lit le coffre ouvert dans
Obsidian et liste ses dossiers et sous-dossiers à tous les niveaux (hors dossiers cachés et liens).
Les chemins sont affichés, par exemple `Kitry/PARIS`, et sont recherchables.
Avec une configuration explicite, les sous-dossiers des projets déclarés sont également proposés.
Choisir un projet copie le CR sous `CR - AAAA-MM-JJ à HHhMMmSSs.md`, vérifie son
contenu et sa sauvegarde disque, puis supprime **tout le dossier d'enregistrement**
(audio, transcription, journaux et CR source). Un nom déjà utilisé reçoit un suffixe
numérique ; aucune note existante n'est écrasée. Annuler ou choisir **Plus tard**
conserve l'enregistrement. On peut reprendre via **Classer le CR dans Obsidian**
dans le sous-menu. Un export en échec conserve le dossier source.

Pour choisir explicitement les projets/dossiers, créer
`~/.config/reunion-audio/obsidian.json`, par exemple :

```json
{
  "vault": "/home/paul/obsidian/PaulWS",
  "projects": {
    "Kitry": "Kitry",
    "Perso": "Perso"
  }
}
```

Les chemins des projets sont relatifs au coffre et doivent rester à l'intérieur.
La configuration utilisateur n'est pas remplacée par l'installateur. Aucun
classement ni nettoyage des anciens enregistrements n'est effectué automatiquement
à l'installation. Le dernier export est référencé dans
`~/.local/state/reunion-audio/last-export.json`.

`python3 tests/check_reunion_lifecycle.py` vérifie les libellés, les états,
l'export, les collisions de noms, les erreurs disque et les protections de suppression.

Pendant la transcription, Waybar affiche `✎ 42 %`, à partir de la progression
réelle fournie par Whisper. Le pourcentage avance par paliers, pas forcément
linéairement dans le temps ; le chargement du modèle commence à 0 %. Pour une
transcription lancée avant cette mise à jour, `≈` signale une estimation à partir
des passages déjà transcrits. Le service en cours n'est pas redémarré.

Les deux touches personnalisables du Keychron identifiées comme `XF86Launch6`
et `XF86Launch7` produisent désormais respectivement `<` et `>`. Le fichier
`~/.config/xkb/keychron-fr.xkb` conserve AZERTY `fr/latin9` et les touches multimédias.
Il est appliqué uniquement au périphérique `keychron--keychron-link--keyboard` ;
Ctrl reste utilisable avec ces caractères. En cas de changement de connexion
USB/Bluetooth, vérifier le nom du périphérique avec `hyprctl devices`.


### Navigation dans les emails Outlook détachés

Depuis un message ouvert en fenêtre flottante, **Ctrl + touche personnalisable >**
ouvre le message suivant et **Ctrl + touche personnalisable <** le précédent.
Les bindings utilisent les codes physiques XKB 194 et 193 du Keychron.
`outlook-navigation` envoie Bas/Haut puis Maj + Entrée à la fenêtre principale
Outlook. Après apparition de la nouvelle fenêtre, il conserve la taille et la
position de la précédente, puis ferme celle-ci. Si aucune nouvelle fenêtre
n'apparaît sous 12 secondes, l'ancienne reste ouverte. Les frappes répétées pendant
une navigation sont ignorées.

Utiliser ces raccourcis en **lecture**, pas dans un brouillon. La fenêtre principale
doit rester ouverte sur la liste des messages avec la sélection correspondant au
message détaché. Une sélection changée manuellement dans la liste change le point
de départ de la navigation. Une seule fenêtre principale par compte/écran est
recommandée. Le comportement aux limites de la liste dépend d'Outlook. Hors d'une
fenêtre de message Outlook, Ctrl + < / > est retransmis à l'application active.
Les erreurs sont consignées dans `~/.local/state/outlook-navigation.log`.

Validation : `python3 tests/check_outlook_navigation.py` couvre la sélection de la
fenêtre principale, les deux sens, la conservation de l'ancien message en cas
d'échec et la transmission du raccourci aux autres applications.


## Verr Num et verrouillage de session (Keychron)

Installer une fois l'accès restreint au clavier avec :

```bash
bash ~/configs/desktop/install-numlock.sh
```

Ce script demande sudo, installe un outil root limité aux commandes `on` et `off`
sur les claviers physiques Keychron, une règle sudoers autorisant uniquement ces
deux appels, un service système d'arrêt et le réglage SDDM `Numlock=off`.
Il teste off/on sans verrouiller ni fermer la session. Le code root est installé
hors du HOME et exécuté par Python en mode isolé. Il ne permet pas d'injecter des
caractères arbitraires. Cette installation système est distincte de
`--configure-only`.

Super + L, le menu Waybar et le verrouillage automatique passent par
`verrouiller-session` : Verr Num est désactivé avant hyprlock, puis réactivé après
un déverrouillage réussi. Les actions de sortie de Waybar désactivent Verr Num
avant de quitter/redémarrer/éteindre. Le service système le désactive aussi avant
l'arrêt du gestionnaire d'affichage. Hyprland garde `numlock_by_default=true` pour
la nouvelle session et un appel `on` au démarrage ; SDDM demande l'état désactivé
sur l'écran de connexion. L'état après coupure d'alimentation ou dans le BIOS
reste contrôlé par le matériel.

Utiliser le raccourci/menu ou `~/.local/bin/verrouiller-session` pour verrouiller :
un appel direct à `hyprlock` ne passe pas par ces hooks. Sans l'installation
administrateur, le verrouillage reste possible mais Verr Num n'est pas modifié.
Les tests `tests/check_numlock_session.py` simulent les commandes sans agir sur
la session ni sur le matériel.

## Sons des Codex distants

Le [relais tmux](tmux-sounds/README.md) attribue un son aléatoire parmi 20 à chaque fenêtre distante, puis conserve ce son pour ses notifications suivantes.
