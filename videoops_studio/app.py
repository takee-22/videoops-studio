import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut
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
    QFrame,
    QTextEdit,
    QFileDialog,
    QMessageBox,
)

from .config import load_settings, save_settings
from .splitter import SplitterWidget
from .merger import MergerWidget
from .converter import ConverterWidget


DARK_THEME = """
QWidget {
    background-color: #0f1117;
    color: #e8eaed;
    font-size: 13px;
    font-family: Segoe UI;
}

QMainWindow {
    background-color: #0f1117;
}

QFrame#sidebar {
    background-color: #12161f;
    border-right: 1px solid #252b36;
}

QFrame#previewPanel, QFrame#rightPanel, QFrame#bottomPanel, QFrame#workspacePanel {
    background-color: #151a23;
    border: 1px solid #252b36;
    border-radius: 14px;
}

QLabel#appTitle {
    font-size: 22px;
    font-weight: bold;
    color: #ffffff;
}

QLabel#sectionTitle {
    font-size: 14px;
    font-weight: 600;
    color: #ffffff;
}

QLabel#previewTitle {
    font-size: 16px;
    font-weight: 600;
    color: #ffffff;
}

QLabel#previewBox {
    background-color: #0b0e14;
    border: 1px dashed #3b4454;
    border-radius: 12px;
    color: #9aa4b2;
    font-size: 18px;
    font-weight: 600;
}

QLabel#timelineLabel {
    color: #b6beca;
    font-size: 13px;
}

QLabel#panelTitle {
    font-size: 18px;
    font-weight: 700;
    color: #ffffff;
}

QPushButton {
    background-color: #1a2030;
    color: #e8eaed;
    border: 1px solid #313949;
    padding: 9px 14px;
    border-radius: 10px;
}

QPushButton:hover {
    background-color: #232b3b;
}

QPushButton:pressed {
    background-color: #2f394d;
}

QPushButton#accentButton {
    background-color: #4f8cff;
    color: white;
    border: none;
    font-weight: 600;
}

QPushButton#accentButton:hover {
    background-color: #6a9dff;
}

QPushButton#accentButton:pressed {
    background-color: #3b78ee;
}

QListWidget {
    background-color: transparent;
    border: none;
    outline: none;
    padding: 6px;
}

QListWidget::item {
    background-color: transparent;
    color: #dce1e7;
    padding: 12px;
    margin: 4px 6px;
    border-radius: 10px;
}

QListWidget::item:selected {
    background-color: #1e2a44;
    color: #ffffff;
    border: 1px solid #4f8cff;
}

QLineEdit, QTextEdit, QComboBox {
    background-color: #0f141d;
    color: #eef2f7;
    border: 1px solid #313949;
    border-radius: 10px;
    padding: 8px;
}

QTextEdit {
    padding: 10px;
}

QComboBox {
    padding-right: 24px;
}

QCheckBox {
    spacing: 8px;
    color: #dce1e7;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
}

QCheckBox::indicator:unchecked {
    border: 1px solid #596579;
    background: #10151f;
    border-radius: 4px;
}

QCheckBox::indicator:checked {
    border: 1px solid #4f8cff;
    background: #4f8cff;
    border-radius: 4px;
}
"""


