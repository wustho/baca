from pkg_resources import resource_filename
from configparser import ConfigParser
from typing import Literal, cast

from .models import Config, Color, Keymaps


DEFAULT_CONFIG = resource_filename(__name__, "resources/config.ini")


def load_config(config_path: str = DEFAULT_CONFIG) -> Config:
    parser = ConfigParser()
    parser.read(config_path)

    return Config(
        max_text_width=parser["General"]["MaxTextWidth"],
        text_justification=cast(
            Literal["default", "center", "full", "right", "left"], parser["General"]["TextJustification"]
        ),
        pretty=parser["General"].getboolean("pretty"),
        dark=Color(
            bg=parser["Color Dark"]["Background"],
            fg=parser["Color Dark"]["Foreground"],
            accent=parser["Color Dark"]["Accent"],
        ),
        light=Color(
            bg=parser["Color Light"]["Background"],
            fg=parser["Color Light"]["Foreground"],
            accent=parser["Color Light"]["Accent"],
        ),
        keymaps=Keymaps(
            toggle_dark=parser["Keymaps"]["ToggleLightDark"].split(","),
            scroll_down=parser["Keymaps"]["ScrollDown"].split(","),
            scroll_up=parser["Keymaps"]["ScrollUp"].split(","),
            page_up=parser["Keymaps"]["PageUp"].split(","),
            page_down=parser["Keymaps"]["PageDown"].split(","),
            home=parser["Keymaps"]["Home"].split(","),
            end=parser["Keymaps"]["End"].split(","),
            open_toc=parser["Keymaps"]["OpenToc"].split(","),
            open_metadata=parser["Keymaps"]["OpenMetadata"].split(","),
            open_help=parser["Keymaps"]["OpenHelp"].split(","),
            close=parser["Keymaps"]["CloseOrQuit"].split(","),
            screenshot=parser["Keymaps"]["Screenshot"].split(","),
        ),
    )
