import inspect

from textual import events
from textual.actions import SkipAction

from ..models import KeyMap


async def dispatch_key(maps: list[KeyMap], event: events.Key, *, propagate: bool = True) -> None:
    callback = {k: m.action for m in maps for k in m.keys}.get(event.key)

    if callback is not None:
        try:
            return_value = callback()
            if inspect.isawaitable(return_value):
                await return_value
        except SkipAction:
            pass

    if propagate:
        # stop propagating to base widget
        event.prevent_default()
        # stop propagating to parent widget
        event.stop()
