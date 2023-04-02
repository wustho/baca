from textual import events
from textual.app import ComposeResult
from textual.message import Message
from textual.reactive import reactive
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

    def __init__(self, config: Config, id: str | None = None):
        super().__init__(**(dict() if id is None else dict(id=id)))
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
        super().__init__(config, id)
        self.data = data
        self.border_title = title

    def compose(self) -> ComposeResult:
        yield Table(headers=["key", "value"], rows=[(k, v) for k, v in self.data.items()])


class NavPoint(Widget):
    can_focus = False

    class Selected(Message):
        def __init__(self, index: int) -> None:
            super().__init__()
            self.index = index

    class Clicked(Selected):
        pass

    def __init__(self, index: int, label: str):
        super().__init__()
        self.index = index
        self.label = label

    def render(self):
        return self.label

    async def on_mouse_move(self, _: events.MouseMove) -> None:
        self.post_message(self.Selected(self.index))

    async def on_click(self) -> None:
        self.post_message(self.Selected(self.index))
        self.post_message(self.Clicked(self.index))


class ToC(Window):
    border_title = "Table of Contents"
    index = reactive(0)

    def __init__(self, config: Config, entries: list[TocEntry], initial_index: int = 0):
        super().__init__(config)
        self.entries = entries
        self.entry_widgets = [NavPoint(n, entry.label) for n, entry in enumerate(self.entries)]
        keymaps = config.keymaps
        self.keymaps = [
            KeyMap(keymaps.close + config.keymaps.open_toc, self.action_close),
            KeyMap(keymaps.scroll_down, lambda: self.action_select_next(1)),
            KeyMap(keymaps.scroll_up, lambda: self.action_select_next(-1)),
            KeyMap(keymaps.home, lambda: self.entry_widgets[0].focus()),
            KeyMap(keymaps.end, lambda: self.entry_widgets[-1].focus()),
            KeyMap(keymaps.confirm, self.follow_nav_point),
            KeyMap(keymaps.screenshot, lambda: self.post_message(Screenshot())),
        ]
        self.index = initial_index

    def on_focus(self) -> None:
        # NOTE: by default when a widget gaining focus, in this case ToC
        # it will reset the scrolling position of this widget which will hide selected NavPoint
        # So, either assign new value for selected navpoint or run watch_selected_value()
        self.watch_index(self.index, self.index)

    def action_select_next(self, n: int) -> None:
        self.index = (self.index + n) % len(self.entries)

    def compose(self) -> ComposeResult:
        yield from self.entry_widgets

    def watch_index(self, old: int, new: int) -> None:
        [entry_widget.remove_class("selected") for entry_widget in self.entry_widgets]
        selected = self.entry_widgets[new]
        selected.add_class("selected")
        self.scroll_to_widget(selected, top=False)

    def on_nav_point_selected(self, message: NavPoint.Selected) -> None:
        self.index = message.index
        message.stop()

    def on_nav_point_clicked(self, message: NavPoint.Clicked) -> None:
        self.follow_nav_point()
        message.stop()

    def follow_nav_point(self) -> None:
        self.post_message(FollowThis(self.entries[self.index].value))
