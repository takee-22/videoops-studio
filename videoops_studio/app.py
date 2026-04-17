import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QMessageBox
from PySide6.QtGui import QAction

from videoops_studio.splitter import SplitterTab
from videoops_studio.merger import MergerTab
from videoops_studio.converter import ConverterTab
from videoops_studio.ffmpeg_utils import ffmpeg_exists, ffprobe_exists


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VideoOps Studio")
        self.resize(1200, 800)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.splitter_tab = SplitterTab()
        self.merger_tab = MergerTab()
        self.converter_tab = ConverterTab()

        self.tabs.addTab(self.splitter_tab, "Cut / Split")
        self.tabs.addTab(self.merger_tab, "Merge")
        self.tabs.addTab(self.converter_tab, "Convert")

        self.create_menu()
        self.check_tools()

    def create_menu(self):
        menu = self.menuBar().addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        menu.addAction(about_action)

    def show_about(self):
        QMessageBox.information(
            self,
            "About",
            "VideoOps Studio\n\n"
            "Features:\n"
            "- Visual split into 2 or many parts\n"
            "- Smart merge naming\n"
            "- DAV-safe conversion mode\n"
            "- Popular input/output formats",
        )

    def check_tools(self):
        missing = []
        if not ffmpeg_exists():
            missing.append("ffmpeg")
        if not ffprobe_exists():
            missing.append("ffprobe")

        if missing:
            QMessageBox.warning(
                self,
                "Missing Tools",
                "Missing from PATH: " + ", ".join(missing)
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())