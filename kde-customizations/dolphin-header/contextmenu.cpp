// SPDX-License-Identifier: MIT
#include "contextmenu.h"
#include "smokematerial.h"
#include <QAction>
#include <QApplication>
#include <QKeyEvent>
#include <QMenu>
#include <KLocalizedString>
#include <KWindowEffects>
#include <QLocalSocket>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QScreen>
#include <QStyle>
#include <QPainterPath>
#include <QPainter>
#include <QTimer>
#include <QWindow>
#include <QCoreApplication>

namespace Ralleur {
namespace {
// Qt Widgets counterpart of TaskbarGlass: eight persistent, input-free native
// blur passes with stable buffers. Tooltips use xdg-positioner on Wayland, so
// unlike ordinary tool windows their positions can follow the native QMenu.
class BlurPass : public QWidget {
public:
    explicit BlurPass(QWidget *window)
        : QWidget(window, Qt::ToolTip | Qt::FramelessWindowHint
            | Qt::WindowTransparentForInput | Qt::WindowDoesNotAcceptFocus
            | Qt::NoDropShadowWindowHint)
    {
        setObjectName(QStringLiteral("ralleurContextBlurPass"));
        setAttribute(Qt::WA_TranslucentBackground);
        setAttribute(Qt::WA_ShowWithoutActivating);
        setProperty("ralleurGlassMenu", true);
        setProperty("_KDE_NET_WM_SKIP_SHADOW", true);
    }
protected:
    void paintEvent(QPaintEvent *) override {
        QPainter painter(this);
        painter.fillRect(0, 0, 1, 1, QColor(0, 0, 0, 1));
    }
};
}

class ContextGlass : public QObject {
public:
    explicit ContextGlass(QWidget *window) : QObject(window), parentWindow(window) {}
    QWidget *parentWindow;
    QPointer<QMenu> owner;
    QList<BlurPass *> passes;
    QSize capacity;
    QMetaObject::Connection destruction;
    void update(QMenu *menu) {
        const bool native = QGuiApplication::platformName() == QStringLiteral("wayland")
            || QGuiApplication::platformName() == QStringLiteral("xcb");
        if (!native) return;
        if (menu && owner != menu) {
            disconnect(destruction);
            owner = menu;
            destruction = connect(menu, &QObject::destroyed, this, [this] { update(nullptr); });
        }
        auto screen = menu ? menu->screen() : parentWindow->screen();
        const auto bounds = screen->geometry();
        const QRect target = menu ? menu->frameGeometry() : QRect(bounds.topLeft(), QSize(342, 500));
        // Reserve once and grow in buckets, never shrink buffers when menus close.
        capacity = capacity.expandedTo(QSize(
            qMin(bounds.width(), ((qMax(512, target.width()) + 63) / 64) * 64),
            qMin(bounds.height(), ((qMax(768, target.height()) + 63) / 64) * 64))).boundedTo(bounds.size());
        const QPoint origin(qBound(bounds.left(), target.x(), qMax(bounds.left(), bounds.right() + 1 - capacity.width())),
                            qBound(bounds.top(), target.y(), qMax(bounds.top(), bounds.bottom() + 1 - capacity.height())));
        QRegion region(QRect(-10, -10, 1, 1)); // Empty means whole-window blur in KWin.
        if (menu && menu->isVisible()) {
            QPainterPath path;
            path.addRoundedRect(QRect(target.topLeft() - origin, target.size()), 14, 14);
            region += QRegion(path.toFillPolygon().toPolygon());
        }
        if (passes.isEmpty()) {
            for (int i = 0; i < 8; ++i) passes.append(new BlurPass(parentWindow));
        }
        for (auto pass : passes) {
            pass->setGeometry(QRect(origin, capacity));
            pass->show();
            if (pass->windowHandle()) KWindowEffects::enableBlurBehind(pass->windowHandle(), true, region);
            pass->setProperty("ralleurContextBlurActive", menu && menu->isVisible());
        }
        if (!menu) { disconnect(destruction); owner.clear(); }
    }
};

namespace {
QString label(QString text)
{
    text.remove('&');
    text.remove(QChar(0x2026));
    if (text.endsWith(QStringLiteral("..."))) text.chop(3);
    return text.trimmed();
}

class ZipAction : public QAction {
public:
    ZipAction(QAction *native, QAction *zip, QMenu *owner)
        : QAction(native->icon(), QStringLiteral("zippen"), owner),
          m_native(native), m_zip(zip), m_options(native->menu())
    {
        setObjectName(QStringLiteral("ralleurZip"));
        connect(this, &QAction::triggered, this, [this] {
            if (!menu() && m_zip && m_zip->isEnabled()) m_zip->trigger();
        });
        connect(native, &QAction::changed, this, [this] { update(); });
        connect(zip, &QAction::changed, this, [this] { update(); });
    }
    void shift(bool pressed) {
        m_shift = pressed;
        if (!pressed && m_options && m_options->isVisible()) m_options->hide();
        setMenu(pressed ? m_options.data() : nullptr);
        update();
    }
private:
    void update() {
        setEnabled(m_native && m_native->isEnabled() && (m_shift || (m_zip && m_zip->isEnabled())));
    }
    QPointer<QAction> m_native, m_zip;
    QPointer<QMenu> m_options;
    bool m_shift = false;
};
}

ContextMenus::ContextMenus(QObject *parent) : QObject(parent), m_socket(new QLocalSocket(this))
{
    qApp->installEventFilter(this);
    connect(m_socket, &QLocalSocket::connected, this, &ContextMenus::syncBackdrop);
    const auto retry = [this] {
        if (!m_visible.isEmpty()) QTimer::singleShot(250, this, &ContextMenus::syncBackdrop);
    };
    connect(m_socket, &QLocalSocket::disconnected, this, retry);
    connect(m_socket, &QLocalSocket::errorOccurred, this, [retry](QLocalSocket::LocalSocketError) { retry(); });
    for (auto window : QApplication::topLevelWidgets()) {
        if (window->inherits("DolphinMainWindow") && window->isVisible()) {
            const QPointer<QWidget> guarded(window);
            QTimer::singleShot(250, this, [this, guarded] { if (guarded) prewarmGlass(guarded); });
        }
    }
}

void ContextMenus::prewarmGlass(QWidget *window)
{
    for (const auto &glass : m_glass)
        if (glass && glass->parentWindow == window) return;
    // Root and first submenu are warm before the first context-menu opening.
    for (int i = 0; i < 2; ++i) {
        auto glass = new ContextGlass(window);
        m_glass.append(glass);
        glass->update(nullptr);
    }
}

void ContextMenus::syncGlass(QMenu *menu)
{
    if (!menu->isVisible()) {
        for (const auto &glass : m_glass) if (glass && glass->owner == menu) glass->update(nullptr);
        return;
    }
    QWidget *window = m_active ? m_active->parentWidget() : nullptr;
    if (!window) return;
    window = window->window();
    for (const auto &glass : m_glass) {
        if (glass && glass->owner == menu) { glass->update(menu); return; }
    }
    for (const auto &glass : m_glass) {
        if (glass && glass->parentWindow == window && !glass->owner) { glass->update(menu); return; }
    }
    auto glass = new ContextGlass(window);
    m_glass.append(glass);
    glass->update(menu);
}

void ContextMenus::styleMenu(QMenu *menu)
{
    // Take over this menu from the shared opaque dialog skin before mapping it.
    menu->ensurePolished();
    menu->removeEventFilter(qApp->style());
    menu->setProperty("ralleurGlassMenu", true);
    menu->setAttribute(Qt::WA_TranslucentBackground);
    const bool light = menu->palette().color(QPalette::Window).lightness() >= 128;
    const QColor surface(QString::fromLatin1(light ? SmokeLight : SmokeDark));
    const auto surfaceCss = QStringLiteral("rgba(%1,%2,%3,%4)")
        .arg(surface.red()).arg(surface.green()).arg(surface.blue()).arg(surface.alpha());
    const auto css = QStringLiteral(R"(
QMenu { background: %1; color: %2; border: 1px solid %3; border-radius: 14px; padding: 8px; }
QMenu::item { padding: 10px 22px 10px 12px; border: 1px solid transparent; border-radius: 9px; }
QMenu::item:selected { background: %4; }
QMenu::item:disabled { color: %5; }
QMenu::separator { height: 1px; background: %3; margin: 8px 10px; }
QMenu::icon { margin-left: 8px; }
)").arg(surfaceCss,
        light ? "#20252d" : "#f3f4f6", light ? "rgba(255,255,255,102)" : "rgba(255,255,255,56)",
        light ? "rgba(0,0,0,16)" : "rgba(255,255,255,24)", light ? "#5b626d" : "#aeb6c2");
    menu->setProperty("ralleurDialogUpdating", true);
    if (menu->styleSheet() != css) menu->setStyleSheet(css);
    menu->setProperty("ralleurDialogUpdating", false);
}

