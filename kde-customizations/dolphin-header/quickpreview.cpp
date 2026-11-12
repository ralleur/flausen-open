#include <KLocalizedString>
// SPDX-License-Identifier: MIT
#include "quickpreview.h"
#include <QApplication>
#include <QAction>
#include <QAudioOutput>
#include <QAbstractButton>
#include <QAbstractSlider>
#include <QAbstractScrollArea>
#include <QDialog>
#include <QFile>
#include <QFileInfo>
#include <QImageReader>
#include <QKeyEvent>
#include <QLabel>
#include <QMainWindow>
#include <QMediaPlayer>
#include <QMetaMethod>
#include <QMimeDatabase>
#include <QMouseEvent>
#include <QPainter>
#include <QPainterPath>
#include <QResizeEvent>
#include <QPdfDocument>
#include <QPdfView>
#include <QPlainTextEdit>
#include <QPushButton>
#include <QScreen>
#include <QSlider>
#include <QVBoxLayout>
#include <QVideoWidget>
#include <QWindow>
#include <KXmlGuiWindow>
#include <KActionCollection>

namespace Ralleur {
namespace {
constexpr int PreviewRadius=16;

class PreviewContent : public QWidget {
public:
    using QWidget::QWidget;
protected:
    void resizeEvent(QResizeEvent *event) override {
        QWidget::resizeEvent(event);
        QPainterPath shape;
        shape.addRoundedRect(QRectF(rect()),PreviewRadius-2,PreviewRadius-2);
        setMask(QRegion(shape.toFillPolygon().toPolygon()));
    }
};

class PreviewDialog : public QDialog {
public:
    explicit PreviewDialog(QWidget *parent) : QDialog(parent,Qt::Tool | Qt::FramelessWindowHint) {
        // Set alpha before the native surface exists, keeping the corners
        // transparent rather than displaying a rectangular black backing.
        setAttribute(Qt::WA_TranslucentBackground);
        setAutoFillBackground(false);
        // This custom surface owns its frame. Opt out of the generic dialog
        // skin while retaining native palettes for its document/media widgets.
        setStyleSheet(QStringLiteral("QDialog#ralleurQuickPreviewDialog { background: transparent; }"));
        auto layout=new QVBoxLayout(this);
        layout->setContentsMargins(2,2,2,2);
        layout->setSpacing(0);
        m_content=new PreviewContent(this);
        layout->addWidget(m_content);
    }
    QWidget *content() const { return m_content; }
protected:
    void paintEvent(QPaintEvent *) override {
        QPainter painter(this);
        painter.setRenderHint(QPainter::Antialiasing);
        const auto frame=QRectF(rect()).adjusted(.5,.5,-.5,-.5);
        const auto theme=qApp->palette();
        auto background=theme.color(QPalette::Window);
        background.setAlpha(255);
        painter.setBrush(background);
        QLinearGradient edge(frame.topLeft(),frame.bottomRight());
        auto light=theme.color(QPalette::WindowText);
        light.setAlpha(92); edge.setColorAt(0,light);
        light.setAlpha(28); edge.setColorAt(.45,light);
        light.setAlpha(55); edge.setColorAt(1,light);
        painter.setPen(QPen(QBrush(edge),1));
        painter.drawRoundedRect(frame,PreviewRadius,PreviewRadius);
    }
private:
    QWidget *m_content;
};

class ImageView : public QWidget {
public:
    explicit ImageView(QImage image, QWidget *parent) : QWidget(parent), m_image(std::move(image)) {
        setMinimumSize(100,100);
        setCursor(Qt::OpenHandCursor);
    }
protected:
    void paintEvent(QPaintEvent *) override {
        QPainter painter(this);
        auto size = m_image.size();
        size.scale(contentsRect().size(), Qt::KeepAspectRatio);
        painter.setRenderHint(QPainter::SmoothPixmapTransform);
        painter.drawImage(QRect(QPoint((width()-size.width())/2,(height()-size.height())/2),size),m_image);
    }
private:
    QImage m_image;
};

QWidget *message(const QString &text, QWidget *parent) {
    auto label = new QLabel(text,parent);
    label->setAlignment(Qt::AlignCenter);
    label->setWordWrap(true);
    label->setTextFormat(Qt::PlainText);
    return label;
}

QWidget *preview(const KFileItem &item, QWidget *parent) {
    // No launch jobs or handlers: a preview never executes the selected file.
    if (!item.url().isLocalFile()) return message(i18nd("flausen", "Quick preview is unavailable for this remote file."),parent);
    const auto path=item.url().toLocalFile();
    const QFileInfo info(path);
    if (!info.exists()) return message(i18nd("flausen", "The file is no longer available."),parent);
    if (info.isDir()) return message(i18nd("flausen", "Folder\n%1").arg(info.fileName()),parent);
    if (!info.isFile()) return message(i18nd("flausen", "Quick preview is unavailable for this file type."),parent);
    const auto mime=QMimeDatabase().mimeTypeForFile(path);
    if (mime.name()==QStringLiteral("application/pdf")) {
        auto document=new QPdfDocument(parent);
        if (document->load(path)!=QPdfDocument::Error::None)
            return message(i18nd("flausen", "Cannot display this PDF (damaged or password protected)."),parent);
        auto view=new QPdfView(parent);
        view->setObjectName(QStringLiteral("ralleurPdfPreview"));
        view->setDocument(document);
        view->setPageMode(QPdfView::PageMode::MultiPage);
        view->setZoomMode(QPdfView::ZoomMode::FitToWidth);
        return view;
    }
    if (mime.name().startsWith("image/")) {
        QImageReader reader(path);
        reader.setAutoTransform(true);
        const auto size=reader.size();
        if (size.isValid() && (size.width()>2560 || size.height()>1600)) reader.setScaledSize(size.scaled(2560,1600,Qt::KeepAspectRatio));
        auto image=reader.read();
        if (image.isNull()) return message(i18nd("flausen", "Cannot display this image."),parent);
        auto view=new ImageView(std::move(image),parent);
        view->setObjectName(QStringLiteral("ralleurImagePreview"));
        return view;
    }
    if (mime.name().startsWith("video/") || mime.name().startsWith("audio/")) {
        auto pane=new QWidget(parent);
        pane->setObjectName(QStringLiteral("ralleurMediaPreview"));
        auto layout=new QVBoxLayout(pane);
        auto player=new QMediaPlayer(pane);
        auto audio=new QAudioOutput(player);
        player->setAudioOutput(audio);
        audio->setVolume(.7f);
        auto video=new QVideoWidget(pane);
        if (mime.name().startsWith("video/")) { layout->addWidget(video,1); player->setVideoOutput(video); }
        else { video->hide(); layout->addWidget(message(i18nd("flausen", "Audio\n%1").arg(info.fileName()),pane),1); }
        auto error=new QLabel(pane);
        error->setTextFormat(Qt::PlainText);
        layout->addWidget(error);
        auto controls=new QHBoxLayout;
        auto play=new QPushButton(i18nd("flausen", "Pause"),pane);
        auto seek=new QSlider(Qt::Horizontal,pane);
        seek->setRange(0,1000);
        controls->addWidget(play); controls->addWidget(seek,1); layout->addLayout(controls);
        QObject::connect(play,&QPushButton::clicked,player,[player] {
            if (player->playbackState()==QMediaPlayer::PlayingState) player->pause(); else player->play();
        });
        QObject::connect(player,&QMediaPlayer::playbackStateChanged,play,[play](QMediaPlayer::PlaybackState state) {
            play->setText(state==QMediaPlayer::PlayingState ? i18nd("flausen", "Pause") : i18nd("flausen", "Play"));
        });
        QObject::connect(seek,&QSlider::sliderMoved,player,[player](int position) { player->setPosition(player->duration()*position/1000); });
        QObject::connect(player,&QMediaPlayer::positionChanged,seek,[player,seek](qint64 position) {
            if (!seek->isSliderDown() && player->duration()>0) seek->setValue(position*1000/player->duration());
        });
        QObject::connect(player,&QMediaPlayer::errorOccurred,error,[error,player] { error->setText(player->errorString()); });
        // Closing the dialog stops sound immediately, before deferred deletion.
        QObject::connect(qobject_cast<QDialog *>(parent->window()),&QDialog::finished,player,&QMediaPlayer::stop);
        player->setSource(item.url());
        player->play();
        return pane;
    }
    if (mime.inherits("text/plain") || mime.inherits("application/json") || mime.inherits("application/xml")) {
        QFile file(path);
        if (!file.open(QIODevice::ReadOnly)) return message(i18nd("flausen", "Cannot read this file."),parent);
        constexpr qint64 limit=1024*1024;
        const auto bytes=file.read(limit);
        auto text=new QPlainTextEdit(parent);
        text->setObjectName(QStringLiteral("ralleurTextPreview"));
        text->setReadOnly(true);
        text->setPlainText(QString::fromUtf8(bytes));
        if (info.size()>limit) text->appendPlainText(i18nd("flausen", "\n… Preview limited to 1 MiB."));
        return text;
    }
    return message(i18nd("flausen", "%1\n%2\nQuick preview is unavailable for this file type.").arg(info.fileName(),mime.comment()),parent);
}
}

QuickPreview::QuickPreview(QMainWindow *window) : QObject(window),m_window(window) {
    setObjectName(QStringLiteral("ralleurQuickPreview"));
    qApp->installEventFilter(this);
    bindViews();
}

void QuickPreview::bindViews() {
    if (!m_window) return;
    auto actions=m_window->findChildren<QAction *>(QStringLiteral("toggle_selection_mode"));
    if (auto native=qobject_cast<KXmlGuiWindow *>(m_window.data())) {
        if (auto action=native->actionCollection()->action(QStringLiteral("toggle_selection_mode"))) actions.append(action);
    }
    for (auto action:actions) {
        auto shortcuts=action->shortcuts();
        if (shortcuts.removeAll(QKeySequence(Qt::Key_Space))) action->setShortcuts(shortcuts);
    }
    for (auto view:m_window->findChildren<QWidget *>()) {
        if (!view->inherits("DolphinView") || m_selection.contains(view)) continue;
        // Bind each tab/split separately; never obtain selection via Clipboard.
        if (view->metaObject()->indexOfSignal("selectionChanged(KFileItemList)")<0) continue;
        m_selection.insert(view,{});
        connect(view,SIGNAL(selectionChanged(KFileItemList)),this,SLOT(selectionChanged(KFileItemList)));
        connect(view,&QObject::destroyed,this,[this,view] {
            m_selection.remove(view);
            if (!m_view && m_dialog) m_dialog->close();
        });
    }
}
void QuickPreview::selectionChanged(const KFileItemList &items) {
    auto view=qobject_cast<QWidget *>(sender());
    m_selection[view]=items;
    if (!m_dialog || !m_dialog->isVisible() || !view || !view->isVisible()) return;
    const auto focus=qApp->focusWidget();
    const bool focused=focus && (focus==view || view->isAncestorOf(focus));
    // Background tabs/splits must not replace the file being inspected. The
    // originating view can still notify while the preview itself has focus.
    if (!focused && !(view==m_view && focus && focus->window()==m_dialog)) return;
    m_view=view;
    updatePreview(items);
}

void QuickPreview::updatePreview(const KFileItemList &items) {
    const auto url=items.isEmpty() ? QUrl() : items.first().url();
    if (url==m_previewUrl && m_dialog->findChild<QWidget *>(QStringLiteral("ralleurPreviewPage"))) return;
    m_previewUrl=url;
    auto dialog=static_cast<PreviewDialog *>(m_dialog.data());
    auto layout=dialog->content()->layout();
    // Each page owns its documents and players, so switching files releases
    // the previous PDF and stops media immediately, without moving the window.
    while (auto item=layout->takeAt(0)) {
        delete item->widget();
        delete item;
    }
    auto page=new QWidget(dialog->content());
    page->setObjectName(QStringLiteral("ralleurPreviewPage"));
    auto pageLayout=new QVBoxLayout(page);
    pageLayout->setContentsMargins(0,0,0,0);
    pageLayout->setSpacing(0);
    pageLayout->addWidget(items.isEmpty() ? message(i18nd("flausen", "No file selected."),page) : preview(items.first(),page));
    layout->addWidget(page);
    dialog->setWindowTitle(items.isEmpty() ? i18nd("flausen", "Preview") : items.first().name()+i18nd("flausen", " — Preview"));
}

void QuickPreview::toggle(QWidget *view) {
    if (m_dialog && m_dialog->isVisible()) { m_dialog->close(); return; }
    // Dolphin batches selection notifications for 300 ms. Flush its existing
    // QObject slot before reading our signal snapshot (no private C++ ABI).
    const auto index=view->metaObject()->indexOfSlot("emitSelectionChangedSignal()");
    if (index>=0) view->metaObject()->method(index).invoke(view,Qt::DirectConnection);
    const auto items=m_selection.value(view);
    if (items.isEmpty()) return;
    auto dialog=new PreviewDialog(m_window);
    m_dialog=dialog;
    m_view=view;
    m_previewUrl=QUrl();
    dialog->setAttribute(Qt::WA_DeleteOnClose);
    dialog->setObjectName(QStringLiteral("ralleurQuickPreviewDialog"));
    auto layout=new QVBoxLayout(dialog->content());
    layout->setContentsMargins(0,0,0,0);
    layout->setSpacing(0);
    updatePreview(items);
    connect(dialog,&QDialog::finished,this,[this] { if (m_view) m_view->setFocus(Qt::OtherFocusReason); });
    const auto available=m_window->screen()->availableGeometry();
    const auto size=QSize(860,640).boundedTo(available.size()*0.85);
    dialog->resize(size);
    dialog->move(m_window->geometry().center()-QPoint(size.width()/2,size.height()/2));
    dialog->show();
    dialog->raise();
    dialog->activateWindow();
}

bool QuickPreview::eventFilter(QObject *watched,QEvent *event) {
    auto widget=qobject_cast<QWidget *>(watched);
    if (!widget || !m_window) return false;
    const bool inPreview=m_dialog && widget->window()==m_dialog;
    if (inPreview && event->type()==QEvent::MouseButtonPress) {
        const auto mouse=static_cast<QMouseEvent *>(event);
        if (mouse->button()!=Qt::LeftButton || mouse->modifiers()!=Qt::NoModifier) return false;
        const auto position=widget->mapTo(m_dialog,mouse->position().toPoint());
        const auto inside=m_dialog->rect().adjusted(12,16,-12,-12);
        for (auto current=widget;current && current!=m_dialog;current=current->parentWidget()) {
            // Playback controls, scrollbars and document selection retain
            // their normal interactions. Documents can be moved at the rim.
            if (qobject_cast<QAbstractButton *>(current) || qobject_cast<QAbstractSlider *>(current)) return false;
            if (qobject_cast<QAbstractScrollArea *>(current) && inside.contains(position)) return false;
        }
        // The compositor owns the drag, including Wayland's input serial,
        // multi-monitor movement and snapping; no manual geometry loop.
        if (auto native=m_dialog->windowHandle()) return native->startSystemMove();
    }
    if (event->type()!=QEvent::ShortcutOverride && event->type()!=QEvent::KeyPress && event->type()!=QEvent::KeyRelease) return false;
    const auto key=static_cast<QKeyEvent *>(event);
    const bool space=key->key()==Qt::Key_Space && key->modifiers()==Qt::NoModifier;
    if (inPreview && (space || key->key()==Qt::Key_Escape)) {
        event->accept();
        if (event->type()==QEvent::KeyPress && !key->isAutoRepeat()) m_dialog->close();
        return true;
    }
    const bool escape=key->key()==Qt::Key_Escape && m_dialog && m_dialog->isVisible();
    if ((!space && !escape) || widget->window()!=m_window) return false;
    // Only file views own this gesture; address/filter/search/rename editors
    // and the embedded terminal retain their ordinary keyboard handling.
    for (auto current=widget;current;current=current->parentWidget()) {
        if (current->inherits("QLineEdit") || current->inherits("QTextEdit") || current->inherits("QPlainTextEdit")) return false;
        if (!current->inherits("DolphinView")) continue;
        event->accept();
        if (event->type()==QEvent::KeyPress && !key->isAutoRepeat()) {
            if (escape) m_dialog->close(); else toggle(current);
        }
        return true;
    }
    return false;
}
}
