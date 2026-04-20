import sys

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QStackedWidget,
)

from .config import load_settings, save_settings
from .splitter import SplitterWidget
from .merger import MergerWidget
from .converter import ConverterWidget


DARK_THEME = """
QWidget {
    background-color: #1e1e1e;
    color: #f0f0f0;
    font-size: 13px;
    font-family: Segoe UI;
}

QMainWindow {
    background-color: #1e1e1e;
}

QLabel {
    color: #f0f0f0;
}

QPushButton {
    background-color: #2d2d2d;
    color: #ffffff;
    border: 1px solid #444444;
    padding: 8px 12px;
    border-radius: 6px;
}

QPushButton:hover {
    background-color: #3a3a3a;
}

QPushButton:pressed {
    background-color: #505050;
}

QLineEdit, QTextEdit, QListWidget, QComboBox {
    background-color: #252526;
    color: #ffffff;
    border: 1px solid #444444;
    border-radius: 6px;
    padding: 6px;
}

QListWidget::item {
    padding: 8px;
    margin: 2px;
}

QListWidget::item:selected {
    background-color: #0078d4;
    color: #ffffff;
    border-radius: 4px;
}
"""

LIGHT_THEME = """
QWidget {
    background-color: #f5f5f5;
    color: #202020;
    font-size: 13px;
    font-family: Segoe UI;
}

QMainWindow {
    background-color: #f5f5f5;
}

QLabel {
    color: #202020;
}

QPushButton {
    background-color: #ffffff;
    color: #202020;
    border: 1px solid #bdbdbd;
    padding: 8px 12px;
    border-radius: 6px;
}

QPushButton:hover {
    background-color: #eaeaea;
}

QPushButton:pressed {
    background-color: #dcdcdc;
}

QLineEdit, QTextEdit, QListWidget, QComboBox {
    background-color: #ffffff;
    color: #202020;
    border: 1px solid #bdbdbd;
    border-radius: 6px;
    padding: 6px;
}

QListWidget::item {
    padding: 8px;
    margin: 2px;
}

QListWidget::item:selected {
    background-color: #cfe8ff;
    color: #000000;
    border-radius: 4px;
}
"""


def apply_theme(app: QApplication, theme_name: str) -> None:
    if theme_name == "light":
        app.setStyleSheet(LIGHT_THEME)
    else:
        app.setStyleSheet(DARK_THEME)


class HomeWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        title = QLabel("VideoOps Studio")
        title.setStyleSheet("font-size: 28px; font-weight: bold;")

        text = QLabel(
            "A PyQt + FFmpeg desktop toolkit for video splitting, merging, and converting.\n\n"
            "Select a tool from the left side."
        )
        text.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(text)
        layout.addStretch()


class MainWindow(QMainWindow):
    def __init__(self, app: QApplication, theme_name: str):
        super().__init__()
        self.app = app
        self.theme_name = theme_name

        self.setWindowTitle("VideoOps Studio")
        self.resize(1200, 760)

        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)

        top_bar = QHBoxLayout()
        title = QLabel("VideoOps Studio")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")

        self.theme_button = QPushButton()
        self.update_theme_button_text()
        self.theme_button.clicked.connect(self.toggle_theme)

        top_bar.addWidget(title)
        top_bar.addStretch()
        top_bar.addWidget(self.theme_button)

        content_layout = QHBoxLayout()

        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(220)
        self.sidebar.addItems([
            "Home",
            "Splitter",
            "Merger",
            "Converter",
        ])
        self.sidebar.currentRowChanged.connect(self.change_page)

        self.stack = QStackedWidget()
        self.stack.addWidget(HomeWidget())
        self.stack.addWidget(SplitterWidget())
        self.stack.addWidget(MergerWidget())
        self.stack.addWidget(ConverterWidget())

        content_layout.addWidget(self.sidebar)
        content_layout.addWidget(self.stack, 1)

        root_layout.addLayout(top_bar)
        root_layout.addLayout(content_layout)

        self.sidebar.setCurrentRow(0)

    def update_theme_button_text(self):
        if self.theme_name == "dark":
            self.theme_button.setText("Switch to Light Mode")
        else:
            self.theme_button.setText("Switch to Dark Mode")

    def toggle_theme(self):
        self.theme_name = "light" if self.theme_name == "dark" else "dark"
        apply_theme(self.app, self.theme_name)
        self.update_theme_button_text()

        settings = load_settings()
        settings["theme"] = self.theme_name
        save_settings(settings)

    def change_page(self, index: int):
        self.stack.setCurrentIndex(index)


def main():
    app = QApplication(sys.argv)

    settings = load_settings()
    theme_name = settings.get("theme", "dark")
    apply_theme(app, theme_name)

    window = MainWindow(app, theme_name)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()