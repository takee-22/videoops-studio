import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal


TIME_PATTERN = re.compile(r"^(\d{2}:)?\d{2}:\d{2}(\.\d+)?$|^\d+(\.\d+)?$")


def is_valid_time(value: str) -> bool:
    value = value.strip()
    if not value:
        return False
    return bool(TIME_PATTERN.match(value))


def normalize_time(value: str) -> str:
    return value.strip()


def find_ffmpeg() -> str:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe

    common_paths = [
        r"C:\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
    ]

    for path in common_paths:
        if os.path.exists(path):
            return path

    return "ffmpeg"


def find_ffprobe() -> str:
    exe = shutil.which("ffprobe")
    if exe:
        return exe

    common_paths = [
        r"C:\ffmpeg\bin\ffprobe.exe",
        r"C:\Program Files\ffmpeg\bin\ffprobe.exe",
        r"C:\Program Files (x86)\ffmpeg\bin\ffprobe.exe",
    ]

    for path in common_paths:
        if os.path.exists(path):
            return path

    return "ffprobe"


def probe_media_info(file_path: str) -> dict:
    ffprobe = find_ffprobe()

    cmd = [
        ffprobe,
        "-v", "error",
        "-show_entries",
        "format=duration,size,bit_rate:stream=index,codec_type,codec_name,width,height,r_frame_rate",
        "-of", "default=noprint_wrappers=1",
        file_path
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True
        )
        return parse_ffprobe_output(result.stdout)
    except Exception as e:
        return {"error": str(e)}


def parse_ffprobe_output(text: str) -> dict:
    info = {
        "duration": "",
        "size": "",
        "bit_rate": "",
        "video_codec": "",
        "audio_codec": "",
        "width": "",
        "height": "",
        "fps": "",
    }

    current_codec_type = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if "=" not in line:
            continue

        key, value = line.split("=", 1)

        if key == "codec_type":
            current_codec_type = value

        elif key == "codec_name":
            if current_codec_type == "video" and not info["video_codec"]:
                info["video_codec"] = value
            elif current_codec_type == "audio" and not info["audio_codec"]:
                info["audio_codec"] = value

        elif key == "width" and not info["width"]:
            info["width"] = value

        elif key == "height" and not info["height"]:
            info["height"] = value

        elif key == "r_frame_rate" and not info["fps"]:
            info["fps"] = fps_from_fraction(value)

        elif key in info and not info[key]:
            info[key] = value

    return info


def fps_from_fraction(value: str) -> str:
    try:
        if "/" in value:
            a, b = value.split("/", 1)
            a = float(a)
            b = float(b)
            if b != 0:
                return f"{a / b:.2f}"
        return value
    except Exception:
        return value


def format_bytes(num_bytes: str) -> str:
    try:
        size = float(num_bytes)
    except Exception:
        return num_bytes

    units = ["B", "KB", "MB", "GB", "TB"]
    idx = 0
    while size >= 1024 and idx < len(units) - 1:
        size /= 1024
        idx += 1
    return f"{size:.2f} {units[idx]}"


def format_duration(seconds_text: str) -> str:
    try:
        total = float(seconds_text)
        hours = int(total // 3600)
        minutes = int((total % 3600) // 60)
        seconds = total % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"
    except Exception:
        return seconds_text


class FFmpegWorker(QThread):
    log = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, command: list[str], temp_file_to_delete: str | None = None):
        super().__init__()
        self.command = command
        self.temp_file_to_delete = temp_file_to_delete

    def run(self):
        try:
            self.log.emit("Running command:")
            self.log.emit(" ".join(f'"{x}"' if " " in x else x for x in self.command))
            self.log.emit("")

            process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace"
            )

            assert process.stdout is not None

            for line in process.stdout:
                line = line.rstrip()
                if line:
                    self.log.emit(line)

            process.wait()

            if process.returncode == 0:
                self.finished_signal.emit(True, "Completed successfully.")
            else:
                self.finished_signal.emit(False, f"Process failed with code {process.returncode}.")

        except Exception as e:
            self.finished_signal.emit(False, str(e))

        finally:
            if self.temp_file_to_delete:
                try:
                    if os.path.exists(self.temp_file_to_delete):
                        os.remove(self.temp_file_to_delete)
                except Exception:
                    pass


def create_concat_file(video_paths: list[str]) -> str:
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8")
    try:
        for path in video_paths:
            safe_path = Path(path).as_posix().replace("'", r"'\''")
            temp.write(f"file '{safe_path}'\n")
    finally:
        temp.close()

    return temp.name