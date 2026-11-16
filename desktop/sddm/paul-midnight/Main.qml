import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    width: 1920; height: 1080
    color: "#11111b"
    property bool busy: false
    function login() {
        if (!busy && username.text.length && password.text.length) {
            busy = true
            status.text = "Connexion…"
            sddm.login(username.text, password.text, sessions.currentIndex)
        }
    }
    gradient: Gradient {
        GradientStop { position: 0; color: "#11111b" }
        GradientStop { position: 1; color: "#28243d" }
    }
    Rectangle { width: 600; height: 600; radius: 300; x: -220; y: -280; color: "#cba6f7"; opacity: 0.035 }
    Rectangle { width: 800; height: 800; radius: 400; x: parent.width - 460; y: parent.height - 450; color: "#89b4fa"; opacity: 0.035 }
    Text {
        anchors { top: parent.top; left: parent.left; margins: 48 }
        text: "H Y P R L A N D"; color: "#cba6f7"; font { family: "Noto Sans"; pixelSize: 18; bold: true }
    }
    Text {
        anchors { top: parent.top; right: parent.right; margins: 48 }
        text: Qt.formatDateTime(new Date(), "ddd d MMMM · hh:mm")
        color: "#a6adc8"; font { family: "Noto Sans"; pixelSize: 16 }
        Timer { interval: 1000; running: true; repeat: true; onTriggered: parent.text = Qt.formatDateTime(new Date(), "ddd d MMMM · hh:mm") }
    }
    Rectangle {
        width: 440; height: form.implicitHeight + 80
        anchors.centerIn: parent
        radius: 24; color: "#1e1e2e"; border { color: "#45475a"; width: 1 }
        ColumnLayout {
            id: form
            anchors { left: parent.left; right: parent.right; top: parent.top; margins: 40 }
            spacing: 18
            Text { text: "Bienvenue"; color: "#cdd6f4"; font { family: "Noto Sans"; pixelSize: 32; bold: true } }
            Text { text: "Votre espace, prêt à vous retrouver."; color: "#a6adc8"; font.pixelSize: 14; Layout.bottomMargin: 10 }
            TextField {
                id: username; Layout.fillWidth: true; implicitHeight: 48
                text: userModel.lastUser; placeholderText: "Utilisateur"; color: "#cdd6f4"; font.pixelSize: 16
                background: Rectangle { color: "#181825"; radius: 10; border.color: username.activeFocus ? "#cba6f7" : "#45475a" }
                Keys.onReturnPressed: password.forceActiveFocus()
            }
            TextField {
                id: password; Layout.fillWidth: true; implicitHeight: 48
                placeholderText: "Mot de passe"; echoMode: TextInput.Password; color: "#cdd6f4"; font.pixelSize: 16
                background: Rectangle { color: "#181825"; radius: 10; border.color: password.activeFocus ? "#cba6f7" : "#45475a" }
                Keys.onReturnPressed: root.login()
                Component.onCompleted: forceActiveFocus()
            }
            ComboBox {
                id: sessions; Layout.fillWidth: true; implicitHeight: 44
                model: sessionModel; textRole: "name"; currentIndex: sessionModel.lastIndex
                palette { button: "#313244"; buttonText: "#cdd6f4"; base: "#181825"; text: "#cdd6f4"; highlight: "#cba6f7"; highlightedText: "#11111b" }
            }
            Button {
                Layout.fillWidth: true; implicitHeight: 48; enabled: !root.busy
                contentItem: Text { text: root.busy ? "Connexion…" : "Se connecter  →"; color: "#11111b"; font { pixelSize: 16; bold: true } horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                background: Rectangle { color: parent.down ? "#b4befe" : "#cba6f7"; radius: 10 }
                onClicked: root.login()
            }
            Text { id: status; text: ""; color: "#f38ba8"; wrapMode: Text.WordWrap; Layout.fillWidth: true; font.pixelSize: 13 }
        }
    }
    Row {
        spacing: 24
        anchors { horizontalCenter: parent.horizontalCenter; bottom: parent.bottom; bottomMargin: 40 }
        Button { text: "Redémarrer"; visible: sddm.canReboot; onClicked: sddm.reboot() }
        Button { text: "Éteindre"; visible: sddm.canPowerOff; onClicked: sddm.powerOff() }
    }
    Connections {
        target: sddm
        function onLoginFailed() { root.busy = false; status.text = "Connexion refusée. Vérifiez vos identifiants."; password.text = ""; password.forceActiveFocus() }
    }
}
