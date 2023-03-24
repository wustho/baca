from dataclasses import dataclass
from configparser import ConfigParser
from typing import Literal, cast


DEFAULT = """\
[General]
MaxTextWidth = 80
# 'full', 'center', 'left', 'right'
TextJustification = full
# Currently using pretty is slow
# and text alignment only works for 'left' aligned
Pretty = no

[Color Dark]
Background = #000000
Foreground = #ffffff
Accent = #00ff00

[Color Light]
Background = #ffffff
Foreground = #000000
Accent = #00ff00

[Keybindings]
ToggleLightDark = c
ScrollDown = down,j
ScrollUp = up,k
PageDown = ctrl+f,pagedown
PageUp = ctrl+b,pageup
OpenToc = tab
OpenMetadata = M
OpenHelp = question_mark
CloseOrQuit = q,escape
Screenshot = f12
"""


@dataclass
class Color:
    bg: str
    fg: str
    accent: str


@dataclass
class Keybindings:
    toggle_dark: list[str]
    scroll_down: list[str]
    scroll_up: list[str]
    page_up: list[str]
    page_down: list[str]
    open_toc: list[str]
    open_metadata: list[str]
    open_help: list[str]
    close: list[str]
    screenshot: list[str]


@dataclass
class Config:
    max_text_width: int
    text_justification: Literal["default", "center", "full", "right", "left"]
    pretty: bool
    dark: Color
    light: Color
    keybindings: Keybindings


def load_config_str(config_str: str = DEFAULT) -> Config:
    parser = ConfigParser()
    parser.read_string(config_str)

    return Config(
        max_text_width=int(parser["General"]["MaxTextWidth"]),
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
        keybindings=Keybindings(
            toggle_dark=parser["Keybindings"]["ToggleLightDark"].split(","),
            scroll_down=parser["Keybindings"]["ScrollDown"].split(","),
            scroll_up=parser["Keybindings"]["ScrollUp"].split(","),
            page_up=parser["Keybindings"]["PageUp"].split(","),
            page_down=parser["Keybindings"]["PageDown"].split(","),
            open_toc=parser["Keybindings"]["OpenToc"].split(","),
            open_metadata=parser["Keybindings"]["OpenMetadata"].split(","),
            open_help=parser["Keybindings"]["OpenHelp"].split(","),
            close=parser["Keybindings"]["CloseOrQuit"].split(","),
            screenshot=parser["Keybindings"]["Screenshot"].split(","),
        ),
    )


config = load_config_str()
