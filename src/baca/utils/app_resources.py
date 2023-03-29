from importlib.resources import as_file, files
from pathlib import Path


def get_resource_file(filename: str) -> Path:
    with as_file(files("baca.resources").joinpath(filename)) as resource_file:
        return resource_file
