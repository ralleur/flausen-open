#include <QGuiApplication>
#include <QIcon>
#include <QImageReader>
#include <QPainter>
#include <QSettings>
#include <QStandardPaths>
#include <QCryptographicHash>
#include <QDir>
#include <QFileInfo>
#include <QSaveFile>
#include <QTextStream>
#include <QUrl>

// Dock-local rendering: leave the installed theme and original artwork untouched.
int main(int argc, char **argv) {
    QGuiApplication app(argc, argv);
    if (argc != 2) return 1;
    const QString source = QString::fromLocal8Bit(argv[1]);
    QSettings settings(QStandardPaths::locate(QStandardPaths::GenericConfigLocation,
                                            "kdeglobals"), QSettings::IniFormat);
    QStringList themePaths = QIcon::themeSearchPaths();
    QStringList fallbackPaths = QIcon::fallbackSearchPaths();
    for (const auto &base : QStandardPaths::standardLocations(QStandardPaths::GenericDataLocation)) {
        themePaths.append(base + "/icons");
        fallbackPaths.append(base + "/pixmaps");
    }
    themePaths.append(QDir::homePath() + "/.icons");
    themePaths.removeDuplicates();
    QIcon::setThemeSearchPaths(themePaths);
    fallbackPaths.removeDuplicates();
    QIcon::setFallbackSearchPaths(fallbackPaths);
    QIcon::setThemeName(settings.value("Icons/Theme", "breeze").toString());
    constexpr int extent = 512;
    QImage image;
    const QUrl url(source);
    if (url.scheme() == "image" && url.host() == "icon") {
        const QString name = url.path().mid(1);
        image = QIcon::fromTheme(name).pixmap(extent, extent).toImage();
    } else {
        const QString path = url.isLocalFile() ? url.toLocalFile() : source;
        QImageReader reader(path);
        const QSize size = reader.size();
        if (size.isValid()) reader.setScaledSize(size.scaled(extent, extent, Qt::KeepAspectRatio));
        image = reader.read();
    }
    if (image.isNull()) return 2;
    image = image.convertToFormat(QImage::Format_ARGB32);
    QRect bounds;
    // Ignore faint external shadows when finding the actual artwork edge.
    for (int y = 0; y < image.height(); ++y) {
        const auto *line = reinterpret_cast<const QRgb *>(image.constScanLine(y));
        for (int x = 0; x < image.width(); ++x)
            if (qAlpha(line[x]) >= 32) bounds |= QRect(x, y, 1, 1);
    }
    if (bounds.isEmpty()) return 3;
    // Reserve a small fringe for antialiasing; never stretch the brand's shape.
    const double scale = 504.0 / qMax(bounds.width(), bounds.height());
    QImage result(extent, extent, QImage::Format_ARGB32_Premultiplied);
    result.fill(Qt::transparent);
    QPainter painter(&result);
    painter.setRenderHint(QPainter::SmoothPixmapTransform);
    painter.translate(extent / 2.0, extent / 2.0);
    painter.scale(scale, scale);
    painter.translate(-(bounds.x() + bounds.width() / 2.0),
                      -(bounds.y() + bounds.height() / 2.0));
    painter.drawImage(0, 0, image);
    painter.end();
    // Hash pixels as well as the source: replaced app icons and themes refresh safely.
    QCryptographicHash hash(QCryptographicHash::Sha256);
    hash.addData(QByteArrayView(reinterpret_cast<const char *>(result.constBits()), result.sizeInBytes()));
    const QString cache = QStandardPaths::writableLocation(QStandardPaths::GenericCacheLocation)
                        + "/flausen/dock-icons-v1";
    if (!QDir().mkpath(cache)) return 4;
    const QString path = cache + "/" + hash.result().toHex() + ".png";
    if (!QFileInfo::exists(path)) {
        QSaveFile file(path);
        if (!file.open(QIODevice::WriteOnly) || !result.save(&file, "PNG") || !file.commit()) return 5;
    }
    QTextStream(stdout) << QUrl::fromLocalFile(path).toString() << Qt::endl;
}