bool ContextMenus::belongsToContext(QMenu *menu) const
{
    if (!m_active) return false;
    QList<QMenu *> pending{m_active};
    QSet<QMenu *> seen;
    while (!pending.isEmpty()) {
        auto current = pending.takeLast();
        if (current == menu) return true;
        if (seen.contains(current)) continue;
        seen.insert(current);
        for (auto action : current->actions()) if (action->menu()) pending.append(action->menu());
    }
    return false;
}

void ContextMenus::syncBackdrop()
{
    if (QGuiApplication::platformName() != QStringLiteral("wayland")
        && QGuiApplication::platformName() != QStringLiteral("xcb")) return;
    if (m_socket->state() == QLocalSocket::UnconnectedState) {
        if (m_visible.isEmpty()) return;
        m_socket->connectToServer(qEnvironmentVariable("XDG_RUNTIME_DIR") + "/ralleur-start-backdrop.sock");
        return;
    }
    if (m_socket->state() != QLocalSocket::ConnectedState) return;
    QJsonArray popups;
    for (auto menu : m_visible) {
        if (!menu->isVisible()) continue;
        const auto rect = menu->frameGeometry();
        popups.append(QJsonObject{{"x", rect.x()}, {"y", rect.y()},
                                 {"width", rect.width()}, {"height", rect.height()}});
    }
    const auto bytes = QJsonDocument(QJsonObject{
        {"owner", "dolphin:" + QString::number(QCoreApplication::applicationPid())},
        {"shown", !popups.isEmpty()}, {"cutouts", popups}}).toJson(QJsonDocument::Compact) + '\n';
    m_socket->write(bytes);
    m_socket->flush();
}

