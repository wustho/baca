import asyncio
import os
import platform
import shutil
from pathlib import Path

from ..exceptions import LaunchingFileError

LAUNCHERS = [
    "gnome-open",
    "gvfs-open",
    "xdg-open",
    "kde-open",
]


async def launch_file(path: Path | str, preferred: str = LAUNCHERS[0]) -> None:
    if platform.system() == "Windows":
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, os.startfile, path)  # type: ignore
        return

    if platform.system() == "Darwin":
        launcher = "open"
    else:
        try:
            launcher = next(l for l in [preferred, *LAUNCHERS] if shutil.which(l) is not None)
        except StopIteration:
            raise LaunchingFileError("System launcher not found.")

    proc = await asyncio.create_subprocess_exec(launcher, path, stderr=asyncio.subprocess.PIPE)
    await proc.wait()
    if proc.returncode != 0:
        _, stderr = await proc.communicate()
        raise LaunchingFileError(stderr.decode())
