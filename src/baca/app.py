import asyncio
import dataclasses
from datetime import datetime
from pathlib import Path
from typing import Type

from textual import events
from textual.actions import SkipAction
from textual.app import App, ComposeResult
from textual.css.query import NoMatches
from textual.widgets import LoadingIndicator

from .components.contents import Content
from .components.events import DoneLoading, FollowThis, OpenThisImage, Screenshot, SearchSubmitted
from .components.windows import Alert, DictDisplay, SearchInputPrompt, ToC
from .config import load_config
from .ebooks import Ebook
from .exceptions import LaunchingFileError
from .models import Coordinate, KeyMap, ReadingHistory, SearchMode
from .utils.app_resources import get_resource_file
from .utils.keys_parser import dispatch_key
from .utils.systems import launch_file
from .utils.urls import is_url


class Baca(App):
    CSS_PATH = str(get_resource_file("style.css"))

    def __init__(self, ebook_path: Path, ebook_class: Type[Ebook]):
        # load first to resolve css variables
        self.config = load_config()
        super().__init__()
        self.ebook_path = ebook_path
        self.ebook_class = ebook_class
        # TODO: make reactive and display percentage
        # as alternative for scrollbar
        self.reading_progress = 0.0
        self.search_mode = None

    def on_load(self, _: events.Load) -> None:
        assert self._loop is not None
        self._loop.run_in_executor(None, self.load_everything)

    def load_everything(self):
        self.ebook = self.ebook_class(self.ebook_path)
        content = Content(self.config, self.ebook)
        self.ebook_state, _ = ReadingHistory.get_or_create(
            filepath=str(self.ebook.get_path()), defaults=dict(reading_progress=0.0)
        )
        # NOTE: using a message instead of calling
        # the callback directly to make sure that the app is ready
        # before calling the callback, since this message will
        # get processed after app ready and composed
        # (self._screen_stack isn't empty)
        # see: Widget.on_event(), App._process_message()
        self.post_message(DoneLoading(content))

    async def on_done_loading(self, event: DoneLoading) -> None:
        # to be safe, unnecessary?
        # while self.screen is None:
        #     await asyncio.sleep(0.1)

        # NOTE: await to prevent broken layout
        await self.mount(event.content)

        def init_render() -> None:
            # restore reading progress
            # make sure to call this after refresh so the screen.max_scroll_y != 0
            self.reading_progress = self.ebook_state.reading_progress * self.screen.max_scroll_y
            self.screen.scroll_to(None, self.reading_progress, duration=0, animate=False)  # type: ignore

            self.get_widget_by_id("startup-loader", LoadingIndicator).remove()

        self.call_after_refresh(init_render)

    def on_mount(self):
        def screen_watch_scroll_y_wrapper(old_watcher, screen):
            def new_watcher(old, new):
                result = old_watcher(old, new)
                if screen.max_scroll_y != 0:
                    self.reading_progress = new / screen.max_scroll_y
                return result

            return new_watcher

        screen_scroll_y_watcher = getattr(self.screen, "watch_scroll_y")
        setattr(self.screen, "watch_scroll_y", screen_watch_scroll_y_wrapper(screen_scroll_y_watcher, self.screen))

    def get_css_variables(self):
        original = super().get_css_variables()
        return {
            **original,
            **{
                "text-max-width": self.config.max_text_width,
                "text-justification": self.config.text_justification,
                "dark-bg": self.config.dark.bg,
                "dark-fg": self.config.dark.fg,
                "dark-accent": self.config.dark.accent,
                "light-bg": self.config.light.bg,
                "light-fg": self.config.light.fg,
                "light-accent": self.config.light.accent,
            },
        }

    async def on_key(self, event: events.Key) -> None:
        keymaps = self.config.keymaps
        await dispatch_key(
            [
                KeyMap(keymaps.close, self.action_cancel_search_or_quit),
                KeyMap(keymaps.scroll_down, self.screen.action_scroll_down),
                KeyMap(keymaps.scroll_up, self.screen.action_scroll_up),
                # KeyMap(keymaps.page_up, self.screen.action_page_up),
                # KeyMap(keymaps.page_down, self.screen.action_page_down),
                KeyMap(keymaps.page_up, self.action_page_up),
                KeyMap(keymaps.page_down, self.action_page_down),
                KeyMap(keymaps.home, self.screen.action_scroll_home),
                KeyMap(keymaps.end, self.screen.action_scroll_end),
                KeyMap(keymaps.open_toc, self.action_open_toc),
                KeyMap(keymaps.open_metadata, self.action_open_metadata),
                KeyMap(keymaps.open_help, self.action_open_help),
                KeyMap(keymaps.toggle_dark, self.action_toggle_dark),
                KeyMap(keymaps.screenshot, lambda: self.post_message(Screenshot())),
                KeyMap(keymaps.search_forward, lambda: self.action_input_search(forward=True)),
                KeyMap(keymaps.search_backward, lambda: self.action_input_search(forward=False)),
                KeyMap(keymaps.next_match, self.action_search_next),
                KeyMap(keymaps.prev_match, self.action_search_prev),
                KeyMap(keymaps.confirm, self.action_stop_search),
                # KeyMap(["D"], lambda: self.log()),
            ],
            event,
        )

    def compose(self) -> ComposeResult:
        yield LoadingIndicator(id="startup-loader")

    async def alert(self, message: str) -> None:
        alert = Alert(self.config, message)
        await self.mount(alert)

    async def action_open_metadata(self) -> None:
        if self.metadata_window is None:
            metadata_window = DictDisplay(
                config=self.config, id="metadata", title="Metadata", data=dataclasses.asdict(self.ebook.get_meta())
            )
            await self.mount(metadata_window)

    def action_page_down(self) -> None:
        if not self.screen.allow_vertical_scroll:
            raise SkipAction()
        self.screen.scroll_page_down(duration=self.config.page_scroll_duration)

    def action_page_up(self) -> None:
        if not self.screen.allow_vertical_scroll:
            raise SkipAction()
        self.screen.scroll_page_up(duration=self.config.page_scroll_duration)

    async def action_input_search(self, forward: bool) -> None:
        await self.mount(SearchInputPrompt(forward=forward))

    async def action_search_next(self) -> bool:
        if self.search_mode is not None:
            new_coord = await self.content.search_next(
                self.search_mode.pattern_str,
                self.search_mode.current_coord,
                self.search_mode.forward,
            )
            if new_coord is not None:
                self.search_mode = dataclasses.replace(self.search_mode, current_coord=new_coord)
                return True
            else:
                # TODO: inconsistent alert window size on initial search
                await self.alert(f"Found no match: '{self.search_mode.pattern_str}'")

        return False

    async def action_search_prev(self) -> None:
        if self.search_mode is not None:
            new_coord = await self.content.search_next(
                self.search_mode.pattern_str,
                self.search_mode.current_coord,
                not self.search_mode.forward,
            )
            if new_coord is not None:
                self.search_mode = dataclasses.replace(self.search_mode, current_coord=new_coord)

    async def action_stop_search(self) -> None:
        if self.search_mode is not None:
            self.search_mode = None
            await self.content.clear_search()

    async def action_open_help(self) -> None:
        if self.help_window is None:
            keymap_data = {
                k.replace("_", " ").title(): ",".join(v) for k, v in dataclasses.asdict(self.config.keymaps).items()
            }
            help_window = DictDisplay(config=self.config, id="help", title="Keymaps", data=keymap_data)
            await self.mount(help_window)

    async def action_open_toc(self) -> None:
        if self.toc_window is None:
            toc_entries = list(self.ebook.get_toc())
            if len(toc_entries) == 0:
                return await self.alert("No content navigations for this ebook.")

            initial_index = 0
            toc_values = [e.value for e in toc_entries]
            for s in self.content.get_navigables():
                if s.nav_point is not None and s.nav_point in toc_values:
                    # if round(self.screen.scroll_y) >= s.virtual_region.y:
                    if self.screen.scroll_offset.y >= s.virtual_region.y:
                        initial_index = toc_values.index(s.nav_point)
                    else:
                        break

            toc = ToC(self.config, entries=toc_entries, initial_index=initial_index)
            # NOTE: await to prevent broken layout
            await self.mount(toc)

    async def action_cancel_search_or_quit(self) -> None:
        if self.search_mode is not None:
            self.screen.scroll_to(
                0, self.search_mode.saved_position * self.screen.max_scroll_y, duration=self.config.page_scroll_duration
            )
            await self.action_stop_search()
        else:
            await self.action_quit()

    async def action_link(self, link: str) -> None:
        if is_url(link):
            try:
                await launch_file(link)
            except LaunchingFileError as e:
                await self.alert(str(e))

        elif link in [n.nav_point for n in self.content.get_navigables()]:
            self.content.scroll_to_section(link)

        else:
            await self.alert(f"No nav point found in document: {link}")

    async def on_search_submitted(self, message: SearchSubmitted) -> None:
        self.search_mode = SearchMode(
            pattern_str=message.value,
            current_coord=Coordinate(-1 if message.forward else self.content.size.width, self.screen.scroll_offset.y),
            forward=message.forward,
            saved_position=self.reading_progress,
        )
        is_found = await self.action_search_next()
        if not is_found:
            self.search_mode = None

    async def on_follow_this(self, message: FollowThis) -> None:
        self.content.scroll_to_section(message.nav_point)
        # NOTE: remove after refresh so the event get handled
        self.call_after_refresh(self.toc_window.remove)  # type: ignore

    async def on_open_this_image(self, message: OpenThisImage) -> None:
        try:
            filename, bytestr = self.ebook.get_img_bytestr(message.value)
            tmpfilepath = self.ebook.get_tempdir() / filename
            with open(tmpfilepath, "wb") as img_tmp:
                img_tmp.write(bytestr)

            await launch_file(tmpfilepath, preferred=self.config.preferred_image_viewer)
        except LaunchingFileError as e:
            await self.alert(f"Error opening an image: {e}")

    async def on_screenshot(self, _: Screenshot) -> None:
        self.save_screenshot(f"baca_{datetime.now().isoformat()}.svg")

    def run(self, *args, **kwargs):
        try:
            return super().run(*args, **kwargs)
        finally:
            meta = self.ebook.get_meta()
            self.ebook_state.last_read = datetime.now()  # type: ignore
            self.ebook_state.title = meta.title  # type: ignore
            self.ebook_state.author = meta.creator  # type: ignore
            self.ebook_state.reading_progress = self.reading_progress  # type: ignore
            self.ebook_state.save()
            self.ebook.cleanup()

    @property
    def toc_window(self) -> ToC | None:
        try:
            return self.query_one(ToC.__name__, ToC)
        except NoMatches:
            return None

    @property
    def metadata_window(self) -> DictDisplay | None:
        try:
            return self.get_widget_by_id("metadata", DictDisplay)
        except NoMatches:
            return None

    @property
    def help_window(self) -> DictDisplay | None:
        try:
            return self.get_widget_by_id("help", DictDisplay)
        except NoMatches:
            return None

    @property
    def content(self) -> Content:
        return self.query_one(Content.__name__, Content)

    # def _remove_nodes(self, widgets: list[Widget], parent: DOMNode) -> AwaitRemove:
    #     await_remove = super()._remove_nodes(widgets, parent)
    #     self.refresh(layout=True)
    #     return await_remove
    # def on_mount(self) -> None:
    #     self.screen.can_focus = True
