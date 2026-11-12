// SPDX-License-Identifier: MIT
#include <QApplication>
#include <QCheckBox>
#include <QMessageBox>
#include <QPushButton>
#include <QTimer>
#include <QStyleFactory>
int main(int argc, char **argv) {
    QApplication app(argc, argv);
    const bool light = app.arguments().contains("--light");
    QPalette palette = app.palette();
    palette.setColor(QPalette::Window, QColor(light ? "#f8f6f3" : "#1c1f21"));
    palette.setColor(QPalette::WindowText, QColor(light ? "#161616" : "#f4f3f1"));
    app.setPalette(palette);
    QMessageBox box(QMessageBox::Warning, "Ralleur · Dialogvorschau", "In den Papierkorb verschieben?", QMessageBox::NoButton);
    box.setInformativeText("„Projektentwurf.pdf“ wird in den Papierkorb verschoben\nund kann von dort wiederhergestellt werden.");
    box.setCheckBox(new QCheckBox("Für diesen Dateityp nicht erneut fragen"));
    box.addButton("Mehr erfahren", QMessageBox::HelpRole);
    auto cancel = box.addButton(QMessageBox::Cancel); cancel->setText("Abbrechen");
    box.addButton("In den Papierkorb", QMessageBox::DestructiveRole);
    box.setDefaultButton(cancel);
    box.show();
    // Preview buttons have no file operations attached.
    const int index = app.arguments().indexOf("--capture");
    if (index >= 0 && index + 1 < argc) QTimer::singleShot(300, &box, [&] {
        box.grab().save(app.arguments().at(index + 1)); app.quit();
    });
    return app.exec();
}
