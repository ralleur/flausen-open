// SPDX-License-Identifier: MIT
#include <QApplication>
#include <QMenu>
#include <QActionGroup>
#include <QTimer>
int main(int argc, char **argv) {
    QApplication app(argc, argv);
    auto palette=app.palette();
    palette.setColor(QPalette::Window, QColor(app.arguments().contains("--light") ? "#f8f6f3" : "#1c1f21"));
    app.setPalette(palette);
    QMenu menu;
    auto add=[&](const char *icon, const char *label, const char *shortcut) {
        auto action=menu.addAction(QIcon::fromTheme(icon),QString::fromUtf8(label));
        action->setShortcut(QKeySequence(shortcut)); return action;
    };
    add("folder-new","Neuer Ordner","Ctrl+Shift+N");
    add("document-new","Neue Datei", "Ctrl+N");
    add("edit-paste","Einfügen","Ctrl+V")->setEnabled(false);
    menu.addSeparator();
    auto sort=menu.addMenu(QIcon::fromTheme("view-sort-ascending"),"Sortieren nach");
    QActionGroup group(sort);
    for(const auto &name : {"Name", "Änderungsdatum", "Typ", "Größe"}) {
        auto action=sort->addAction(QString::fromUtf8(name));
        action->setCheckable(true); group.addAction(action);
    }
    sort->actions().first()->setChecked(true);
    menu.addMenu(QIcon::fromTheme("view-list-icons"),"Ansicht")->addAction("Symbole");
    menu.addSeparator();
    add("edit-rename","Umbenennen","F2");
    add("edit-copy","Duplizieren","Ctrl+D");
    add("user-trash","In den Papierkorb","Delete");
    menu.addSeparator();
    add("document-properties","Eigenschaften","Alt+Return");
    menu.popup(QPoint(80,80));
    const auto idx=app.arguments().indexOf("--capture");
    if(idx>=0 && idx+1<argc) QTimer::singleShot(300,&menu,[&] {
        menu.grab().save(app.arguments().at(idx+1)); app.quit();
    });
    QObject::connect(&menu,&QMenu::aboutToHide,&app,&QApplication::quit);
    return app.exec();
}
