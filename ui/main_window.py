import os
import shutil
import uuid

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QListWidgetItem,
    QLabel, QMessageBox, QFileDialog, QSystemTrayIcon,
    QMenu, QAction, QSplitter
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon

from database import MemeRepository
from ui.add_meme_dialog import AddMemeDialog
from ui.search_widget import SearchWidget
from ui.tag_cloud import TagCloud


IMAGES_DIR = "images"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.repo = MemeRepository()
        self.setWindowTitle("Meme Manager")
        self.setMinimumSize(1000, 700)

        os.makedirs(IMAGES_DIR, exist_ok=True)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        top_panel = QHBoxLayout()
        add_btn = QPushButton("Добавить из буфера")
        add_btn.clicked.connect(self.add_from_clipboard)
        add_file_btn = QPushButton("Добавить из файла")
        add_file_btn.clicked.connect(self.add_from_file)
        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self.delete_selected)
        top_panel.addWidget(add_btn)
        top_panel.addWidget(add_file_btn)
        top_panel.addWidget(delete_btn)
        top_panel.addStretch()
        main_layout.addLayout(top_panel)

        self.search_widget = SearchWidget()
        self.search_widget.search_requested.connect(self.do_search)
        main_layout.addWidget(self.search_widget)

        splitter = QSplitter(Qt.Horizontal)

        self.meme_list = QListWidget()
        self.meme_list.setIconSize(QSize(120, 120))
        self.meme_list.itemClicked.connect(self.on_meme_selected)
        splitter.addWidget(self.meme_list)

        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        self.details_image = QLabel()
        self.details_image.setAlignment(Qt.AlignCenter)
        self.details_title = QLabel()
        self.details_title.setWordWrap(True)
        self.details_desc = QLabel()
        self.details_desc.setWordWrap(True)
        self.details_tags = QLabel()
        self.details_tags.setWordWrap(True)
        self.details_date = QLabel()

        details_layout.addWidget(self.details_image)
        details_layout.addWidget(self.details_title)
        details_layout.addWidget(self.details_desc)
        details_layout.addWidget(self.details_tags)
        details_layout.addWidget(self.details_date)
        details_layout.addStretch()

        splitter.addWidget(details_widget)
        splitter.setSizes([500, 400])

        main_layout.addWidget(splitter)

        main_layout.addWidget(QLabel("Облако тегов:"))
        self.tag_cloud = TagCloud()
        self.tag_cloud.tag_clicked.connect(self.on_tag_clicked)
        main_layout.addWidget(self.tag_cloud)

        self.status = self.statusBar()

        self.setup_tray()
        self.refresh_memes()
        self.refresh_tag_cloud()

    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(
            self.style().SP_ComputerIcon))
        menu = QMenu()
        show_action = QAction("Показать", self)
        show_action.triggered.connect(self.showNormal)
        quit_action = QAction("Выход", self)
        quit_action.triggered.connect(self._quit)
        menu.addAction(show_action)
        menu.addAction(quit_action)
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self._tray_activated)
        self.tray_icon.show()

    def _tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.showNormal()

    def _quit(self):
        self.tray_icon.hide()
        from PyQt5.QtWidgets import QApplication
        QApplication.quit()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Meme Manager",
            "Приложение свёрнуто в трей",
            QSystemTrayIcon.Information,
            2000
        )

    def add_from_clipboard(self):
        try:
            from PIL import ImageGrab
            image = ImageGrab.grabclipboard()
            if image is None:
                QMessageBox.warning(self, "Ошибка",
                                    "В буфере обмена нет изображения")
                return
            filename = uuid.uuid4().hex + ".png"
            filepath = os.path.join(IMAGES_DIR, filename)
            image.save(filepath, "PNG")
            self._open_add_dialog(filepath)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка",
                                 "Не удалось получить изображение: " + str(e))

    def add_from_file(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение", "",
            "Изображения (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if not filepath:
            return
        ext = os.path.splitext(filepath)[1]
        filename = uuid.uuid4().hex + ext
        new_path = os.path.join(IMAGES_DIR, filename)
        shutil.copy(filepath, new_path)
        self._open_add_dialog(new_path)

    def _open_add_dialog(self, image_path):
        existing_tags = self.repo.get_all_tags()
        dialog = AddMemeDialog(image_path, existing_tags, self)
        if dialog.exec_():
            meme = dialog.get_meme()
            self.repo.add_meme(meme)
            self.refresh_memes()
            self.refresh_tag_cloud()

    def refresh_memes(self, memes=None):
        if memes is None:
            memes = self.repo.get_all_memes()
        self.meme_list.clear()
        for meme in memes:
            item = QListWidgetItem(meme.title)
            item.setData(Qt.UserRole, meme.id)
            pixmap = QPixmap(meme.image_path)
            if not pixmap.isNull():
                item.setIcon(QIcon(pixmap.scaled(
                    120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)))
            self.meme_list.addItem(item)
        self.status.showMessage("Найдено мемов: " + str(len(memes)))

    def refresh_tag_cloud(self):
        counts = self.repo.get_tag_usage_counts()
        self.tag_cloud.update_tags(counts)

    def on_meme_selected(self, item):
        meme_id = item.data(Qt.UserRole)
        memes = self.repo.get_all_memes()
        meme = None
        for m in memes:
            if m.id == meme_id:
                meme = m
                break
        if not meme:
            return
        pixmap = QPixmap(meme.image_path)
        if not pixmap.isNull():
            self.details_image.setPixmap(pixmap.scaled(
                350, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.details_title.setText("<b>" + meme.title + "</b>")
        self.details_desc.setText("Описание: " + meme.description)
        tags_str = ", ".join(t.name for t in meme.tags)
        self.details_tags.setText("Теги: " + tags_str)
        self.details_date.setText("Добавлено: " + str(meme.date_added))

    def do_search(self, text, date_from, date_to):
        memes = self.repo.search_memes(
            text=text,
            date_from=date_from if date_from else None,
            date_to=date_to if date_to else None
        )
        self.refresh_memes(memes)

    def on_tag_clicked(self, tag_name):
        all_memes = self.repo.get_all_memes()
        filtered = [m for m in all_memes
                    if any(t.name == tag_name for t in m.tags)]
        self.refresh_memes(filtered)
        self.status.showMessage(
            "Фильтр по тегу: " + tag_name + " (" + str(len(filtered)) + ")")

    def delete_selected(self):
        item = self.meme_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Ошибка", "Выберите мем")
            return
        reply = QMessageBox.question(
            self, "Удаление", "Удалить выбранный мем?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            meme_id = item.data(Qt.UserRole)
            self.repo.delete_meme(meme_id)
            self.refresh_memes()
            self.refresh_tag_cloud()
