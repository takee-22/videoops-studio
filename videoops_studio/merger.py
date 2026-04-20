from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QTextEdit,
    QMessageBox,
    QListWidget,
    QCheckBox,
    QLineEdit,
)

from .ffmpeg_utils import FFmpegWorker, find_ffmpeg, create_concat_file


class MergerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        title = QLabel("Merge Videos")
        title.setObjectName("panelTitle")

        self.file_list = QListWidget()
        self.file_list.setMinimumHeight(220)

        row1 = QHBoxLayout()
        add_btn = QPushButton("Add Files")
        remove_btn = QPushButton("Remove")
        up_btn = QPushButton("Move Up")
        down_btn = QPushButton("Move Down")

        add_btn.clicked.connect(self.add_files)
        remove_btn.clicked.connect(self.remove_selected)
        up_btn.clicked.connect(self.move_up)
        down_btn.clicked.connect(self.move_down)

        row1.addWidget(add_btn)
        row1.addWidget(remove_btn)
        row1.addWidget(up_btn)
        row1.addWidget(down_btn)

        output_row = QHBoxLayout()
        self.output_edit = QLineEdit()
        output_btn = QPushButton("Save As")
        output_btn.clicked.connect(self.browse_output)
        output_row.addWidget(self.output_edit)
        output_row.addWidget(output_btn)

        self.lossless_checkbox = QCheckBox("Use concat + copy for fast merge")
        self.lossless_checkbox.setChecked(True)

        self.run_button = QPushButton("Export Merge")
        self.run_button.setObjectName("accentButton")
        self.run_button.clicked.connect(self.run_merge)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setPlaceholderText("FFmpeg logs will appear here...")

        layout.addWidget(title)
        layout.addWidget(QLabel("Clip Queue"))
        layout.addWidget(self.file_list)
        layout.addLayout(row1)
        layout.addWidget(QLabel("Output File"))
        layout.addLayout(output_row)
        layout.addWidget(self.lossless_checkbox)
        layout.addWidget(self.run_button)
        layout.addWidget(QLabel("Logs"))
        layout.addWidget(self.log_box)

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Video Files",
            "",
            "Video Files (*.mp4 *.mkv *.avi *.mov *.dav *.ts *.wmv);;All Files (*.*)"
        )
        for file_path in files:
            self.file_list.addItem(file_path)

    def remove_selected(self):
        row = self.file_list.currentRow()
        if row >= 0:
            self.file_list.takeItem(row)

    def move_up(self):
        row = self.file_list.currentRow()
        if row > 0:
            item = self.file_list.takeItem(row)
            self.file_list.insertItem(row - 1, item)
            self.file_list.setCurrentRow(row - 1)

    def move_down(self):
        row = self.file_list.currentRow()
        if row < self.file_list.count() - 1 and row >= 0:
            item = self.file_list.takeItem(row)
            self.file_list.insertItem(row + 1, item)
            self.file_list.setCurrentRow(row + 1)

    def browse_output(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Merged Video",
            "",
            "MP4 Files (*.mp4);;MKV Files (*.mkv);;AVI Files (*.avi);;All Files (*.*)"
        )
        if file_path:
            self.output_edit.setText(file_path)

    def append_log(self, text: str):
        self.log_box.append(text)

    def set_running(self, running: bool):
        self.run_button.setEnabled(not running)

    def run_merge(self):
        files = [self.file_list.item(i).text() for i in range(self.file_list.count())]
        output_file = self.output_edit.text().strip()

        if len(files) < 2:
            QMessageBox.warning(self, "Not Enough Files", "Please add at least 2 video files.")
            return

        if not output_file:
            QMessageBox.warning(self, "Missing Output", "Please select an output file.")
            return

        ffmpeg = find_ffmpeg()
        temp_concat_file = create_concat_file(files)

        if self.lossless_checkbox.isChecked():
            cmd = [
                ffmpeg,
                "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", temp_concat_file,
                "-c", "copy",
                output_file
            ]
        else:
            cmd = [
                ffmpeg,
                "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", temp_concat_file,
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "23",
                "-c:a", "aac",
                "-b:a", "192k",
                output_file
            ]

        self.log_box.clear()
        self.set_running(True)

        self.worker = FFmpegWorker(cmd, temp_file_to_delete=temp_concat_file)
        self.worker.log.connect(self.append_log)
        self.worker.finished_signal.connect(self.on_finished)
        self.worker.start()

    def on_finished(self, success: bool, message: str):
        self.set_running(False)
        self.append_log("")
        self.append_log(message)

        if success:
            QMessageBox.information(self, "Done", message)
        else:
            QMessageBox.critical(self, "Error", message)