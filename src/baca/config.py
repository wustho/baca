from configparser import ConfigParser
from pathlib import Path
from typing import Literal, cast

from .models import Color, Config, Keymaps
from .utils.systems import determine_image_viewer
from .utils.user_appdirs import retrieve_user_config_file


def parse_keymaps(config_map: str) -> list[str]:
    return [k.strip() for k in config_map.split(",")]


def load_config(config_path: Path) -> Config:
    parser = ConfigParser()
    parser.read(config_path)

    general = parser["General"]
    dark = parser["Color Dark"]
    light = parser["Color Light"]
    keymaps = parser["Keymaps"]

    return Config(
        image_viewer=determine_image_viewer(preferred=general["PreferredImageViewer"]),
        max_text_width=general["MaxTextWidth"],
        text_justification=cast(Literal["default", "center", "full", "right", "left"], general["TextJustification"]),
        pretty=general.getboolean("pretty"),
        dark=Color(
            bg=dark["Background"],
            fg=dark["Foreground"],
            accent=dark["Accent"],
        ),
        light=Color(
            bg=light["Background"],
            fg=light["Foreground"],
            accent=light["Accent"],
        ),
        keymaps=Keymaps(
            toggle_dark=parse_keymaps(keymaps["ToggleLightDark"]),
            scroll_down=parse_keymaps(keymaps["ScrollDown"]),
            scroll_up=parse_keymaps(keymaps["ScrollUp"]),
            page_up=parse_keymaps(keymaps["PageUp"]),
            page_down=parse_keymaps(keymaps["PageDown"]),
            home=parse_keymaps(keymaps["Home"]),
            end=parse_keymaps(keymaps["End"]),
            open_toc=parse_keymaps(keymaps["OpenToc"]),
            open_metadata=parse_keymaps(keymaps["OpenMetadata"]),
            open_help=parse_keymaps(keymaps["OpenHelp"]),
            close=parse_keymaps(keymaps["CloseOrQuit"]),
            screenshot=parse_keymaps(keymaps["Screenshot"]),
        ),
    )


# TODO: add fallback config
# def load_default_config() -> Config:
#     return load_config(DEFAULT_CONFIG)


def load_user_config() -> Config:
    return load_config(retrieve_user_config_file())
