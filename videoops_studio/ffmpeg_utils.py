import os
import re
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path


POPULAR_INPUT_FILTER = (
    "Video Files (*.mp4 *.mov *.mkv *.avi *.mpeg *.mpg *.dav *.wmv *.m4v *.ts *.mts *.m2ts);;"
    "All Files (*.*)"
)

POPULAR_OUTPUT_EXTS = ["mp4", "mkv", "mov", "avi", "mpeg"]


def ffmpeg_exists() -> bool:
    return shutil.which("ffmpeg") is not None


def ffprobe_exists() -> bool:
    return shutil.which("ffprobe") is not None


def run_cmd(cmd: list[str]) -> tuple[bool, str]:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        ok = result.returncode == 0
        output = (result.stdout or "") + ("\n" + result.stderr if result.stderr else "")
        return ok, output.strip()
    except Exception as e:
        return False, str(e)


def sec_to_hms(seconds: float) -> str:
    seconds = max(0.0, float(seconds))
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hrs:02d}:{mins:02d}:{secs:06.3f}"


def ms_to_readable(ms: int) -> str:
    total_seconds = max(0, ms // 1000)
    hrs = total_seconds // 3600
    mins = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hrs:02d}:{mins:02d}:{secs:02d}"


def get_duration_seconds(path: str) -> float:
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        path,
    ]
    ok, out = run_cmd(cmd)
    if not ok:
        raise RuntimeError(out)
    return float(out.strip())


def sanitize_name(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*]+', "_", name).strip(" ._")


def input_ext(path: str) -> str:
    return Path(path).suffix.lower().lstrip(".")


def is_dav(path: str) -> bool:
    return input_ext(path) == "dav"


def smart_merge_name(files: list[str], out_ext: str) -> str:
    if not files:
        return f"merged_output.{out_ext}"

    pattern = re.compile(r"(\d{2}\.\d{2}\.\d{2})-(\d{2}\.\d{2}\.\d{2})", re.IGNORECASE)

    first_base = Path(files[0]).stem
    last_base = Path(files[-1]).stem

    m1 = pattern.search(first_base)
    m2 = pattern.search(last_base)

    if m1 and m2:
        start_part = m1.group(1)
        end_part = m2.group(2)
        return f"{start_part}-{end_part}.{out_ext}"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"merged_{timestamp}.{out_ext}"


def segment_output_name(src_path: str, idx: int, start_sec: float, end_sec: float, out_ext: str) -> str:
    base = Path(src_path).stem
    start_txt = sec_to_hms(start_sec).replace(":", ".")[:8]
    end_txt = sec_to_hms(end_sec).replace(":", ".")[:8]
    safe_base = sanitize_name(base)
    return f"{safe_base}_part{idx:02d}_{start_txt}-{end_txt}.{out_ext}"


def codec_args_for_ext(ext: str) -> list[str]:
    ext = ext.lower()

    if ext in {"mp4", "mov", "mkv"}:
        return ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-c:a", "aac", "-b:a", "192k"]

    if ext == "avi":
        return ["-c:v", "mpeg4", "-q:v", "2", "-c:a", "mp3", "-b:a", "192k"]

    if ext == "mpeg":
        return ["-c:v", "mpeg2video", "-q:v", "2", "-c:a", "mp2", "-b:a", "192k"]

    return ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-c:a", "aac", "-b:a", "192k"]


def convert_video(input_file: str, output_file: str, mode: str) -> tuple[bool, str]:
    out_ext = input_ext(output_file)

    if mode == "copy" and not is_dav(input_file):
        cmd = ["ffmpeg", "-y", "-i", input_file, "-c", "copy", output_file]
    else:
        # Safe mode is better for DAV timestamp issues.
        cmd = ["ffmpeg", "-y", "-fflags", "+genpts", "-i", input_file, *codec_args_for_ext(out_ext), output_file]

    return run_cmd(cmd)


def export_segment(input_file: str, start_sec: float, end_sec: float, output_file: str, mode: str) -> tuple[bool, str]:
    out_ext = input_ext(output_file)
    duration = max(0.001, end_sec - start_sec)

    if mode == "copy" and not is_dav(input_file):
        cmd = [
            "ffmpeg", "-y",
            "-ss", sec_to_hms(start_sec),
            "-i", input_file,
            "-t", f"{duration:.3f}",
            "-c", "copy",
            output_file,
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            "-fflags", "+genpts",
            "-ss", sec_to_hms(start_sec),
            "-i", input_file,
            "-t", f"{duration:.3f}",
            *codec_args_for_ext(out_ext),
            output_file,
        ]

    return run_cmd(cmd)


def split_into_segments(
    input_file: str,
    markers_sec: list[float],
    output_dir: str,
    out_ext: str,
    mode: str,
) -> tuple[bool, str]:
    total_duration = get_duration_seconds(input_file)
    valid_markers = sorted(set(x for x in markers_sec if 0 < x < total_duration))

    points = [0.0] + valid_markers + [total_duration]
    logs = []

    for i in range(len(points) - 1):
        start_sec = points[i]
        end_sec = points[i + 1]
        out_name = segment_output_name(input_file, i + 1, start_sec, end_sec, out_ext)
        out_path = str(Path(output_dir) / out_name)

        ok, out = export_segment(input_file, start_sec, end_sec, out_path, mode)
        logs.append(f"[SEGMENT {i + 1}] {out_name}\n{out}\n")
        if not ok:
            return False, "\n".join(logs)

    return True, "\n".join(logs)


def merge_videos(files: list[str], output_file: str, mode: str) -> tuple[bool, str]:
    if len(files) < 2:
        return False, "Need at least 2 files."

    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt", encoding="utf-8") as tf:
        list_path = tf.name
        for file in files:
            safe = file.replace("\\", "/").replace("'", r"'\''")
            tf.write(f"file '{safe}'\n")

    try:
        if mode == "copy" and not any(is_dav(f) for f in files):
            cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path, "-c", "copy", output_file]
        else:
            out_ext = input_ext(output_file)
            cmd = [
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0", "-i", list_path,
                *codec_args_for_ext(out_ext),
                output_file,
            ]
        return run_cmd(cmd)
    finally:
        try:
            os.remove(list_path)
        except OSError:
            pass