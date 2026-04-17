from pathlib import Path

from PySide6.QtCore import QUrl, Qt
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QLabel,
    QSlider, QListWidget, QMessageBox, QComboBox, QPlainTextEdit
)

from videoops_studio.ffmpeg_utils import (
    POPULAR_INPUT_FILTER,
    POPULAR_OUTPUT_EXTS,
    ffmpeg_exists,
    ffprobe_exists,
    get_duration_seconds,
    ms_to_readable,
    split_into_segments,
)


class SplitterTab(QWidget):
    def __init__(self):
        super().__init__()

        self.input_path = ""
        self.duration_ms = 0
        self.markers_ms = []

        self.player = QMediaPlayer()
        self.audio = QAudioOutput()
        self.player.setAudioOutput(self.audio)
        self.audio.setVolume(1.0)

        self.video_widget = QVideoWidget()
        self.player.setVideoOutput(self.video_widget)

        self.lbl_file = QLabel("No video loaded")
        self.lbl_time = QLabel("00:00:00 / 00:00:00")

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)

        self.btn_open = QPushButton("Open Video")
        self.btn_play = QPushButton("Play / Pause")
        self.btn_back_5 = QPushButton("-5s")
        self.btn_fwd_5 = QPushButton("+5s")
        self.btn_back_30 = QPushButton("-30s")
        self.btn_fwd_30 = QPushButton("+30s")
        self.btn_add_marker = QPushButton("Add Cut Point")
        self.btn_remove_marker = QPushButton("Remove Selected")
        self.btn_clear_markers = QPushButton("Clear All")
        self.btn_export = QPushButton("Export Segments")

        self.cmb_format = QComboBox()
        self.cmb_format.addItems(POPULAR_OUTPUT_EXTS)

        self.cmb_mode = QComboBox()
        self.cmb_mode.addItems(["safe", "copy"])
        self.cmb_mode.setCurrentText("safe")

        self.marker_list = QListWidget()
        self.log_box = QPlainTextEdit()
        self.log_box.setReadOnly(True)

        main = QVBoxLayout(self)
        top_row = QHBoxLayout()
        ctrl_row = QHBoxLayout()
        marker_row = QHBoxLayout()
        export_row = QHBoxLayout()

        top_row.addWidget(self.btn_open)
        top_row.addWidget(self.lbl_file)

        ctrl_row.addWidget(self.btn_back_30)
        ctrl_row.addWidget(self.btn_back_5)
        ctrl_row.addWidget(self.btn_play)
        ctrl_row.addWidget(self.btn_fwd_5)
        ctrl_row.addWidget(self.btn_fwd_30)

        marker_row.addWidget(self.btn_add_marker)
        marker_row.addWidget(self.btn_remove_marker)
        marker_row.addWidget(self.btn_clear_markers)

        export_row.addWidget(QLabel("Output Format:"))
        export_row.addWidget(self.cmb_format)
        export_row.addSpacing(12)
        export_row.addWidget(QLabel("Mode:"))
        export_row.addWidget(self.cmb_mode)
        export_row.addStretch()
        export_row.addWidget(self.btn_export)

        main.addLayout(top_row)
        main.addWidget(self.video_widget, stretch=1)
        main.addWidget(self.lbl_time)
        main.addWidget(self.slider)
        main.addLayout(ctrl_row)
        main.addWidget(QLabel("Cut Points"))
        main.addWidget(self.marker_list)
        main.addLayout(marker_row)
        main.addLayout(export_row)
        main.addWidget(QLabel("Log"))
        main.addWidget(self.log_box)

        self.btn_open.clicked.connect(self.open_video)
        self.btn_play.clicked.connect(self.toggle_play)
        self.btn_back_5.clicked.connect(lambda: self.seek_relative(-5000))
        self.btn_fwd_5.clicked.connect(lambda: self.seek_relative(5000))
        self.btn_back_30.clicked.connect(lambda: self.seek_relative(-30000))
        self.btn_fwd_30.clicked.connect(lambda: self.seek_relative(30000))
        self.btn_add_marker.clicked.connect(self.add_marker)
        self.btn_remove_marker.clicked.connect(self.remove_marker)
        self.btn_clear_markers.clicked.connect(self.clear_markers)
        self.btn_export.clicked.connect(self.export_segments)

        self.slider.sliderMoved.connect(self.player.setPosition)
        self.player.positionChanged.connect(self.on_position_changed)
        self.player.durationChanged.connect(self.on_duration_changed)

    def log(self, text: str):
        self.log_box.appendPlainText(text)

    def open_video(self):
        if not ffmpeg_exists() or not ffprobe_exists():
            QMessageBox.critical(self, "Missing FFmpeg", "ffmpeg or ffprobe not found in PATH.")
            return

        file, _ = QFileDialog.getOpenFileName(self, "Open Video", "", POPULAR_INPUT_FILTER)
        if not file:
            return

        self.input_path = file
        self.lbl_file.setText(file)
        self.player.setSource(QUrl.fromLocalFile(file))
        self.player.pause()
        self.markers_ms.clear()
        self.marker_list.clear()
        self.log(f"Loaded: {file}")

    def toggle_play(self):
        if not self.input_path:
            return
        if self.player.isPlaying():
            self.player.pause()
        else:
            self.player.play()

    def seek_relative(self, delta_ms: int):
        pos = self.player.position() + delta_ms
        pos = max(0, min(pos, self.duration_ms))
        self.player.setPosition(pos)

    def add_marker(self):
        if not self.input_path:
            return

        pos = self.player.position()
        if pos <= 0 or pos >= self.duration_ms:
            QMessageBox.warning(self, "Invalid Point", "Move to a point inside the video.")
            return

        if pos not in self.markers_ms:
            self.markers_ms.append(pos)
            self.markers_ms.sort()
            self.refresh_markers()

    def remove_marker(self):
        row = self.marker_list.currentRow()
        if row < 0:
            return
        value = self.marker_list.item(row).data(Qt.UserRole)
        if value in self.markers_ms:
            self.markers_ms.remove(value)
        self.refresh_markers()

    def clear_markers(self):
        self.markers_ms.clear()
        self.refresh_markers()

    def refresh_markers(self):
        self.marker_list.clear()
        for ms in self.markers_ms:
            label = ms_to_readable(ms)
            item_text = f"{label}"
            self.marker_list.addItem(item_text)
            self.marker_list.item(self.marker_list.count() - 1).setData(Qt.UserRole, ms)

    def on_position_changed(self, pos: int):
        if not self.slider.isSliderDown():
            self.slider.setValue(pos)
        self.lbl_time.setText(f"{ms_to_readable(pos)} / {ms_to_readable(self.duration_ms)}")

    def on_duration_changed(self, duration: int):
        self.duration_ms = duration
        self.slider.setRange(0, duration)
        self.lbl_time.setText(f"{ms_to_readable(self.player.position())} / {ms_to_readable(duration)}")

    def export_segments(self):
        if not self.input_path:
            QMessageBox.warning(self, "No Video", "Open a video first.")
            return

        try:
            total_duration = get_duration_seconds(self.input_path)
        except Exception as e:
            QMessageBox.critical(self, "Duration Error", str(e))
            return

        markers_sec = [m / 1000.0 for m in self.markers_ms]
        if not markers_sec:
            QMessageBox.warning(self, "No Cut Points", "Add at least one cut point.")
            return

        out_dir = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if not out_dir:
            return

        out_ext = self.cmb_format.currentText()
        mode = self.cmb_mode.currentText()

        if Path(self.input_path).suffix.lower() == ".dav":
            mode = "safe"

        self.log(f"Exporting {len(markers_sec) + 1} segments...")
        self.log(f"Duration: {total_duration:.2f}s")
        self.log(f"Mode: {mode}, Format: {out_ext}")

        ok, out = split_into_segments(self.input_path, markers_sec, out_dir, out_ext, mode)
        self.log(out)

        if ok:
            QMessageBox.information(self, "Done", "Segments exported successfully.")
        else:
            QMessageBox.critical(self, "Export Failed", "See log for details.")