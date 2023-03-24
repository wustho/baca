from dataclasses import asdict
import inspect

from rich.text import Text
from textual import events
from textual.actions import SkipAction
from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import DataTable, Static

from ..models import Layers, TocEntry, BookMetadata
from .events import FollowThis
from .contents import Table


# TODO: Widget seems weird when being inherited
async def _window_on_key(obj: Widget, event: events.Key) -> None:
    callback = {
        **{k: obj.action_close for k in ["q", "escape"]},
        **{k: obj.action_scroll_down for k in ["j", "down"]},
        **{k: obj.action_scroll_up for k in ["k", "up"]},
        "ctrl+f": obj.action_page_down,
        "ctrl+b": obj.action_page_up,
    }.get(event.key)

    if callback is not None:
        try:
            return_value = callback()
            if inspect.isawaitable(return_value):
                await return_value
        except SkipAction:
            pass

    event.stop()
    event.prevent_default()


def _window_on_mount(obj: Widget) -> None:
    obj.focus()
    # self.styles.background = "blue"
    obj.styles.dock = "top"
    obj.styles.border = ("double", obj.styles.scrollbar_color)
    obj.styles.layer = Layers.WINDOWS.value
    obj.styles.margin = (int(0.1 * obj.screen.size.height), int(0.1 * obj.screen.size.width))
    # obj.styles.width = "90%"
    # obj.styles.height = "90%"
    obj.styles.padding = (1, 4)
    obj.styles.scrollbar_size_vertical = 1
    obj.styles.overflow_y = "auto"
    obj.styles.border_title_align = "center"


class Window(Widget):
    pass


class Alert(Window):
    border_title = "❗"
    can_focus = True

    def __init__(self, message: str):
        super().__init__()
        self.message = message

    def on_mount(self) -> None:
        _window_on_mount(self)
        self.styles.padding = 5
        # self.styles.align = ("center", "middle")
        self.styles.border = ("solid", "darkred")
        self.styles.color = "darkred"
        self.styles.border_title_align = "center"

    async def on_key(self, event: events.Key) -> None:
        await _window_on_key(self, event)

    def render(self):
        return Text(self.message, justify="center", style="bold")


class Metadata(Window):
    border_title = "Metadata"
    can_focus = True

    def __init__(self, metadata: BookMetadata):
        super().__init__()
        self.metadata = metadata

    def action_close(self) -> None:
        self.remove()

    def on_mount(self) -> None:
        _window_on_mount(self)
        # self.styles.padding = 5
        self.styles.border_title_align = "center"
        self.styles.align = ("center", "top")

    async def on_key(self, event: events.Key) -> None:
        await _window_on_key(self, event)

    def compose(self) -> ComposeResult:
        yield Table(headers=["key", "value"], rows=[(k, v) for k, v in asdict(self.metadata).items()])


class FollowButton(Widget):
    DEFAULT_CSS = """
    FollowButton:focus {
        background: red;
    }
    """
    can_focus = True

    def __init__(self, label: str, value: str | int):
        super().__init__()
        self.value = value
        self.label = label

    async def on_key(self, event: events.Key) -> None:
        callback = {"enter": self.action_follow_this}.get(event.key)

        if callback is not None:
            return_value = callback()
            if inspect.isawaitable(return_value):
                await return_value

    async def on_mouse_move(self, _: events.MouseMove) -> None:
        self.focus()

    def action_follow_this(self) -> None:
        self.post_message(FollowThis(self.value))

    def on_mount(self) -> None:
        self.styles.height = "auto"
        self.styles.border = ("tall", "grey")
        self.styles.margin = (0, 1, 1, 0)
        self.styles.padding = (0, 1)

    def render(self):
        return self.label

    async def on_click(self) -> None:
        # self.post_message(events.DescendantFocus())
        # return await super()._on_click(event)
        self.action_follow_this()


class ToC(Window):
    border_title = "Table of Contents"

    def __init__(self, entries: list[TocEntry], initial_focused_id: str | None = None):
        super().__init__()
        self.entries = entries
        self.initial_focused_id = initial_focused_id
        self.entry_widgets = [FollowButton(entry.label, entry.value) for entry in self.entries]

    def on_mount(self) -> None:
        _window_on_mount(self)

    async def on_key(self, event: events.Key) -> None:
        callback = {
            # NOTE: somehow cannot be bound to self.remove for closing
            # it will freeze the app
            **{k: self.action_close for k in ["q", "escape", "tab"]},
            **{k: self.action_focus_next_child for k in ["j", "down"]},
            **{k: self.action_focus_prev_child for k in ["k", "up"]},
        }.get(event.key)

        if callback is not None:
            return_value = callback()
            if inspect.isawaitable(return_value):
                await return_value

        event.stop()
        event.prevent_default()  # stopping the event from being handled by base class

    def render(self):
        if len(self.entries):
            if self.initial_focused_id is None:
                self.entry_widgets[0].focus()
            else:
                for w in self.entry_widgets:
                    if w.value == self.initial_focused_id:
                        w.focus()
                        w.scroll_visible(top=True)
                        break

        return super().render()

    # TODO: simplify
    def action_focus_next_child(self) -> None:
        try:
            next(w for w in self.entry_widgets if w.has_focus)
        except StopIteration:
            self.entry_widgets[0].focus()
            return

        for idx, widget in enumerate(self.entry_widgets):
            if self.entry_widgets[idx - 1].has_focus:
                widget.focus()

    # TODO: simplify
    def action_focus_prev_child(self) -> None:
        try:
            next(w for w in self.entry_widgets if w.has_focus)
        except StopIteration:
            self.entry_widgets[-1].focus()
            return

        children = list(reversed(self.entry_widgets))
        for idx, widget in enumerate(children):
            if children[idx - 1].has_focus:
                widget.focus()

    def compose(self) -> ComposeResult:
        yield from self.entry_widgets

    def action_close(self) -> None:
        self.remove()
