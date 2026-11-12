// SPDX-License-Identifier: MIT
#include <QGenericPlugin>
#include <QGuiApplication>
#include <QQuickWindow>
#include <QQuickItem>
#include <QTimer>
#include <QPalette>
#include <QFile>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <functional>
class Probe : public QGenericPlugin {
    Q_OBJECT
    Q_PLUGIN_METADATA(IID QGenericPluginFactoryInterface_iid FILE "probe.json")
public:
    QObject *create(const QString &name, const QString &) override {
        if (name != "ralleurstyleprobe") return nullptr;
        auto owner = new QObject;
        QTimer::singleShot(0, owner, [owner] {
            const auto args=QCoreApplication::arguments();
            if (!args.contains("--testing") && !args.contains("--test")) return;
            const auto size = qEnvironmentVariable("RALLEUR_PROBE_SIZE").split('x');
            if (size.size() == 2) for (auto candidate : QGuiApplication::topLevelWindows())
                candidate->resize(size[0].toInt(), size[1].toInt());
            const bool dark=qEnvironmentVariable("RALLEUR_PROBE_MODE")=="dark";
            auto pal=QGuiApplication::palette();
            pal.setColor(QPalette::Window, QColor(dark ? "#1c1f21" : "#f8f6f3"));
            pal.setColor(QPalette::WindowText, QColor(dark ? "#f4f3f1" : "#161616"));
            QGuiApplication::setPalette(pal);
            QTimer::singleShot(800, owner, [owner,args] {
                QQuickWindow *window=nullptr;
                for(auto candidate:QGuiApplication::topLevelWindows()) if(auto quick=qobject_cast<QQuickWindow*>(candidate)) {window=quick;break;}
                if(!window) { QCoreApplication::exit(2); return; }
                if (qEnvironmentVariableIsSet("RALLEUR_PROBE_AVATAR")) {
                    QJsonArray avatars;
                    std::function<void(QQuickItem *)> visit = [&](QQuickItem *object) {
                        for (auto child : object->childItems()) visit(child);
                        if (object->metaObject()->indexOfProperty("avatarPath") < 0) return;
                        const auto path = object->property("avatarPath").toString();
                        bool loaded = false;
                        std::function<void(QQuickItem *)> inspectImage = [&](QQuickItem *child) {
                            if (child->property("source").toUrl().toString() == path
                                && child->property("status").toInt() == 1) loaded = true;
                            for (auto item : child->childItems()) inspectImage(item);
                        };
                        inspectImage(object);
                        avatars.append(QJsonObject{{"userName",object->property("userName").toString()},
                                                  {"source",path},{"loaded",loaded}});
                    };
                    visit(window->contentItem());
                    QFile report(qEnvironmentVariable("RALLEUR_PROBE_AVATAR"));
                    if (report.open(QIODevice::WriteOnly)) report.write(QJsonDocument(avatars).toJson());
                }
                if (args.contains("--testing") && qEnvironmentVariableIsSet("RALLEUR_PROBE_LAYOUT")) {
                    auto content = window->contentItem();
                    auto viewport = content->findChild<QQuickItem*>("ralleurLockActionsViewport");
                    auto footer = content->findChild<QQuickItem*>("ralleurLockFooter");
                    auto actions = content->findChild<QQuickItem*>("ralleurLockActions");
                    auto date = content->findChild<QObject*>("ralleurLockDate");
                    const QRectF bounds(0,0,window->width(),window->height());
                    auto inside = [content,bounds](QQuickItem *item) {
                        return item && bounds.adjusted(-1,-1,1,1).contains(item->mapRectToItem(content, QRectF(0,0,item->width(),item->height())));
                    };
                    bool actionBounds = actions != nullptr;
                    if (actions) for (auto child : actions->childItems()) if(child->isVisible()) actionBounds &= inside(child);
                    QJsonObject report{{"width",window->width()},{"height",window->height()},
                        {"viewportInside",inside(viewport)},{"footerInside",inside(footer)},{"actionsInside",actionBounds},
                        {"date",date ? date->property("text").toString() : QString()}};
                    QFile file(qEnvironmentVariable("RALLEUR_PROBE_LAYOUT"));
                    if(file.open(QIODevice::WriteOnly)) file.write(QJsonDocument(report).toJson());
                }
                const auto capture=qEnvironmentVariable("RALLEUR_PROBE_CAPTURE");
                if(!capture.isEmpty()) window->grabWindow().save(capture);
                // The login manager's test backend is the only target allowed
                // to receive synthetic credentials. No PAM process is involved.
                if(args.contains("--test") && qEnvironmentVariableIsSet("RALLEUR_PROBE_AUTH")) {
                    auto login=window->contentItem()->findChild<QObject*>("ralleurLogin");
                    auto password=window->contentItem()->findChild<QObject*>("ralleurPassword");
                    if(!login || !password) {QCoreApplication::exit(3);return;}
                    password->setProperty("text", "ralleur-test-invalid");
                    const bool invoked=QMetaObject::invokeMethod(login,"startLogin");
                    QTimer::singleShot(1000,owner,[window,login,invoked] {
                        auto root=window->contentItem()->findChild<QObject*>("ralleurLoginRoot");
                        const bool failed=root && !root->property("notificationMessage").toString().isEmpty();
                        const bool retry = login->property("enabled").toBool();
                        QFile report(qEnvironmentVariable("RALLEUR_PROBE_AUTH"));
                        if (!report.open(QIODevice::WriteOnly)) {QCoreApplication::exit(5);return;}
                        report.write(QJsonDocument(QJsonObject{{"invoked",invoked},{"failureDisplayed",failed},{"readyForRetry",retry}}).toJson());
                        QCoreApplication::exit(invoked && failed && retry ? 0 : 4);
                    });
                } else QCoreApplication::exit(0);
            });
        });
        return owner;
    }
};
#include "probe.moc"
