from configparser import ConfigParser
from pathlib import Path
from typing import Literal, cast

from .models import Color, Config, Keymaps
from .utils.user_appdirs import retrieve_user_config_file


def load_config(config_path: Path) -> Config:
    parser = ConfigParser()
    parser.read(config_path)

    general = parser["General"]
    dark = parser["Color Dark"]
    light = parser["Color Light"]
    keymaps = parser["Keymaps"]

    return Config(
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
            toggle_dark=keymaps["ToggleLightDark"].split(","),
            scroll_down=keymaps["ScrollDown"].split(","),
            scroll_up=keymaps["ScrollUp"].split(","),
            page_up=keymaps["PageUp"].split(","),
            page_down=keymaps["PageDown"].split(","),
            home=keymaps["Home"].split(","),
            end=keymaps["End"].split(","),
            open_toc=keymaps["OpenToc"].split(","),
            open_metadata=keymaps["OpenMetadata"].split(","),
            open_help=keymaps["OpenHelp"].split(","),
            close=keymaps["CloseOrQuit"].split(","),
            screenshot=keymaps["Screenshot"].split(","),
        ),
    )


# TODO: add fallback config
# def load_default_config() -> Config:
#     return load_config(DEFAULT_CONFIG)


def load_user_config() -> Config:
    return load_config(retrieve_user_config_file())
