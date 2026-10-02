from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QPushButton, QDateEdit, QLabel
)
from PyQt5.QtCore import pyqtSignal, QDate


class SearchWidget(QWidget):
    search_requested = pyqtSignal(str, str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Поиск по названию или описанию...")
        self.search_edit.returnPressed.connect(self._emit_search)

        layout.addWidget(QLabel("Поиск:"))
        layout.addWidget(self.search_edit)

        layout.addWidget(QLabel("С:"))
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate(2000, 1, 1))
        layout.addWidget(self.date_from)

        layout.addWidget(QLabel("По:"))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        layout.addWidget(self.date_to)

        search_btn = QPushButton("Найти")
        search_btn.clicked.connect(self._emit_search)
        layout.addWidget(search_btn)

        reset_btn = QPushButton("Сброс")
        reset_btn.clicked.connect(self._reset)
        layout.addWidget(reset_btn)

    def _emit_search(self):
        text = self.search_edit.text().strip()
        date_from = self.date_from.date().toString("yyyy-MM-dd")
        date_to = self.date_to.date().toString("yyyy-MM-dd")
        self.search_requested.emit(text, date_from, date_to)

    def _reset(self):
        self.search_edit.clear()
        self.search_requested.emit("", "", "")
