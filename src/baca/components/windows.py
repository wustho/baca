from typing import Type

from textual import events
from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Input, Static

from ..models import Config, KeyMap, TocEntry
from ..utils.keys_parser import dispatch_key
from .contents import Table
from .events import FollowThis, Screenshot, SearchSubmitted


class SearchInputPrompt(Input):
    can_focus = True

    def __init__(self, forward: bool):
        super().__init__()
        self.forward = forward
        self.border_title = f"Search {'Forward' if forward else 'Backward'}"

    def on_mount(self):
        self.focus()

    async def on_key(self, event: events.Key) -> None:
        keymaps = [
            KeyMap(["backspace", "ctrl+h"], self.action_delete_left),
            KeyMap(["home", "ctrl+a"], self.action_home),
            KeyMap(["end", "ctrl+e"], self.action_end),
            KeyMap(["left"], self.action_cursor_left),
            KeyMap(["right"], self.action_cursor_right),
            KeyMap(["ctrl+w"], self.action_delete_left_word),
            KeyMap(["delete"], self.action_delete_right),
            KeyMap(["enter"], self.action_submit),
            KeyMap(["escape"], self.action_close),
        ]

        if event.key not in set(k for keymap in keymaps for k in keymap.keys):
            await super().on_key(event)
            event.stop()
            event.prevent_default()
        else:
            await dispatch_key(keymaps, event)

    def action_submit(self) -> None:
        self.post_message(SearchSubmitted(value=self.value, forward=self.forward))
        self.action_close()

    def action_close(self) -> None:
        self.call_after_refresh(self.remove)


class Window(Widget):
    can_focus = True

    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        keymaps = self.config.keymaps
        self.keymaps = [
            KeyMap(keymaps.close, self.action_close),
            KeyMap(keymaps.scroll_down, self.action_scroll_down),
            KeyMap(keymaps.scroll_up, self.action_scroll_up),
            KeyMap(keymaps.page_down, self.action_page_down),
            KeyMap(keymaps.page_up, self.action_page_up),
            KeyMap(keymaps.screenshot, lambda: self.post_message(Screenshot())),
        ]

    async def on_key(self, event: events.Key) -> None:
        await dispatch_key(self.keymaps, event)

    def on_mount(self) -> None:
        # NOTE: somehow this method is automatically inherited
        # even if the child class overriding this without super().on_moun()
        self.focus(False)

        # NOTE: set here instead of in CSS file
        # so it will be responsive to screen size
        screen_size = self.screen.size
        self.styles.margin = (screen_size.height // 10, screen_size.width // 10)

    def action_close(self) -> None:
        self.call_after_refresh(self.remove)


class Alert(Window):
    border_title = "❗"

    def __init__(self, config: Config, message: str):
        super().__init__(config)
        self.message = message

    def compose(self) -> ComposeResult:
        yield Static(self.message)

    # NOTE: self.render() is low level API
    # so, this won't be any auto scroll-overflow
    # use self.compose() instead
    # def render(self):


class DictDisplay(Window):
    def __init__(self, config: Config, id: str, title: str, data: dict):
        super().__init__(config)
        self.data = data
        self.border_title = title

    def compose(self) -> ComposeResult:
        yield Table(headers=["key", "value"], rows=[(k, v) for k, v in self.data.items()])


class NavPoint(Widget):
    can_focus = True

    def __init__(self, config: Config, label: str, value: str):
        super().__init__()
        self.config = config
        self.value = value
        self.label = label

    async def on_key(self, event: events.Key) -> None:
        await dispatch_key([KeyMap(self.config.keymaps.confirm, self.action_follow_this)], event, propagate=False)

    async def on_mouse_move(self, event: events.MouseMove) -> None:
        self.focus()

    def action_follow_this(self) -> None:
        self.post_message(FollowThis(self.value))

    def render(self):
        return self.label

    async def on_click(self) -> None:
        # self.post_message(events.DescendantFocus())
        # return await super()._on_click(event)
        self.action_follow_this()


class ToC(Window):
    border_title = "Table of Contents"

    def __init__(self, config: Config, entries: list[TocEntry], initial_focused_id: str | None = None):
        super().__init__(config)
        self.entries = entries
        self.initial_focused_id = initial_focused_id
        self.entry_widgets = [NavPoint(self.config, entry.label, entry.value) for entry in self.entries]
        keymaps = config.keymaps
        self.keymaps = [
            KeyMap(keymaps.close + config.keymaps.open_toc, self.action_close),
            KeyMap(keymaps.scroll_down, lambda: self.action_shift_focus(1)),
            KeyMap(keymaps.scroll_up, lambda: self.action_shift_focus(-1)),
            KeyMap(keymaps.home, lambda: self.entry_widgets[0].focus()),
            KeyMap(keymaps.end, lambda: self.entry_widgets[-1].focus()),
            KeyMap(keymaps.screenshot, lambda: self.post_message(Screenshot())),
        ]

    def on_focus(self) -> None:
        # always make the focus to the entries
        # and let the entries pass the key event to this window
        if len(self.entries):
            if self.initial_focused_id is None:
                self.entry_widgets[0].focus()
            else:
                for w in self.entry_widgets:
                    if w.value == self.initial_focused_id:
                        w.focus()
                        w.scroll_visible(top=True)
                        break

    def action_shift_focus(self, n: int) -> None:
        try:
            current_focused_idx = next(n for n, e in enumerate(self.entry_widgets) if e.has_focus)
            next_focused_idx = (current_focused_idx + n) % len(self.entry_widgets)
        except StopIteration:
            next_focused_idx = 0 if n >= 0 else -1
        self.entry_widgets[next_focused_idx].focus()

    def compose(self) -> ComposeResult:
        yield from self.entry_widgets
