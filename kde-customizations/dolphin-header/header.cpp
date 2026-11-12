#include <KLocalizedString>
#include "../window-controls/controls.h"
// SPDX-License-Identifier: MIT
#include "header.h"
#include "foldercolors.h"
#include "quickpreview.h"
#include "contextmenu.h"
#include <KWindowShadow>
#include <KAboutData>
#include <KIconLoader>
#include <KIconTheme>
#include <KActionCollection>
#include <KXmlGuiWindow>
#include <QAbstractItemView>
#include <QAbstractButton>
#include <QApplication>
#include <QDBusConnection>
#include <QEvent>
#include <QHBoxLayout>
#include <QMainWindow>
#include <QDialog>
#include <QScreen>
#include <QListView>
#include <QLineEdit>
#include <QTextEdit>
#include <QPlainTextEdit>
#include <QComboBox>
#include <QAbstractScrollArea>
#include <QGraphicsView>
#include <QGraphicsScene>
#include <KUrlNavigator>
#include <QMouseEvent>
#include <QPainter>
#include <QPainterPath>
#include <QStyle>
#include <QProxyStyle>
#include <QSettings>
#include <QStandardPaths>
#include <QFileInfo>
#include <QSurfaceFormat>
#include <QTimer>
#include <QToolBar>
#include <QToolButton>
#include <QTabBar>
#include <QTabWidget>
#include <QWidgetAction>
#include <QWindow>
#include <cmath>

