import os
from pathlib import Path

import appdirs

from .. import __appname__
from .app_resources import get_resource_file

DEFAULT_CONFIG = get_resource_file("config.ini")


def retrieve_user_cache_dbfile() -> Path:
    cachedir = appdirs.user_cache_dir(__appname__)
    if not os.path.isdir(cachedir):
        os.makedirs(cachedir)

    return Path(cachedir) / f"{__appname__}.db"


def retrieve_user_config_file() -> Path:
    configdir = Path(appdirs.user_config_dir(appname=__appname__))
    if not os.path.isdir(configdir):
        os.makedirs(configdir)

    configfile = configdir / "config.ini"
    if not os.path.isfile(configfile):
        # shutil.copyfile(str(DEFAULT_CONFIG), str(configfile))
        with open(DEFAULT_CONFIG, "r", encoding="utf-8") as src, open(configfile, "w", encoding="utf-8") as dest:
            dest.write(src.read())

    return configfile