void ContextMenus::prepare(QMenu *menu, bool shift)
{
    if (menu->property("ralleurContextPrepared").toBool()) { setShift(menu, shift); return; }
    menu->setProperty("ralleurContextPrepared", true);
    for (auto action : menu->actions()) {
        const auto icon = action->icon().name();
        const auto text = label(action->text());
        const auto move = label(i18ndc("dolphin", "@action:inmenu", "Move to New Folder…"));
        if (action->objectName() == QStringLiteral("duplicate")
            || text == move
            || icon == QStringLiteral("tag") || icon == QStringLiteral("activities")) {
            // Remove only from this context menu; shared keyboard/menu actions survive.
            menu->removeAction(action);
            continue;
        }
        if (icon != QStringLiteral("archive-insert") || !action->menu()) continue;
        const auto choices = action->menu()->actions();
        // Ark 26.08: tar.gz, zip (when supported), custom archive dialog.
        // Leave unknown/new layouts untouched instead of running the wrong format.
        if (choices.size() != 3 || !choices[1]->text().contains(QStringLiteral("zip"))) continue;
        styleMenu(action->menu());
        auto replacement = new ZipAction(action, choices[1], menu);
        menu->insertAction(action, replacement);
        menu->removeAction(action);
        replacement->shift(shift);
    }
}

