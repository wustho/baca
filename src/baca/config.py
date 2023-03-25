import os
import shutil
from configparser import ConfigParser
from typing import Literal, cast

import appdirs
from pkg_resources import resource_filename

from . import __appname__ as appname
from .models import Color, Config, Keymaps

DEFAULT_CONFIG = resource_filename(__name__, "resources/config.ini")


def load_config(config_path: str) -> Config:
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
    configdir = appdirs.user_config_dir(appname=appname)
    if not os.path.isdir(configdir):
        os.makedirs(configdir)

    configfile = os.path.join(configdir, "config.ini")
    if not os.path.isfile(configfile):
        shutil.copyfile(DEFAULT_CONFIG, configfile)

    return load_config(configfile)
