from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont, QCursor


class ClickableLabel(QLabel):
    clicked = pyqtSignal(str)

    def __init__(self, text, tag_name, parent=None):
        super().__init__(text, parent)
        self.tag_name = tag_name
        self.setCursor(QCursor(Qt.PointingHandCursor))

    def mousePressEvent(self, event):
        self.clicked.emit(self.tag_name)
        super().mousePressEvent(event)


class TagCloud(QWidget):
    tag_clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QGridLayout(self)
        self.layout.setSpacing(8)

    def update_tags(self, tag_counts):
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not tag_counts:
            self.layout.addWidget(QLabel("Нет тегов"), 0, 0)
            return

        max_count = max(tag_counts.values())
        min_count = min(tag_counts.values())

        row, col = 0, 0
        max_cols = 6
        for name, count in tag_counts.items():
            font_size = self._calculate_font_size(count, max_count, min_count)
            label = ClickableLabel(name, name)
            font = QFont()
            font.setPointSize(font_size)
            label.setFont(font)
            label.clicked.connect(self.tag_clicked.emit)
            self.layout.addWidget(label, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    @staticmethod
    def _calculate_font_size(count, max_count, min_count):
        if max_count == min_count:
            return 12
        normalized = (count - min_count) / (max_count - min_count)
        return int(10 + normalized * 14)
