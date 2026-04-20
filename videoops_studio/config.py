from pathlib import Path
import json

APP_NAME = "VideoOps Studio"
APP_DIR = Path.home() / ".videoops_studio"
SETTINGS_FILE = APP_DIR / "settings.json"


def ensure_app_dir() -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)


def load_settings() -> dict:
    ensure_app_dir()

    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception:
            pass

    return {
        "theme": "dark"
    }


def save_settings(settings: dict) -> None:
    ensure_app_dir()

    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)