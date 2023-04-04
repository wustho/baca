from configparser import ConfigParser
from typing import Literal, cast

from .models import Color, Config, Keymaps
from .utils.user_appdirs import DEFAULT_CONFIG, retrieve_user_config_file


def parse_keymaps(config_map: str) -> list[str]:
    return [k.strip() for k in config_map.split(",")]


def load_config() -> Config:
    user_conf = ConfigParser()
    user_conf.read(retrieve_user_config_file())
    default_conf = ConfigParser()
    default_conf.read(DEFAULT_CONFIG)

    def get_value(section: str, key: str, is_bool: bool = False) -> str | bool:
        section_conf = user_conf[section] if section in user_conf else default_conf[section]
        return (
            section_conf.get(key, default_conf[section][key])
            if not is_bool
            else section_conf.getboolean(key, fallback=default_conf[section].getboolean(key))
        )

    return Config(
        preferred_image_viewer=str(get_value("General", "PreferredImageViewer")),
        max_text_width=str(get_value("General", "MaxTextWidth")),
        text_justification=cast(
            Literal["default", "center", "full", "right", "left"], get_value("General", "TextJustification")
        ),
        pretty=bool(get_value("General", "Pretty", True)),
        page_scroll_duration=float(get_value("General", "PageScrollDuration")),
        dark=Color(
            bg=str(get_value("Color Dark", "Background")),
            fg=str(get_value("Color Dark", "Foreground")),
            accent=str(get_value("Color Dark", "Accent")),
        ),
        light=Color(
            bg=str(get_value("Color Light", "Background")),
            fg=str(get_value("Color Light", "Foreground")),
            accent=str(get_value("Color Light", "Accent")),
        ),
        keymaps=Keymaps(
            toggle_dark=parse_keymaps(str(get_value("Keymaps", "ToggleLightDark"))),
            scroll_down=parse_keymaps(str(get_value("Keymaps", "ScrollDown"))),
            scroll_up=parse_keymaps(str(get_value("Keymaps", "ScrollUp"))),
            page_up=parse_keymaps(str(get_value("Keymaps", "PageUp"))),
            page_down=parse_keymaps(str(get_value("Keymaps", "PageDown"))),
            home=parse_keymaps(str(get_value("Keymaps", "Home"))),
            end=parse_keymaps(str(get_value("Keymaps", "End"))),
            open_toc=parse_keymaps(str(get_value("Keymaps", "OpenToc"))),
            open_metadata=parse_keymaps(str(get_value("Keymaps", "OpenMetadata"))),
            open_help=parse_keymaps(str(get_value("Keymaps", "OpenHelp"))),
            search_forward=parse_keymaps(str(get_value("Keymaps", "SearchForward"))),
            search_backward=parse_keymaps(str(get_value("Keymaps", "SearchBackward"))),
            next_match=parse_keymaps(str(get_value("Keymaps", "NextMatch"))),
            prev_match=parse_keymaps(str(get_value("Keymaps", "PreviousMatch"))),
            confirm=parse_keymaps(str(get_value("Keymaps", "Confirm"))),
            close=parse_keymaps(str(get_value("Keymaps", "CloseOrQuit"))),
            screenshot=parse_keymaps(str(get_value("Keymaps", "Screenshot"))),
        ),
    )
