import QtQuick

Card {
    implicitHeight: Theme.geo.metricsHeight ?? 104
    Row {
        anchors.centerIn: parent
        spacing: 10
        Gauge {
            label: "CPU"
            value: Metrics.available ? Metrics.cpu : -1
            accent: Theme.mode === "dark" ? "#73AEF4" : Theme.brand.blue
        }
        Gauge {
            label: "RAM"
            value: Metrics.available ? Metrics.memory : -1
            accent: Theme.brand.red
        }
        Gauge {
            label: "Disk /"
            value: Metrics.available ? Metrics.disk : -1
            accent: Theme.mode === "dark" ? "#68C181" : Theme.brand.green
        }
    }
}
