from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QTextEdit,
    QMessageBox,
    QCheckBox,
    QFormLayout,
)

from .ffmpeg_utils import (
    FFmpegWorker,
    find_ffmpeg,
    is_valid_time,
    normalize_time,
)


class SplitterWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Video Splitter / Cutter")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")

        form = QFormLayout()

        self.input_edit = QLineEdit()
        self.output_edit = QLineEdit()
        self.start_edit = QLineEdit()
        self.end_edit = QLineEdit()

        self.start_edit.setPlaceholderText("Example: 00:00:10")
        self.end_edit.setPlaceholderText("Example: 00:01:30")

        input_row = QHBoxLayout()
        input_row.addWidget(self.input_edit)
        input_browse = QPushButton("Browse")
        input_browse.clicked.connect(self.browse_input)
        input_row.addWidget(input_browse)

        output_row = QHBoxLayout()
        output_row.addWidget(self.output_edit)
        output_browse = QPushButton("Save As")
        output_browse.clicked.connect(self.browse_output)
        output_row.addWidget(output_browse)

        form.addRow("Input Video:", input_row)
        form.addRow("Output File:", output_row)
        form.addRow("Start Time:", self.start_edit)
        form.addRow("End Time:", self.end_edit)

        self.lossless_checkbox = QCheckBox("Use lossless cut (-c copy)")
        self.lossless_checkbox.setChecked(True)

        self.run_button = QPushButton("Start Split")
        self.run_button.clicked.connect(self.run_split)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)

        layout.addWidget(title)
        layout.addLayout(form)
        layout.addWidget(self.lossless_checkbox)
        layout.addWidget(self.run_button)
        layout.addWidget(QLabel("Logs:"))
        layout.addWidget(self.log_box)

    def browse_input(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Input Video",
            "",
            "Video Files (*.mp4 *.mkv *.avi *.mov *.dav *.ts *.wmv);;All Files (*.*)"
        )
        if file_path:
            self.input_edit.setText(file_path)

    def browse_output(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Output Video",
            "",
            "MP4 Files (*.mp4);;MKV Files (*.mkv);;AVI Files (*.avi);;All Files (*.*)"
        )
        if file_path:
            self.output_edit.setText(file_path)

    def append_log(self, text: str):
        self.log_box.append(text)

    def set_running(self, running: bool):
        self.run_button.setEnabled(not running)

    def run_split(self):
        input_file = self.input_edit.text().strip()
        output_file = self.output_edit.text().strip()
        start_time = self.start_edit.text().strip()
        end_time = self.end_edit.text().strip()

        if not input_file:
            QMessageBox.warning(self, "Missing Input", "Please select an input video.")
            return

        if not output_file:
            QMessageBox.warning(self, "Missing Output", "Please select an output file.")
            return

        if not start_time or not end_time:
            QMessageBox.warning(self, "Missing Time", "Please provide both start and end times.")
            return

        if not is_valid_time(start_time):
            QMessageBox.warning(self, "Invalid Time", "Start time format is invalid.")
            return

        if not is_valid_time(end_time):
            QMessageBox.warning(self, "Invalid Time", "End time format is invalid.")
            return

        ffmpeg = find_ffmpeg()

        start_time = normalize_time(start_time)
        end_time = normalize_time(end_time)

        if self.lossless_checkbox.isChecked():
            cmd = [
                ffmpeg,
                "-y",
                "-ss", start_time,
                "-to", end_time,
                "-i", input_file,
                "-c", "copy",
                output_file
            ]
        else:
            cmd = [
                ffmpeg,
                "-y",
                "-ss", start_time,
                "-to", end_time,
                "-i", input_file,
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "23",
                "-c:a", "aac",
                "-b:a", "192k",
                output_file
            ]

        self.log_box.clear()
        self.set_running(True)

        self.worker = FFmpegWorker(cmd)
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