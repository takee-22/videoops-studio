from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QListWidget,
    QMessageBox, QLabel, QComboBox, QPlainTextEdit
)

from videoops_studio.ffmpeg_utils import (
    POPULAR_INPUT_FILTER,
    POPULAR_OUTPUT_EXTS,
    ffmpeg_exists,
    convert_video,
)


class ConverterTab(QWidget):
    def __init__(self):
        super().__init__()

        self.listbox = QListWidget()
        self.output_dir = ""

        self.btn_add = QPushButton("Add Files")
        self.btn_remove = QPushButton("Remove Selected")
        self.btn_pick_folder = QPushButton("Choose Output Folder")
        self.btn_convert = QPushButton("Convert")

        self.lbl_output_dir = QLabel("No output folder selected")

        self.cmb_format = QComboBox()
        self.cmb_format.addItems(POPULAR_OUTPUT_EXTS)

        self.cmb_mode = QComboBox()
        self.cmb_mode.addItems(["safe", "copy"])
        self.cmb_mode.setCurrentText("safe")

        self.log_box = QPlainTextEdit()
        self.log_box.setReadOnly(True)

        main = QVBoxLayout(self)
        row1 = QHBoxLayout()
        row2 = QHBoxLayout()
        row3 = QHBoxLayout()

        row1.addWidget(self.btn_add)
        row1.addWidget(self.btn_remove)

        row2.addWidget(QLabel("Output Folder:"))
        row2.addWidget(self.lbl_output_dir)
        row2.addWidget(self.btn_pick_folder)

        row3.addWidget(QLabel("Output Format:"))
        row3.addWidget(self.cmb_format)
        row3.addSpacing(12)
        row3.addWidget(QLabel("Mode:"))
        row3.addWidget(self.cmb_mode)
        row3.addStretch()
        row3.addWidget(self.btn_convert)

        main.addLayout(row1)
        main.addWidget(self.listbox)
        main.addLayout(row2)
        main.addLayout(row3)
        main.addWidget(QLabel("Log"))
        main.addWidget(self.log_box)

        self.btn_add.clicked.connect(self.add_files)
        self.btn_remove.clicked.connect(self.remove_selected)
        self.btn_pick_folder.clicked.connect(self.pick_output_folder)
        self.btn_convert.clicked.connect(self.run_convert)

    def log(self, text: str):
        self.log_box.appendPlainText(text)

    def files(self) -> list[str]:
        return [self.listbox.item(i).text() for i in range(self.listbox.count())]

    def add_files(self):
        if not ffmpeg_exists():
            QMessageBox.critical(self, "Missing FFmpeg", "ffmpeg not found in PATH.")
            return

        files, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", POPULAR_INPUT_FILTER)
        if not files:
            return

        for file in files:
            self.listbox.addItem(file)

    def remove_selected(self):
        row = self.listbox.currentRow()
        if row >= 0:
            self.listbox.takeItem(row)

    def pick_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if not folder:
            return
        self.output_dir = folder
        self.lbl_output_dir.setText(folder)

    def run_convert(self):
        files = self.files()
        if not files:
            QMessageBox.warning(self, "No Files", "Add files first.")
            return

        if not self.output_dir:
            QMessageBox.warning(self, "No Output Folder", "Choose an output folder.")
            return

        out_ext = self.cmb_format.currentText()
        mode = self.cmb_mode.currentText()

        for file in files:
            src = Path(file)
            final_mode = "safe" if src.suffix.lower() == ".dav" else mode
            out_file = str(Path(self.output_dir) / f"{src.stem}.{out_ext}")

            self.log(f"Converting: {file}")
            self.log(f"Output: {out_file}")
            self.log(f"Mode: {final_mode}")

            ok, out = convert_video(file, out_file, final_mode)
            self.log(out)

            if not ok:
                QMessageBox.critical(self, "Conversion Failed", f"Failed on:\n{file}")
                return

        QMessageBox.information(self, "Done", "All files converted successfully.")