void ContextMenus::setShift(QMenu *menu, bool shift)
{
    for (auto action : menu->actions())
        if (auto zip = dynamic_cast<ZipAction *>(action)) zip->shift(shift);
}

bool ContextMenus::eventFilter(QObject *watched, QEvent *event)
{
    if (event->type() == QEvent::Show && watched->inherits("DolphinMainWindow")) {
        const QPointer<QWidget> window(qobject_cast<QWidget *>(watched));
        QTimer::singleShot(250, this, [this, window] {
            if (window && window->isVisible()) prewarmGlass(window);
        });
    }
    auto menu = qobject_cast<QMenu *>(watched);
    if (menu && event->type() == QEvent::Polish
        && (menu->inherits("DolphinContextMenu") || belongsToContext(menu))) {
        if (!menu->property("ralleurGlassHooked").toBool()) {
            menu->setProperty("ralleurGlassHooked", true);
            connect(menu, &QMenu::aboutToShow, this, [this, menu] {
                if (menu->inherits("DolphinContextMenu")) {
                    prepare(menu, QApplication::keyboardModifiers().testFlag(Qt::ShiftModifier));
                    m_active = menu;
                }
                QList<QMenu *> pending{menu};
                QSet<QMenu *> seen;
                while (!pending.isEmpty()) {
                    auto next = pending.takeLast();
                    if (seen.contains(next)) continue;
                    seen.insert(next);
                    styleMenu(next);
                    for (auto action : next->actions()) if (action->menu()) pending.append(action->menu());
                }
            });
        }
    }
    if (menu && event->type() == QEvent::Show) {
        if (menu->inherits("DolphinContextMenu")) {
            prepare(menu, QApplication::keyboardModifiers().testFlag(Qt::ShiftModifier));
            m_active = menu;
        }
        if (belongsToContext(menu)) {
            // Existing submenus were polished before the root popup mapped.
            // Lazy submenus inherit the same stylesheet from their parent menu.
            if (!menu->property("ralleurBackdropTracked").toBool()) {
                menu->setProperty("ralleurBackdropTracked", true);
                connect(menu, &QObject::destroyed, this, [this, menu] {
                    m_visible.remove(menu);
                    syncBackdrop();
                });
            }
            m_visible.insert(menu);
            syncGlass(menu);
        }
    }
    if (menu && menu->property("ralleurGlassMenu").toBool()
        && (event->type() == QEvent::Show || event->type() == QEvent::Resize)) {
        if (auto window = menu->windowHandle()) {
            QPainterPath shape;
            shape.addRoundedRect(menu->rect(), 14, 14);
            KWindowEffects::enableBlurBehind(window, true, QRegion(shape.toFillPolygon().toPolygon()));
        }
        QTimer::singleShot(0, this, &ContextMenus::syncBackdrop);
    }
    if (menu && event->type() == QEvent::Hide && m_visible.remove(menu)) {
        syncGlass(menu);
        if (menu == m_active) {
            for (const auto &glass : m_glass) if (glass && glass->owner) glass->update(nullptr);
            m_visible.clear();
        }
        syncBackdrop();
    }
    if (menu && (event->type() == QEvent::Move || event->type() == QEvent::Resize) && m_visible.contains(menu)) {
        syncGlass(menu);
        QTimer::singleShot(0, this, &ContextMenus::syncBackdrop);
    }
    if (m_active && m_active->isVisible()
        && (event->type() == QEvent::KeyPress || event->type() == QEvent::KeyRelease)) {
        auto key = static_cast<QKeyEvent *>(event);
        if (key->key() == Qt::Key_Shift && !key->isAutoRepeat())
            setShift(m_active, event->type() == QEvent::KeyPress);
    }
    return false;
}
}