LIGHT_THEME = """
QWidget {
    background-color: #eef2f7;
    color: #20252b;
    font-size: 13px;
    font-family: Segoe UI;
}

QMainWindow {
    background-color: #eef2f7;
}

QFrame#sidebar {
    background-color: #f8fafc;
    border-right: 1px solid #d7dde6;
}

QFrame#previewPanel, QFrame#rightPanel, QFrame#bottomPanel, QFrame#workspacePanel {
    background-color: #ffffff;
    border: 1px solid #d7dde6;
    border-radius: 14px;
}

QLabel#appTitle {
    font-size: 22px;
    font-weight: bold;
    color: #111827;
}

QLabel#sectionTitle {
    font-size: 14px;
    font-weight: 600;
    color: #111827;
}

QLabel#previewTitle {
    font-size: 16px;
    font-weight: 600;
    color: #111827;
}

QLabel#previewBox {
    background-color: #f7f9fc;
    border: 1px dashed #b9c4d3;
    border-radius: 12px;
    color: #667085;
    font-size: 18px;
    font-weight: 600;
}

QLabel#timelineLabel {
    color: #5a6472;
    font-size: 13px;
}

QLabel#panelTitle {
    font-size: 18px;
    font-weight: 700;
    color: #111827;
}

QPushButton {
    background-color: #ffffff;
    color: #111827;
    border: 1px solid #cfd8e3;
    padding: 9px 14px;
    border-radius: 10px;
}

QPushButton:hover {
    background-color: #f3f6fa;
}

QPushButton:pressed {
    background-color: #e8edf4;
}

QPushButton#accentButton {
    background-color: #2563eb;
    color: white;
    border: none;
    font-weight: 600;
}

QPushButton#accentButton:hover {
    background-color: #3d75ee;
}

QPushButton#accentButton:pressed {
    background-color: #1f59d5;
}

QListWidget {
    background-color: transparent;
    border: none;
    outline: none;
    padding: 6px;
}

QListWidget::item {
    background-color: transparent;
    color: #111827;
    padding: 12px;
    margin: 4px 6px;
    border-radius: 10px;
}

QListWidget::item:selected {
    background-color: #e8f0ff;
    color: #111827;
    border: 1px solid #3b82f6;
}

QLineEdit, QTextEdit, QComboBox {
    background-color: #ffffff;
    color: #111827;
    border: 1px solid #cfd8e3;
    border-radius: 10px;
    padding: 8px;
}

QTextEdit {
    padding: 10px;
}

QComboBox {
    padding-right: 24px;
}

QCheckBox {
    spacing: 8px;
    color: #111827;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
}

QCheckBox::indicator:unchecked {
    border: 1px solid #94a3b8;
    background: #ffffff;
    border-radius: 4px;
}

QCheckBox::indicator:checked {
    border: 1px solid #2563eb;
    background: #2563eb;
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
        layout.setSpacing(14)

        title = QLabel("Welcome to VideoOps Studio")
        title.setObjectName("panelTitle")

        text = QLabel(
            "CapCut-style V1 workspace for desktop video operations.\n\n"
            "Use the left sidebar to switch between tools.\n"
            "The upper preview area and lower timeline area are visual editor panels."
        )
        text.setWordWrap(True)

        notes = QTextEdit()
        notes.setReadOnly(True)
        notes.setPlainText(
            "Planned workflow:\n"
            "- Import videos\n"
            "- Preview clips\n"
            "- Split or merge\n"
            "- Convert/export\n"
            "- Add future timeline features later\n\n"
            "Keyboard shortcuts:\n"
            "Ctrl+O = Open File\n"
            "Ctrl+E = Export Project\n"
            "Ctrl+T = Toggle Theme\n"
            "Ctrl+1 = Home\n"
            "Ctrl+2 = Split\n"
            "Ctrl+3 = Merge\n"
            "Ctrl+4 = Convert"
        )

        layout.addWidget(title)
        layout.addWidget(text)
        layout.addWidget(notes)
        layout.addStretch()


class MainWindow(QMainWindow):
    def __init__(self, app: QApplication, theme_name: str):
        super().__init__()
        self.app = app
        self.theme_name = theme_name
        self.last_opened_file = ""

        self.setWindowTitle("VideoOps Studio - CapCut Style V1")
        self.resize(1400, 850)

        central = QWidget()
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.sidebar_frame = QFrame()
        self.sidebar_frame.setObjectName("sidebar")
        self.sidebar_frame.setFixedWidth(240)

        sidebar_layout = QVBoxLayout(self.sidebar_frame)
        sidebar_layout.setContentsMargins(16, 20, 16, 20)
        sidebar_layout.setSpacing(14)

        app_title = QLabel("VideoOps Studio")
        app_title.setObjectName("appTitle")

        app_sub = QLabel("Editor Workspace")
        app_sub.setObjectName("sectionTitle")

        self.theme_button = QPushButton()
        self.update_theme_button_text()
        self.theme_button.clicked.connect(self.toggle_theme)

        self.sidebar = QListWidget()
        self.sidebar.addItems([
            "Home",
            "Split",
            "Merge",
            "Convert",
        ])
        self.sidebar.currentRowChanged.connect(self.change_page)

        sidebar_layout.addWidget(app_title)
        sidebar_layout.addWidget(app_sub)
        sidebar_layout.addWidget(self.theme_button)
        sidebar_layout.addSpacing(8)
        sidebar_layout.addWidget(self.sidebar)
        sidebar_layout.addStretch()

        self.main_area = QWidget()
        main_layout = QVBoxLayout(self.main_area)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(16)

        top_row = QHBoxLayout()
        top_row.setSpacing(16)

        self.preview_panel = QFrame()
        self.preview_panel.setObjectName("previewPanel")
        preview_layout = QVBoxLayout(self.preview_panel)
        preview_layout.setContentsMargins(18, 18, 18, 18)
        preview_layout.setSpacing(12)

        preview_title = QLabel("Preview Monitor")
        preview_title.setObjectName("previewTitle")

        self.preview_box = QLabel("Drop Video Here or Use Import")
        self.preview_box.setObjectName("previewBox")
        self.preview_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_box.setMinimumHeight(260)
        self.preview_box.setWordWrap(True)

        preview_controls = QHBoxLayout()
        preview_controls.setSpacing(10)

        self.import_button = QPushButton("Import")
        self.import_button.clicked.connect(self.open_file_action)

        self.play_button = QPushButton("Play")
        self.pause_button = QPushButton("Pause")
        self.stop_button = QPushButton("Stop")
        self.snapshot_button = QPushButton("Snapshot")

        preview_controls.addWidget(self.import_button)
        preview_controls.addWidget(self.play_button)
        preview_controls.addWidget(self.pause_button)
        preview_controls.addWidget(self.stop_button)
        preview_controls.addStretch()
        preview_controls.addWidget(self.snapshot_button)

        preview_layout.addWidget(preview_title)
        preview_layout.addWidget(self.preview_box)
        preview_layout.addLayout(preview_controls)

        self.right_panel = QFrame()
        self.right_panel.setObjectName("rightPanel")
        self.right_panel.setFixedWidth(300)

        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(16, 16, 16, 16)
        right_layout.setSpacing(12)

        right_title = QLabel("Inspector")
        right_title.setObjectName("sectionTitle")

        self.inspector_box = QTextEdit()
        self.inspector_box.setReadOnly(True)
        self.inspector_box.setPlainText(
            "Project Panel\n\n"
            "- Selected tool info\n"
            "- Output options\n"
            "- Future preview metadata\n"
            "- Timeline/clip settings"
        )

        quick_actions = QLabel("Quick Actions")
        quick_actions.setObjectName("sectionTitle")

        btn_row_1 = QHBoxLayout()
        self.open_file_btn = QPushButton("Open File")
        self.open_file_btn.clicked.connect(self.open_file_action)
        self.open_folder_btn = QPushButton("Open Folder")
        self.open_folder_btn.clicked.connect(self.open_folder_action)
        btn_row_1.addWidget(self.open_file_btn)
        btn_row_1.addWidget(self.open_folder_btn)

        btn_row_2 = QHBoxLayout()
        self.recent_btn = QPushButton("Recent")
        self.export_btn_top = QPushButton("Export")
        self.export_btn_top.clicked.connect(self.export_action)
        btn_row_2.addWidget(self.recent_btn)
        btn_row_2.addWidget(self.export_btn_top)

        right_layout.addWidget(right_title)
        right_layout.addWidget(self.inspector_box)
        right_layout.addWidget(quick_actions)
        right_layout.addLayout(btn_row_1)
        right_layout.addLayout(btn_row_2)
        right_layout.addStretch()

        top_row.addWidget(self.preview_panel, 1)
        top_row.addWidget(self.right_panel)

        self.workspace_panel = QFrame()
        self.workspace_panel.setObjectName("workspacePanel")
        workspace_layout = QVBoxLayout(self.workspace_panel)
        workspace_layout.setContentsMargins(16, 16, 16, 16)
        workspace_layout.setSpacing(12)

        workspace_title = QLabel("Workspace")
        workspace_title.setObjectName("sectionTitle")

        self.stack = QStackedWidget()
        self.stack.addWidget(HomeWidget())
        self.stack.addWidget(SplitterWidget())
        self.stack.addWidget(MergerWidget())
        self.stack.addWidget(ConverterWidget())

        workspace_layout.addWidget(workspace_title)
        workspace_layout.addWidget(self.stack)

        self.bottom_panel = QFrame()
        self.bottom_panel.setObjectName("bottomPanel")
        self.bottom_panel.setFixedHeight(150)

        bottom_layout = QVBoxLayout(self.bottom_panel)
        bottom_layout.setContentsMargins(16, 14, 16, 14)
        bottom_layout.setSpacing(10)

        timeline_title = QLabel("Timeline / Queue")
        timeline_title.setObjectName("sectionTitle")

        timeline_text = QLabel(
            "[ Clip 1 ]    [ Clip 2 ]    [ Clip 3 ]    [ Output Preview ]\n"
            "This is a visual V1 timeline panel. Real drag timeline can be added later."
        )
        timeline_text.setObjectName("timelineLabel")
        timeline_text.setWordWrap(True)

        bottom_buttons = QHBoxLayout()
        self.add_media_btn = QPushButton("Add Media")
        self.add_media_btn.clicked.connect(self.open_file_action)
        bottom_buttons.addWidget(self.add_media_btn)
        bottom_buttons.addWidget(QPushButton("Trim"))
        bottom_buttons.addWidget(QPushButton("Split"))
        bottom_buttons.addWidget(QPushButton("Merge"))
        bottom_buttons.addWidget(QPushButton("Convert"))
        bottom_buttons.addStretch()

        self.export_btn = QPushButton("Export Project")
        self.export_btn.setObjectName("accentButton")
        self.export_btn.clicked.connect(self.export_action)
        bottom_buttons.addWidget(self.export_btn)

        bottom_layout.addWidget(timeline_title)
        bottom_layout.addWidget(timeline_text)
        bottom_layout.addLayout(bottom_buttons)

        main_layout.addLayout(top_row, 4)
        main_layout.addWidget(self.workspace_panel, 4)
        main_layout.addWidget(self.bottom_panel, 2)

        root.addWidget(self.sidebar_frame)
        root.addWidget(self.main_area, 1)

        self.sidebar.setCurrentRow(0)

        self.setup_shortcuts()

    def setup_shortcuts(self):
        self.shortcut_open = QShortcut(QKeySequence("Ctrl+O"), self)
        self.shortcut_open.activated.connect(self.open_file_action)

        self.shortcut_export = QShortcut(QKeySequence("Ctrl+E"), self)
        self.shortcut_export.activated.connect(self.export_action)

        self.shortcut_theme = QShortcut(QKeySequence("Ctrl+T"), self)
        self.shortcut_theme.activated.connect(self.toggle_theme)

        self.shortcut_home = QShortcut(QKeySequence("Ctrl+1"), self)
        self.shortcut_home.activated.connect(lambda: self.sidebar.setCurrentRow(0))

        self.shortcut_split = QShortcut(QKeySequence("Ctrl+2"), self)
        self.shortcut_split.activated.connect(lambda: self.sidebar.setCurrentRow(1))

        self.shortcut_merge = QShortcut(QKeySequence("Ctrl+3"), self)
        self.shortcut_merge.activated.connect(lambda: self.sidebar.setCurrentRow(2))

        self.shortcut_convert = QShortcut(QKeySequence("Ctrl+4"), self)
        self.shortcut_convert.activated.connect(lambda: self.sidebar.setCurrentRow(3))

    def update_theme_button_text(self):
        if self.theme_name == "dark":
            self.theme_button.setText("Switch to Light")
        else:
            self.theme_button.setText("Switch to Dark")

    def toggle_theme(self):
        self.theme_name = "light" if self.theme_name == "dark" else "dark"
        apply_theme(self.app, self.theme_name)
        self.update_theme_button_text()

        settings = load_settings()
        settings["theme"] = self.theme_name
        save_settings(settings)

    def change_page(self, index: int):
        self.stack.setCurrentIndex(index)
        page_names = ["Home", "Split", "Merge", "Convert"]
        current_name = page_names[index] if 0 <= index < len(page_names) else "Unknown"

        self.inspector_box.setPlainText(
            f"Project Panel\n\n"
            f"Current Tool: {current_name}\n"
            f"Last Opened File: {self.last_opened_file or 'None'}\n\n"
            f"Shortcuts:\n"
            f"Ctrl+O = Open File\n"
            f"Ctrl+E = Export Project\n"
            f"Ctrl+T = Toggle Theme\n"
            f"Ctrl+1/2/3/4 = Switch Tools"
        )

    def open_file_action(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Video File",
            "",
            "Video Files (*.mp4 *.mkv *.avi *.mov *.dav *.ts *.wmv);;All Files (*.*)"
        )
        if file_path:
            self.last_opened_file = file_path
            self.preview_box.setText(file_path)
            self.inspector_box.setPlainText(
                f"Project Panel\n\n"
                f"Current Tool: {self.sidebar.currentItem().text() if self.sidebar.currentItem() else 'Unknown'}\n"
                f"Last Opened File:\n{file_path}\n\n"
                f"Shortcuts:\n"
                f"Ctrl+O = Open File\n"
                f"Ctrl+E = Export Project\n"
                f"Ctrl+T = Toggle Theme\n"
                f"Ctrl+1/2/3/4 = Switch Tools"
            )

    def open_folder_action(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Open Folder", "")
        if folder_path:
            self.inspector_box.setPlainText(
                f"Project Panel\n\n"
                f"Opened Folder:\n{folder_path}\n\n"
                f"Last Opened File: {self.last_opened_file or 'None'}"
            )

    def export_action(self):
        QMessageBox.information(
            self,
            "Export Project",
            "Export action triggered.\n\n"
            "You can connect this button later to your final render/export workflow."
        )


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