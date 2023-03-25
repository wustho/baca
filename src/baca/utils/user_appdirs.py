import os
import shutil
from importlib import resources
from pathlib import Path

import appdirs

from .. import __appname__

DEFAULT_CONFIG = resources.path("baca.resources", "config.ini")


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
        shutil.copyfile(str(DEFAULT_CONFIG), str(configfile))

    return configfile
