from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QTextEdit, QPushButton, QLabel, QListWidget,
    QListWidgetItem, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from models import Meme, Tag


class AddMemeDialog(QDialog):
    def __init__(self, image_path, existing_tags, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.setWindowTitle("Добавление мема")
        self.setMinimumSize(600, 600)

        layout = QVBoxLayout(self)

        self.preview = QLabel()
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            self.preview.setPixmap(
                pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        layout.addWidget(self.preview)

        form = QFormLayout()
        self.title_edit = QLineEdit()
        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(80)
        form.addRow("Название:", self.title_edit)
        form.addRow("Описание шаблона:", self.desc_edit)
        layout.addLayout(form)

        layout.addWidget(QLabel("Теги (можно выбрать несколько, Ctrl+клик):"))
        self.tag_list = QListWidget()
        self.tag_list.setSelectionMode(QListWidget.MultiSelection)
        for tag in existing_tags:
            item = QListWidgetItem(tag.name)
            item.setData(Qt.UserRole, tag)
            self.tag_list.addItem(item)
        layout.addWidget(self.tag_list)

        new_tag_layout = QHBoxLayout()
        self.new_tag_edit = QLineEdit()
        self.new_tag_edit.setPlaceholderText("Новый тег")
        add_tag_btn = QPushButton("Добавить тег")
        add_tag_btn.clicked.connect(self._add_new_tag)
        new_tag_layout.addWidget(self.new_tag_edit)
        new_tag_layout.addWidget(add_tag_btn)
        layout.addLayout(new_tag_layout)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        cancel_btn = QPushButton("Отмена")
        save_btn.clicked.connect(self._on_save)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def _add_new_tag(self):
        name = self.new_tag_edit.text().strip()
        if not name:
            return
        tag = Tag(id=None, name=name)
        item = QListWidgetItem(name)
        item.setData(Qt.UserRole, tag)
        item.setSelected(True)
        self.tag_list.addItem(item)
        self.new_tag_edit.clear()

    def _on_save(self):
        title = self.title_edit.text().strip()
        if not title:
            QMessageBox.warning(self, "Ошибка", "Введите название мема")
            return
        self.accept()

    def get_meme(self):
        title = self.title_edit.text().strip()
        description = self.desc_edit.toPlainText().strip()
        tags = []
        for item in self.tag_list.selectedItems():
            tag = item.data(Qt.UserRole)
            if tag is None:
                tag = Tag(id=None, name=item.text())
            tags.append(tag)
        return Meme(
            id=None,
            title=title,
            description=description,
            image_path=self.image_path,
            tags=tags
        )
