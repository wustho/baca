import shutil
import sys

LAUNCHERS = [
    "gnome-open",
    "gvfs-open",
    "xdg-open",
    "kde-open",
]

VIEWERS = [
    *LAUNCHERS,
    "feh",
    "imv",
    "gio",
    "firefox",
]


def determine_image_viewer(preferred: str = "auto") -> str | None:
    if sys.platform == "win32":
        return "start"
    elif sys.platform == "darwin":
        return "open"
    else:
        all_viewers = [preferred, *VIEWERS]
        try:
            return [v for v in all_viewers if shutil.which(v) is not None][0]
        except IndexError:
            return None


def get_system_launcher() -> str | None:
    if sys.platform == "win32":
        return "start"
    elif sys.platform == "darwin":
        return "open"
    else:
        try:
            return [o for o in LAUNCHERS if shutil.which(o) is not None][0]
        except IndexError:
            return None
