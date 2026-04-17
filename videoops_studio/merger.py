from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QListWidget,
    QMessageBox, QLabel, QComboBox, QPlainTextEdit, QLineEdit
)

from videoops_studio.ffmpeg_utils import (
    POPULAR_INPUT_FILTER,
    POPULAR_OUTPUT_EXTS,
    ffmpeg_exists,
    smart_merge_name,
    merge_videos,
)


class MergerTab(QWidget):
    def __init__(self):
        super().__init__()

        self.listbox = QListWidget()
        self.listbox.setSelectionMode(QListWidget.SingleSelection)

        self.btn_add = QPushButton("Add Videos")
        self.btn_remove = QPushButton("Remove Selected")
        self.btn_up = QPushButton("Move Up")
        self.btn_down = QPushButton("Move Down")
        self.btn_pick_folder = QPushButton("Choose Output Folder")
        self.btn_merge = QPushButton("Merge")

        self.lbl_output_dir = QLabel("No output folder selected")
        self.txt_name_preview = QLineEdit()
        self.txt_name_preview.setPlaceholderText("Output name will appear here")

        self.cmb_format = QComboBox()
        self.cmb_format.addItems(POPULAR_OUTPUT_EXTS)

        self.cmb_mode = QComboBox()
        self.cmb_mode.addItems(["safe", "copy"])
        self.cmb_mode.setCurrentText("safe")

        self.log_box = QPlainTextEdit()
        self.log_box.setReadOnly(True)

        self.output_dir = ""

        main = QVBoxLayout(self)
        row1 = QHBoxLayout()
        row2 = QHBoxLayout()
        row3 = QHBoxLayout()

        row1.addWidget(self.btn_add)
        row1.addWidget(self.btn_remove)
        row1.addWidget(self.btn_up)
        row1.addWidget(self.btn_down)

        row2.addWidget(QLabel("Output Folder:"))
        row2.addWidget(self.lbl_output_dir)
        row2.addWidget(self.btn_pick_folder)

        row3.addWidget(QLabel("Output Format:"))
        row3.addWidget(self.cmb_format)
        row3.addSpacing(12)
        row3.addWidget(QLabel("Mode:"))
        row3.addWidget(self.cmb_mode)
        row3.addStretch()
        row3.addWidget(self.btn_merge)

        main.addLayout(row1)
        main.addWidget(self.listbox)
        main.addWidget(QLabel("Auto Output Name"))
        main.addWidget(self.txt_name_preview)
        main.addLayout(row2)
        main.addLayout(row3)
        main.addWidget(QLabel("Log"))
        main.addWidget(self.log_box)

        self.btn_add.clicked.connect(self.add_files)
        self.btn_remove.clicked.connect(self.remove_selected)
        self.btn_up.clicked.connect(self.move_up)
        self.btn_down.clicked.connect(self.move_down)
        self.btn_pick_folder.clicked.connect(self.pick_output_folder)
        self.btn_merge.clicked.connect(self.run_merge)
        self.cmb_format.currentTextChanged.connect(self.refresh_name_preview)

    def log(self, text: str):
        self.log_box.appendPlainText(text)

    def files(self) -> list[str]:
        return [self.listbox.item(i).text() for i in range(self.listbox.count())]

    def add_files(self):
        if not ffmpeg_exists():
            QMessageBox.critical(self, "Missing FFmpeg", "ffmpeg not found in PATH.")
            return

        files, _ = QFileDialog.getOpenFileNames(self, "Select Videos", "", POPULAR_INPUT_FILTER)
        if not files:
            return

        for file in files:
            self.listbox.addItem(file)

        self.refresh_name_preview()

    def remove_selected(self):
        row = self.listbox.currentRow()
        if row >= 0:
            self.listbox.takeItem(row)
            self.refresh_name_preview()

    def move_up(self):
        row = self.listbox.currentRow()
        if row > 0:
            item = self.listbox.takeItem(row)
            self.listbox.insertItem(row - 1, item)
            self.listbox.setCurrentRow(row - 1)
            self.refresh_name_preview()

    def move_down(self):
        row = self.listbox.currentRow()
        if 0 <= row < self.listbox.count() - 1:
            item = self.listbox.takeItem(row)
            self.listbox.insertItem(row + 1, item)
            self.listbox.setCurrentRow(row + 1)
            self.refresh_name_preview()

    def pick_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if not folder:
            return
        self.output_dir = folder
        self.lbl_output_dir.setText(folder)

    def refresh_name_preview(self):
        out_ext = self.cmb_format.currentText()
        preview = smart_merge_name(self.files(), out_ext)
        self.txt_name_preview.setText(preview)

    def run_merge(self):
        files = self.files()
        if len(files) < 2:
            QMessageBox.warning(self, "Not Enough Files", "Add at least 2 videos.")
            return

        if not self.output_dir:
            QMessageBox.warning(self, "No Output Folder", "Choose an output folder.")
            return

        out_name = self.txt_name_preview.text().strip()
        if not out_name:
            out_name = smart_merge_name(files, self.cmb_format.currentText())

        out_ext = self.cmb_format.currentText()
        if not out_name.lower().endswith(f".{out_ext}"):
            out_name += f".{out_ext}"

        output_file = str(Path(self.output_dir) / out_name)

        mode = self.cmb_mode.currentText()
        if any(Path(f).suffix.lower() == ".dav" for f in files):
            mode = "safe"

        self.log(f"Merging {len(files)} files")
        self.log(f"Output: {output_file}")
        self.log(f"Mode: {mode}")

        ok, out = merge_videos(files, output_file, mode)
        self.log(out)

        if ok:
            QMessageBox.information(self, "Done", "Videos merged successfully.")
        else:
            QMessageBox.critical(self, "Merge Failed", "See log for details.")