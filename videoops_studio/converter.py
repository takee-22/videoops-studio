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
    QFormLayout,
    QComboBox,
)

from .ffmpeg_utils import FFmpegWorker, find_ffmpeg, probe_media_info, format_bytes, format_duration


class ConverterWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        title = QLabel("Convert / Transcode Video")
        title.setObjectName("panelTitle")

        form = QFormLayout()
        form.setSpacing(12)

        self.input_edit = QLineEdit()
        self.output_edit = QLineEdit()

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

        self.format_combo = QComboBox()
        self.format_combo.addItems(["mp4", "mkv", "avi", "mov"])

        self.video_codec_combo = QComboBox()
        self.video_codec_combo.addItems(["libx264", "libx265", "mpeg4"])

        self.audio_codec_combo = QComboBox()
        self.audio_codec_combo.addItems(["aac", "mp3", "copy"])

        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems([
            "Keep Original",
            "1920x1080",
            "1280x720",
            "854x480",
            "640x360"
        ])

        self.fps_combo = QComboBox()
        self.fps_combo.addItems([
            "Keep Original",
            "60",
            "30",
            "25",
            "24"
        ])

        self.crf_combo = QComboBox()
        self.crf_combo.addItems(["18", "20", "23", "25", "28"])
        self.crf_combo.setCurrentText("23")

        inspect_btn = QPushButton("Inspect Input")
        inspect_btn.clicked.connect(self.inspect_input)

        form.addRow("Input Video", input_row)
        form.addRow("Output File", output_row)
        form.addRow("Format", self.format_combo)
        form.addRow("Video Codec", self.video_codec_combo)
        form.addRow("Audio Codec", self.audio_codec_combo)
        form.addRow("Resolution", self.resolution_combo)
        form.addRow("FPS", self.fps_combo)
        form.addRow("CRF", self.crf_combo)
        form.addRow("", inspect_btn)

        self.info_label = QTextEdit()
        self.info_label.setReadOnly(True)
        self.info_label.setMaximumHeight(150)
        self.info_label.setPlaceholderText("Input video info...")

        self.run_button = QPushButton("Export Converted Video")
        self.run_button.setObjectName("accentButton")
        self.run_button.clicked.connect(self.run_convert)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setPlaceholderText("FFmpeg logs will appear here...")

        layout.addWidget(title)
        layout.addLayout(form)
        layout.addWidget(QLabel("Input Video Info"))
        layout.addWidget(self.info_label)
        layout.addWidget(self.run_button)
        layout.addWidget(QLabel("Logs"))
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
        selected_format = self.format_combo.currentText()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Converted Video",
            f"output.{selected_format}",
            "Video Files (*.mp4 *.mkv *.avi *.mov);;All Files (*.*)"
        )
        if file_path:
            self.output_edit.setText(file_path)

    def inspect_input(self):
        input_file = self.input_edit.text().strip()
        if not input_file:
            QMessageBox.warning(self, "Missing Input", "Please select an input file.")
            return

        info = probe_media_info(input_file)

        if "error" in info:
            self.info_label.setPlainText(f"Error: {info['error']}")
            return

        text = []
        text.append(f"Duration: {format_duration(info.get('duration', ''))}")
        text.append(f"Size: {format_bytes(info.get('size', ''))}")
        text.append(f"Bitrate: {info.get('bit_rate', '')}")
        text.append(f"Video Codec: {info.get('video_codec', '')}")
        text.append(f"Audio Codec: {info.get('audio_codec', '')}")
        text.append(f"Resolution: {info.get('width', '')} x {info.get('height', '')}")
        text.append(f"FPS: {info.get('fps', '')}")

        self.info_label.setPlainText("\n".join(text))

    def append_log(self, text: str):
        self.log_box.append(text)

    def set_running(self, running: bool):
        self.run_button.setEnabled(not running)

    def run_convert(self):
        input_file = self.input_edit.text().strip()
        output_file = self.output_edit.text().strip()

        if not input_file:
            QMessageBox.warning(self, "Missing Input", "Please select an input video.")
            return

        if not output_file:
            QMessageBox.warning(self, "Missing Output", "Please select an output file.")
            return

        ffmpeg = find_ffmpeg()

        video_codec = self.video_codec_combo.currentText()
        audio_codec = self.audio_codec_combo.currentText()
        resolution = self.resolution_combo.currentText()
        fps = self.fps_combo.currentText()
        crf = self.crf_combo.currentText()

        cmd = [
            ffmpeg,
            "-y",
            "-i", input_file,
            "-c:v", video_codec
        ]

        if video_codec in {"libx264", "libx265"}:
            cmd += ["-crf", crf, "-preset", "medium"]

        if audio_codec == "copy":
            cmd += ["-c:a", "copy"]
        else:
            cmd += ["-c:a", audio_codec, "-b:a", "192k"]

        if resolution != "Keep Original":
            cmd += ["-vf", f"scale={resolution}"]

        if fps != "Keep Original":
            cmd += ["-r", fps]

        cmd.append(output_file)

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