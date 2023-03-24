import os
import asyncio
import subprocess
from datetime import datetime
import inspect

from rich.text import Text
from rich.console import RenderableType
from textual import events
from textual.app import App, ComposeResult
from textual.await_remove import AwaitRemove
from textual.color import Color
from textual.css.query import NoMatches
from textual.dom import DOMNode
from textual.widget import Widget
from textual.widgets import LoadingIndicator

from .components.contents import Content
from .components.events import DoneLoading, FollowThis, OpenThisImage
from .components.windows import Alert, ToC
from .ebooks import Ebook
from .models import Layers


class Baca(App):
    def __init__(self, ebook: Ebook):
        super().__init__()
        # move initializing ebook to self.load_everything()
        self.ebook = ebook
        self.loader = LoadingIndicator()

    def debug(self) -> None:
        # self.log("=======", self.screen.scroll_y, self.screen.scroll_target_y)
        # results = list(self.query("Section").results())
        # self.log("=======", results[8].virtual_region)
        self.log("-------", self.focused)

    async def alert(self, message: str) -> None:
        alert = Alert(message)
        await self.mount(alert)
        alert.focus(False)

    async def on_key(self, event: events.Key) -> None:
        callback = {
            **{k: self.action_quit for k in ["q", "escape"]},
            **{k: self.screen.action_scroll_down for k in ["j", "down"]},
            **{k: self.screen.action_scroll_up for k in ["k", "up"]},
            "c": self.action_toggle_dark,
            "tab": self.action_open_toc,
            "ctrl+f": self.screen.action_page_down,
            "ctrl+b": self.screen.action_page_up,
            "f11": lambda: self.save_screenshot(f"baca_{datetime.now().isoformat()}.svg"),
            "l": self.debug,
        }.get(event.key)

        if callback is not None:
            return_value = callback()
            if inspect.isawaitable(return_value):
                await return_value

    def on_mount(self) -> None:
        # self.styles.background = "transparent"
        # self.screen.styles.background = "transparent"
        self.screen.styles.align = ("center", "middle")
        self.screen.styles.scrollbar_size_vertical = 1
        self.screen.styles.layers = (layer.value for layer in Layers)
        self.screen.can_focus = True
        # setattr(self.screen, "on_resize", self.action_open_toc)

    def compose(self) -> ComposeResult:
        yield self.loader

    def on_load(self, _: events.Load) -> None:
        assert self._loop is not None
        self._loop.run_in_executor(None, self.load_everything)

    def load_everything(self):
        content = Content(self.ebook)
        self.post_message(DoneLoading(content))

    async def on_done_loading(self, event: DoneLoading) -> None:
        # NOTE: awaiting is necessary to prevent broken layout
        await self.mount(event.content)
        self.loader.remove()
        # TODO: temp workaround
        self.screen.focus()
        # self.call_after_refresh(self.query_one("#startup-loader").remove())

    async def action_open_toc(self) -> None:
        if self.toc is None:
            toc_entries = list(self.ebook.get_toc())
            if len(toc_entries) == 0:
                return await self.alert("No content navigations for this ebook.")

            initial_focused_id: str | None = None
            for s in self.content.sections:  # type: ignore
                if self.screen.scroll_y >= s.virtual_region.y:
                    initial_focused_id = s.id
                # TODO: check why breaking here not working
                # else:
                #     break

            toc = ToC(entries=toc_entries, initial_focused_id=initial_focused_id)
            # NOTE: awaiting is necessary to prevent broken layout
            await self.mount(toc)
            toc.focus(False)

    async def on_follow_this(self, message: FollowThis) -> None:
        # TODO: add attr TocEntry.uuid so query("#{uuid}")
        for s in self.content.sections:  # type: ignore
            if s.id == message.value:
                s.scroll_visible(top=True)
                break

        # NOTE: remove after refresh so the event get handled
        self.call_after_refresh(self.toc.remove)  # type: ignore

    async def on_open_this_image(self, message: OpenThisImage) -> None:
        filename, bytestr = self.ebook.get_img_bytestr(message.value)
        tmpfilepath = os.path.join(self.ebook.get_tempdir(), filename)
        with open(tmpfilepath, "wb") as img_tmp:
            img_tmp.write(bytestr)

        try:
            subprocess.check_output(["xdg-open", tmpfilepath], stderr=subprocess.PIPE)
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            error_msg = e.stderr.decode() if isinstance(e, subprocess.CalledProcessError) else str(e)
            await self.alert(f"Error opening an image: {error_msg}")

    def _remove_nodes(self, widgets: list[Widget], parent: DOMNode) -> AwaitRemove:
        await_remove = super()._remove_nodes(widgets, parent)
        self.refresh(layout=True)
        return await_remove

    def run(self, *args, **kwargs):
        try:
            return super().run(*args, **kwargs)
        finally:
            self.ebook.cleanup()

    @property
    def toc(self) -> ToC | None:
        try:
            return self.query_one(ToC.__name__, ToC)
        except NoMatches:
            return None

    @property
    def content(self) -> Content | None:
        return self.query_one(Content.__name__, Content)