namespace Ralleur {
namespace {
constexpr int Radius = 12;
constexpr int EdgeWidth = 5;

class WindowControlButton : public QToolButton {
public:
    WindowControlButton(RalleurControls::Symbol symbol, QWidget *parent)
        : QToolButton(parent), m_symbol(symbol) { setMouseTracking(true); }
protected:
    void paintEvent(QPaintEvent *) override {
        QPainter p(this);
        RalleurControls::paint(p, QRectF(rect()), m_symbol,
            palette().color(QPalette::Active, QPalette::WindowText),
            window()->isActiveWindow(), underMouse(), isDown());
        if (hasFocus()) {
            p.setPen(QPen(palette().color(QPalette::Highlight), 1));
            p.setBrush(Qt::NoBrush);
            p.drawRoundedRect(QRectF(rect()).adjusted(1,1,-1,-1), 4,4);
        }
    }
private:
    RalleurControls::Symbol m_symbol;
};


class PlacesMetricsStyle : public QProxyStyle {
public:
    explicit PlacesMetricsStyle(QStyle *base) : QProxyStyle(base) { setProperty("ralleurPlacesMetrics", true); }
    QSize sizeFromContents(ContentsType type, const QStyleOption *option, const QSize &contents,
                          const QWidget *widget = nullptr) const override {
        auto size = QProxyStyle::sizeFromContents(type, option, contents, widget);
        // KDE's native Places delegate asks QApplication::style(), bypassing
        // the view-local stylesheet. Keep its previous 12 px row padding here
        // without a global stylesheet or replacing the native delegate.
        if (type == CT_ItemViewItem && widget && widget->inherits("KFilePlacesView")) size.rheight() += 12;
        return size;
    }
};

void ensurePlacesMetrics()
{
    if (!qApp->style()->property("ralleurPlacesMetrics").toBool())
        qApp->setStyle(new PlacesMetricsStyle(qApp->style()));
}

void configurePlaces(QWidget *window)
{
    for (auto view : window->findChildren<QListView *>()) {
        if (!view->inherits("KFilePlacesView") || view->property("ralleurSpacing").toBool()) continue;
        view->setProperty("ralleurSpacing", true);
        view->setIconSize(QSize(16, 16));
        // Keep KDE's delegate and its hit testing intact. Horizontal list
        // spacing breaks KIO's fixed text inset; vertical padding lives in
        // the application's scoped Qt stylesheet instead.
        view->setSpacing(0);
        // Scope spacing to Places. An application-wide stylesheet wraps every
        // widget's style and can retain old navigation/tab palette brushes.
        view->setStyleSheet(view->styleSheet() + QStringLiteral(
            "\nKFilePlacesView { background-color: transparent; border: none; padding-left: 8px; padding-right: 6px; }\n"));
    }
}

KWindowShadowTile::Ptr tile(const QImage &image, const QRect &rect)
{
    auto result = KWindowShadowTile::Ptr::create();
    result->setImage(image.copy(rect));
    return result;
}
}

Header::Header(QWidget *window, QToolBar *toolbar)
    : QObject(window), m_window(window), m_toolbar(toolbar)
{
    setObjectName(QStringLiteral("ralleurHeader"));
    ensureControls();
    // No persistent KWin rule hides titlebars. If loading the plugin fails,
    // unmodified Dolphin keeps its ordinary, usable window decoration.
    const bool visible = window->isVisible();
    const auto state = window->windowState();
    const auto geometry = window->geometry();
    window->setAttribute(Qt::WA_TranslucentBackground);
    window->setAutoFillBackground(false);
    window->setWindowFlag(Qt::FramelessWindowHint, true);
    // Changing WA_TranslucentBackground after a surface was created does not
    // change its pixel format (QTBUG-85714). Recreate that surface if needed;
    // otherwise transparent corner pixels are presented as opaque black.
    if (auto native = window->windowHandle(); native && native->format().alphaBufferSize() < 8) {
        window->hide();
        native->destroy();
        auto format = native->requestedFormat();
        format.setAlphaBufferSize(8);
        native->setFormat(format);
    }
    window->setContentsMargins(1, 1, 1, 1);
    window->setMouseTracking(true);
    qApp->installEventFilter(this);
    toolbar->setMovable(false);
    toolbar->setFloatable(false);
    toolbar->setMinimumHeight(40);
    if (visible) {
        window->setGeometry(geometry);
        window->setWindowState(state);
        window->show();
    }
    configurePlaces(window);
    const auto policy = FolderPolicy::load(QStandardPaths::writableLocation(QStandardPaths::GenericConfigLocation)
        + QStringLiteral("/ralleur-dolphin/folder-colors.json"));
    if (policy.valid() && window->inherits("DolphinMainWindow")) m_colors = new FolderColors(policy,
        QStandardPaths::writableLocation(QStandardPaths::GenericStateLocation)
            + QStringLiteral("/ralleur-desktop-tweaks/folder-icon-changes"), this);
    configureContents();
    if (auto mainWindow = qobject_cast<QMainWindow *>(window)) m_preview = new QuickPreview(mainWindow);
    updateFrame();
    const QString path = QStringLiteral("/org/ralleur/DolphinHeader/%1").arg(window->objectName().replace('#', '_'));
    QDBusConnection::sessionBus().registerObject(path, this,
        QDBusConnection::ExportAllSlots | QDBusConnection::ExportAllProperties);
    QTimer::singleShot(0, this, &Header::createShadow);
}

bool Header::maximized() const { return m_window && m_window->isMaximized(); }
bool Header::decorated() const { return m_window && !m_window->windowFlags().testFlag(Qt::FramelessWindowHint); }
bool Header::shadowCreated() const { return m_shadow && m_shadow->isCreated(); }
int Header::alphaBufferSize() const { return m_window && m_window->windowHandle() ? m_window->windowHandle()->format().alphaBufferSize() : -1; }
void Header::minimize() { if (m_minimize) m_minimize->click(); }
void Header::maximizeRestore() { if (m_maximize) m_maximize->click(); }
void Header::closeWindow() { if (m_close) m_close->click(); }

void Header::ensureControls()
{
    if (!m_window || !m_toolbar || m_adjusting || QCoreApplication::closingDown()) return;
    m_adjusting = true;
    if (!m_action) {
        auto group = new QWidget(m_toolbar);
        group->setObjectName(QStringLiteral("ralleurWindowControls"));
        auto layout = new QHBoxLayout(group);
        layout->setContentsMargins(10, 0, 5, 0);
        layout->setSpacing(RalleurControls::Gap);
        auto button = [&](const QString &name, const QString &label, QStyle::StandardPixmap icon) {
            const auto symbol = icon == QStyle::SP_TitleBarMinButton ? RalleurControls::Symbol::Minimize
                : icon == QStyle::SP_TitleBarMaxButton ? RalleurControls::Symbol::Maximize : RalleurControls::Symbol::Close;
            auto item = new WindowControlButton(symbol, group);
            item->setObjectName(name);
            item->setAccessibleName(label);
            item->setToolTip(label);
            item->setAutoRaise(true);
            item->setFocusPolicy(Qt::StrongFocus);
            const QString themeName = icon == QStyle::SP_TitleBarMinButton ? QStringLiteral("window-minimize")
                : icon == QStyle::SP_TitleBarMaxButton ? QStringLiteral("window-maximize") : QStringLiteral("window-close");
            item->setIcon(KDE::icon(themeName));
            item->setIconSize(QSize(16, 16));
            item->setFixedSize(30, 30);
            layout->addWidget(item);
            return item;
        };
        m_minimize = button(QStringLiteral("ralleurMinimize"), i18nd("flausen", "Minimize"), QStyle::SP_TitleBarMinButton);
        m_maximize = button(QStringLiteral("ralleurMaximize"), i18nd("flausen", "Maximize"), QStyle::SP_TitleBarMaxButton);
        m_close = button(QStringLiteral("ralleurClose"), i18nd("flausen", "Close"), QStyle::SP_TitleBarCloseButton);
        connect(m_minimize, &QToolButton::clicked, m_window, &QWidget::showMinimized);
        connect(m_maximize, &QToolButton::clicked, this, [this] {
            if (!m_window) return;
            if (m_window->isMaximized()) m_window->showNormal();
            else m_window->showMaximized();
        });
        connect(m_close, &QToolButton::clicked, m_window, &QWidget::close);
        auto action = new QWidgetAction(m_toolbar);
        action->setObjectName(QStringLiteral("ralleurWindowControlsAction"));
        action->setDefaultWidget(group);
        m_action = action;
    }
    if (m_toolbar->actions().isEmpty() || m_toolbar->actions().last() != m_action) {
        m_toolbar->removeAction(m_action);
        m_toolbar->addAction(m_action);
    }
    m_adjusting = false;
    configureContents();
}

void Header::configureContents()
{
    if (!m_window || !m_toolbar) return;
    ensurePlacesMetrics();
    // Keep themed action/tool icons on KDE's palette-aware SVG engine, even
    // when Qt's platform theme initially created plain SVG icon engines.
    auto themedIcon = [](auto object) {
        const auto icon = object->icon();
        const auto name = icon.name();
        if (name.isEmpty() || object->property("ralleurThemedIconKey").toULongLong() == quint64(icon.cacheKey())) return;
        object->setIcon(KDE::icon(name));
        object->setProperty("ralleurThemedIconKey", qulonglong(object->icon().cacheKey()));
    };
    if (auto native = qobject_cast<KXmlGuiWindow *>(m_window.data()))
        for (auto action : native->actionCollection()->actions()) themedIcon(action);
    for (auto button : m_toolbar->findChildren<QToolButton *>()) themedIcon(button);
    for (auto button : m_toolbar->findChildren<QToolButton *>()) {
        auto action = button->defaultAction();
        if (!action || (action->objectName() != "go_back" && action->objectName() != "go_forward")) continue;
        if (!button->property("ralleurPlainHistory").toBool()) {
            button->setProperty("ralleurPlainHistory", true);
            button->setStyleSheet(QStringLiteral("QToolButton::menu-indicator { image: none; width: 0px; height: 0px; }"));
        }
    }
    auto tint = [](QWidget *widget) {
        // Rebuild from the current application palette, including foreground,
        // selection and alternate rows. Never copy a previously tinted palette.
        auto palette = QApplication::palette(widget);
        for (const auto group : {QPalette::Active, QPalette::Inactive, QPalette::Disabled}) {
            auto base = palette.color(group, QPalette::Base);
            if (base.lightness() < 100) base = QColor(qMin(255, base.red()+10), qMin(255, base.green()+10), qMin(255, base.blue()+10), base.alpha());
            palette.setColor(group, QPalette::Base, base);
        }
        if (widget->palette() != palette) widget->setPalette(palette);
    };
    auto followTheme = [](QWidget *widget) {
        const auto palette = QApplication::palette(widget);
        if (widget->palette() != palette) widget->setPalette(palette);
    };
    followTheme(m_toolbar);
    for (auto widget : m_toolbar->findChildren<QWidget *>()) followTheme(widget);
    for (auto view : m_window->findChildren<QWidget *>()) {
        if (view->inherits("KFilePlacesView")) {
            followTheme(view);
            if (auto area = qobject_cast<QAbstractScrollArea *>(view)) followTheme(area->viewport());
        }
        if (qobject_cast<QLineEdit *>(view) || qobject_cast<QTextEdit *>(view) || qobject_cast<QPlainTextEdit *>(view)) {
            followTheme(view);
            if (auto area = qobject_cast<QAbstractScrollArea *>(view)) followTheme(area->viewport());
        }
        if (qobject_cast<KUrlNavigator *>(view) || qobject_cast<QTabBar *>(view) || qobject_cast<QTabWidget *>(view)) {
            followTheme(view);
            // A tab widget also owns the file views, so only refresh descendants
            // of the navigation bar and tab bar as chrome.
            if (!qobject_cast<QTabWidget *>(view))
                for (auto child : view->findChildren<QWidget *>()) followTheme(child);
        }
        if (!view->inherits("DolphinView")) continue;
        tint(view);
        for (auto area : view->findChildren<QAbstractScrollArea *>()) { tint(area); tint(area->viewport()); }
        for (auto graphics : view->findChildren<QGraphicsView *>()) {
            if (!graphics->scene()) continue;
            const auto palette = graphics->palette();
            if (graphics->scene()->palette() != palette) graphics->scene()->setPalette(palette);
        }
    }
    if (m_colors) for (auto navigator : m_window->findChildren<KUrlNavigator *>()) m_colors->bind(navigator);
    if (m_preview) m_preview->bindViews();
}

Qt::Edges Header::resizeEdges(const QPointF &position) const
{
    if (!m_window || m_window->isMaximized() || m_window->isFullScreen()) return {};
    Qt::Edges edges;
    if (position.x() < EdgeWidth) edges |= Qt::LeftEdge;
    if (position.x() > m_window->width() - EdgeWidth) edges |= Qt::RightEdge;
    if (position.y() < EdgeWidth) edges |= Qt::TopEdge;
    if (position.y() > m_window->height() - EdgeWidth) edges |= Qt::BottomEdge;
    return edges;
}

void Header::updateFrame()
{
    if (!m_window) return;
    const bool square = m_window->isMaximized() || m_window->isFullScreen();
    if (square) m_window->clearMask();
    else {
        QPainterPath shape;
        shape.addRoundedRect(QRectF(m_window->rect()), Radius, Radius);
        m_window->setMask(QRegion(shape.toFillPolygon().toPolygon()));
    }
    if (m_maximize) {
        m_maximize->setIcon(KDE::icon(m_window->isMaximized() ? QStringLiteral("window-restore") : QStringLiteral("window-maximize")));
        const QString label = m_window->isMaximized() ? i18nd("flausen", "Restore") : i18nd("flausen", "Maximize");
        m_maximize->setToolTip(label);
        m_maximize->setAccessibleName(label);
    }
    if (m_action) m_action->setVisible(!m_window->isFullScreen());
    if (m_shadow) {
        if (square) m_shadow->destroy();
        else if (!m_shadow->isCreated()) m_shadow->create();
    }
    m_window->update();
}

void Header::createShadow()
{
    if (!m_window || !m_window->windowHandle() || m_shadow) return;
    // KDE's public client shadow API supplies a compositor-owned shadow.
    // Tiles are generated once from a blurred rounded rectangle.
    constexpr int pad = 24, corner = pad + Radius, extent = corner * 2 + 1;
    QImage image(extent, extent, QImage::Format_ARGB32_Premultiplied);
    image.fill(Qt::transparent);
    for (int y = 0; y < extent; ++y) {
        for (int x = 0; x < extent; ++x) {
            const double dx = std::abs(x - extent / 2.0) - .5;
            const double dy = std::abs(y - extent / 2.0 - 2) - .5;
            const double distance = qMax(0.0, std::hypot(qMax(0.0, dx), qMax(0.0, dy)) - Radius);
            image.setPixelColor(x, y, QColor(0, 0, 0, qRound(70 * std::exp(-distance * distance / 110.0))));
        }
    }
    m_shadow = new KWindowShadow(this);
    m_shadow->setTopLeftTile(tile(image, {0, 0, corner, corner}));
    m_shadow->setTopTile(tile(image, {corner, 0, 1, corner}));
    m_shadow->setTopRightTile(tile(image, {corner + 1, 0, corner, corner}));
    m_shadow->setRightTile(tile(image, {corner + 1, corner, corner, 1}));
    m_shadow->setBottomRightTile(tile(image, {corner + 1, corner + 1, corner, corner}));
    m_shadow->setBottomTile(tile(image, {corner, corner + 1, 1, corner}));
    m_shadow->setBottomLeftTile(tile(image, {0, corner + 1, corner, corner}));
    m_shadow->setLeftTile(tile(image, {0, corner, corner, 1}));
    m_shadow->setPadding(QMargins(pad, pad, pad, pad));
    m_shadow->setWindow(m_window->windowHandle());
    if (!m_window->isMaximized() && !m_window->isFullScreen()) m_shadow->create();
}

bool Header::eventFilter(QObject *watched, QEvent *event)
{
    if (!m_window || !m_toolbar) return false;
    if (watched == m_window->windowHandle() && event->type() == QEvent::Expose
        && m_window->windowHandle()->isExposed()
        && m_window->property("ralleurFileDialogInitialSize").isValid()) {
        const auto size = m_window->property("ralleurFileDialogInitialSize").toSize();
        m_window->setProperty("ralleurFileDialogInitialSize", QVariant());
        QPointer<QWidget> guard(m_window);
        QTimer::singleShot(0, this, [guard, size] { if (guard) guard->resize(size); });
    }
    auto source = qobject_cast<QWidget *>(watched);
    const bool ours = source && source->window() == m_window;
    const bool applicationTheme = watched == qApp && (event->type() == QEvent::ApplicationPaletteChange || event->type() == QEvent::ThemeChange);
    const bool widgetTheme = ours && (event->type() == QEvent::ChildAdded || event->type() == QEvent::ApplicationPaletteChange
        || event->type() == QEvent::PaletteChange || event->type() == QEvent::StyleChange || event->type() == QEvent::ThemeChange);
    if ((applicationTheme || widgetTheme) && !m_contentsPending) {
        m_contentsPending = true;
        QTimer::singleShot(0, this, [this] { configureContents(); m_contentsPending = false; });
    }
    if (!ours) return false;
    if (watched == m_toolbar && (event->type() == QEvent::ActionRemoved || event->type() == QEvent::ActionAdded)) {
        if (!m_adjusting) QTimer::singleShot(0, this, &Header::ensureControls);
    }
    if (watched == m_window) {
        if (event->type() == QEvent::Resize || event->type() == QEvent::WindowStateChange
            || event->type() == QEvent::StyleChange) updateFrame();
        if (event->type() == QEvent::Paint) {
            QPainter painter(m_window);
            painter.setRenderHint(QPainter::Antialiasing);
            const int radius = (m_window->isMaximized() || m_window->isFullScreen()) ? 0 : Radius;
            painter.setBrush(m_window->palette().window());
            auto edge = m_window->palette().mid().color();
            edge.setAlpha(90);
            painter.setPen(edge);
            painter.drawRoundedRect(QRectF(m_window->rect()).adjusted(.5, .5, -.5, -.5), radius, radius);
        }
    }
    if (event->type() == QEvent::MouseButtonPress || event->type() == QEvent::MouseButtonDblClick) {
        auto mouse = static_cast<QMouseEvent *>(event);
        if (mouse->button() != Qt::LeftButton || !m_window->windowHandle()) return false;
        const QPointF inWindow = source->mapTo(m_window, mouse->position().toPoint());
        const auto edges = resizeEdges(inWindow);
        if (edges && event->type() == QEvent::MouseButtonPress)
            return m_window->windowHandle()->startSystemResize(edges);
        bool inToolbar = false, interactive = false;
        for (auto ancestor = source; ancestor && ancestor != m_window; ancestor = ancestor->parentWidget()) {
            if (qobject_cast<QAbstractButton *>(ancestor) || qobject_cast<QLineEdit *>(ancestor)
                || qobject_cast<QComboBox *>(ancestor)) interactive = true;
            if (ancestor == m_toolbar) { inToolbar = true; break; }
        }
        // Breadcrumb buttons, address editors and tools retain their own
        // interaction; unused header space performs a native Wayland move.
        if (inToolbar && !interactive) {
            if (event->type() == QEvent::MouseButtonDblClick) { maximizeRestore(); return true; }
            return m_window->windowHandle()->startSystemMove();
        }
    }
    if (event->type() == QEvent::MouseMove) {
        const auto edges = resizeEdges(source->mapTo(m_window, static_cast<QMouseEvent *>(event)->position().toPoint()));
        if (edges == (Qt::TopEdge | Qt::LeftEdge) || edges == (Qt::BottomEdge | Qt::RightEdge))
            m_window->setCursor(Qt::SizeFDiagCursor);
        else if (edges == (Qt::TopEdge | Qt::RightEdge) || edges == (Qt::BottomEdge | Qt::LeftEdge))
            m_window->setCursor(Qt::SizeBDiagCursor);
        else if (edges.testFlag(Qt::LeftEdge) || edges.testFlag(Qt::RightEdge)) m_window->setCursor(Qt::SizeHorCursor);
        else if (edges.testFlag(Qt::TopEdge) || edges.testFlag(Qt::BottomEdge)) m_window->setCursor(Qt::SizeVerCursor);
        else m_window->unsetCursor();
    }
    return false;
}

Integration::Integration(QObject *parent) : QObject(parent)
{
    // The generic factory runs before Dolphin constructs its windows. Prime
    // only its main windows as soon as their first children are constructed,
    // before QWidget creates the native surface during show().
    QCoreApplication::instance()->installEventFilter(this);
}
bool Integration::eligible(QMainWindow *window)
{
    return window && window->inherits("DolphinMainWindow")
        && window->windowType() == Qt::Window
        && window->findChild<QToolBar *>(QStringLiteral("mainToolBar"));
}
Header *Integration::attachFileDialog(QWidget *window)
{
    // winId() can process queued polish events inside FileDialog's constructor.
    // Wait for open()/show(), after its layout and restored geometry exist.
    if (!qobject_cast<QDialog *>(window) || !window->isWindow() || !window->isVisible()) return nullptr;
    QWidget *files = nullptr;
    for (auto child : window->findChildren<QWidget *>())
        if (child->inherits("KFileWidget")) { files = child; break; }
    if (!files) return nullptr;
    auto toolbar = files->findChild<QToolBar *>();
    if (!toolbar) return nullptr;
    if (auto existing = window->findChild<Header *>(QStringLiteral("ralleurHeader"), Qt::FindDirectChildrenOnly)) return existing;
    if (window->objectName().isEmpty())
        window->setObjectName(QStringLiteral("FilesDialog_%1").arg(quintptr(window), 0, 16));
    auto header = new Header(window, toolbar);
    // Start as a usable dialog rather than inheriting a screen-sized chooser.
    // Subsequent manual maximize/resize operations remain native.
    const auto available = window->screen()->availableGeometry().size();
    const QSize initialSize(qMin(1040, available.width() - 64), qMin(700, available.height() - 64));
    window->setProperty("ralleurFileDialogInitialSize", initialSize);
    window->resize(initialSize);
    if (window->windowHandle() && window->windowHandle()->isExposed()) {
        window->setProperty("ralleurFileDialogInitialSize", QVariant());
        QPointer<QWidget> guard(window);
        QTimer::singleShot(0, header, [guard, initialSize] { if (guard) guard->resize(initialSize); });
    }
    return header;
}
Header *Integration::attach(QMainWindow *window)
{
    if (!eligible(window)) return nullptr;
    if (!window->property("ralleurFilesName").toBool()) {
        window->setProperty("ralleurFilesName", true);
        const auto rename = [window] {
            QString title = window->windowTitle();
            if (title == QStringLiteral("Dolphin")
                || title.endsWith(QStringLiteral(" — Dolphin"))
                || title.endsWith(QStringLiteral(" – Dolphin"))
                || title.endsWith(QStringLiteral(" - Dolphin"))) {
                title.chop(QStringLiteral("Dolphin").size());
                window->setWindowTitle(title + QStringLiteral("Files"));
            }
        };
        QObject::connect(window, &QWidget::windowTitleChanged, window, rename);
        rename();
    }
    auto existing = window->findChild<Header *>(QStringLiteral("ralleurHeader"), Qt::FindDirectChildrenOnly);
    if (existing) { existing->ensureControls(); return existing; }
    return new Header(window, window->findChild<QToolBar *>(QStringLiteral("mainToolBar")));
}

void Integration::start()
{
    if (!qobject_cast<QApplication *>(QCoreApplication::instance())) return;
    auto about = KAboutData::applicationData();
    about.setDisplayName(QStringLiteral("Files"));
    KAboutData::setApplicationData(about);
    QApplication::setApplicationDisplayName(QStringLiteral("Files"));
    // Use KDE's platform icon engine with dolphinrc's per-app overlay. Setting
    // a nonempty QIcon theme explicitly bypasses KIconEngine, freezing symbolic
    // SVG colors (white toolbar icons would stay white in a light palette).
    QSettings config(QStandardPaths::writableLocation(QStandardPaths::GenericConfigLocation)
                     + QStringLiteral("/dolphinrc"), QSettings::IniFormat);
    const QString folderTheme = QStringLiteral("ralleur-rounded-folders");
    if (config.value(QStringLiteral("Icons/Theme")).toString() == folderTheme
        && !QStandardPaths::locate(QStandardPaths::GenericDataLocation,
             QStringLiteral("icons/") + folderTheme + QStringLiteral("/index.theme")).isEmpty())
    {
        QIcon::setThemeName(QString());
        KIconTheme::reconfigure();
        KIconLoader::global()->reconfigure(QCoreApplication::applicationName());
        KIconLoader::global()->resetPalette();
    }
    // Keep the injection local to this Dolphin process; children use their own
    // normal Qt setup, while new Dolphin launches go through the wrapper.
    auto plugins = qEnvironmentVariable("QT_QPA_GENERIC_PLUGINS").split(',', Qt::SkipEmptyParts);
    plugins.removeAll(QStringLiteral("ralleurdolphin"));
    if (plugins.isEmpty()) qunsetenv("QT_QPA_GENERIC_PLUGINS");
    else qputenv("QT_QPA_GENERIC_PLUGINS", plugins.join(',').toLocal8Bit());
    auto paths = qEnvironmentVariable("QT_PLUGIN_PATH").split(':', Qt::SkipEmptyParts);
    paths.removeAll(qEnvironmentVariable("RALLEUR_DOLPHIN_PLUGIN_DIR"));
    if (paths.isEmpty()) qunsetenv("QT_PLUGIN_PATH");
    else qputenv("QT_PLUGIN_PATH", paths.join(':').toLocal8Bit());
    qunsetenv("RALLEUR_DOLPHIN_PLUGIN_DIR");
    if (QFileInfo(QCoreApplication::applicationFilePath()).fileName() == QStringLiteral("dolphin"))
        new ContextMenus(this);
    qApp->installEventFilter(this);
    for (auto widget : QApplication::topLevelWidgets()) {
        attach(qobject_cast<QMainWindow *>(widget));
        attachFileDialog(widget);
    }
}

bool Integration::eventFilter(QObject *watched, QEvent *event)
{
    if (event->type() == QEvent::ChildAdded || event->type() == QEvent::PolishRequest
        || event->type() == QEvent::Polish) {
        // FileDialog restores its size with winId() during construction. Set
        // the surface flags before that, preserving the portal activation.
        if (auto dialog = qobject_cast<QDialog *>(watched);
            dialog && dialog->inherits("FileDialog") && !dialog->isVisible()) {
            dialog->setAttribute(Qt::WA_TranslucentBackground);
            dialog->setAttribute(Qt::WA_OpaquePaintEvent, false);
            dialog->setWindowFlag(Qt::FramelessWindowHint, true);
        }
        if (auto window = qobject_cast<QMainWindow *>(watched);
            window && window->inherits("DolphinMainWindow") && window->windowType() == Qt::Window) {
            window->setAttribute(Qt::WA_TranslucentBackground);
            window->setAttribute(Qt::WA_OpaquePaintEvent, false);
        }
    }
    if (event->type() == QEvent::Show || event->type() == QEvent::Polish) {
        if (auto dialog = qobject_cast<QDialog *>(watched); dialog && dialog->isWindow()) {
            QPointer<QDialog> guard(dialog);
            QTimer::singleShot(0, this, [guard] { if (guard) attachFileDialog(guard); });
        }
        if (auto window = qobject_cast<QMainWindow *>(watched); eligible(window)) {
            QPointer<QMainWindow> guard(window);
            QTimer::singleShot(0, this, [guard] { if (guard) attach(guard); });
        }
    }
    return false;
}
}
