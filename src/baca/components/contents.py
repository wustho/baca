import re
from marshal import dumps
from urllib.parse import urljoin

from rich.markdown import Markdown
from rich.text import Text
from textual import events
from textual.app import ComposeResult
from textual.geometry import Region
from textual.strip import Strip
from textual.widget import Widget
from textual.widgets import DataTable
from textual.widgets.markdown import Markdown as PrettyMarkdown

from ..ebooks import Ebook
from ..models import Config, Coordinate, SegmentType
from ..utils.urls import is_url
from .events import OpenThisImage


class Table(DataTable):
    can_focus = False

    def __init__(self, headers: list[str], rows: list[tuple]):
        super().__init__(show_header=True, zebra_stripes=True, show_cursor=False)
        self.add_columns(*headers)
        self.add_rows(rows)

    def on_mount(self) -> None:
        self.zebra_stripes = True
        self.show_cursor = False


class SegmentWidget(Widget):
    can_focus = False

    def __init__(self, config: Config, nav_point: str | None):
        super().__init__()
        self.config = config
        self.nav_point = nav_point

    def get_text_at(self, y: int) -> str:
        return self.render_lines(Region(0, y, self.virtual_region_with_margin.width, 1))[0].text


class Body(SegmentWidget):
    def __init__(self, config: Config, content: str, nav_point: str | None = None):
        super().__init__(config, nav_point)
        self.content = content

    def render(self):
        # NOTE: Markdwon rich isn't widget, so we cannot set using css
        # hence this translation workaround
        return Markdown(
            self.content, justify=dict(center="center", left="left", right="right", justify="full")[self.styles.text_align]  # type: ignore
        )

    def render_line(self, y) -> Strip:
        strip = super().render_line(y)
        for s in strip._segments:
            if s.style is not None and s.style.link is not None:
                link = (
                    s.style.link
                    if is_url(s.style.link) or self.nav_point is None
                    else urljoin(self.nav_point, s.style.link)
                )
                s.style._meta = dumps({"@click": f"link({link!r})"})
        return strip


class Image(SegmentWidget):
    def __init__(self, config: Config, src: str, nav_point: str | None = None):
        super().__init__(config, nav_point)
        # TODO: maybe put it in Widget.id?
        self.content = src

    def render(self):
        return Text("IMAGE", justify="center")

    # TODO: "Click ot Open" on mouse hover
    # def on_mouse_move(self, _: events.MouseMove) -> None:
    #     self.styles.background = "red"

    async def on_click(self) -> None:
        self.post_message(OpenThisImage(self.content))


class PrettyBody(PrettyMarkdown):
    def __init__(self, config: Config, value: str, nav_point: str | None = None):
        super().__init__(value)
        self.nav_point = nav_point

    def get_text_at(self, y: int) -> str | None:
        # TODO: this implementation still has issue in positioning match
        # at the end of ebook segment
        accumulated_height = 0
        for child in self.children:
            if accumulated_height + child.virtual_region_with_margin.height > y:
                return child.render_lines(Region(0, y - accumulated_height, child.virtual_region_with_margin.width, 1))[
                    0
                ].text
            accumulated_height += child.virtual_region_with_margin.height


class SearchMatch(Widget):
    can_focus = False

    def __init__(self, match_str: str, coordinate: Coordinate):
        super().__init__()
        self.match_str = match_str
        self.coordinate = coordinate

    def on_mount(self):
        self.styles.offset = (self.coordinate.x, self.coordinate.y)

    def render(self):
        return self.match_str

    def scroll_visible(self):
        # NOTE: need to override default .scroll_visible().
        # Somehow this widget.virtual_region_with_margin
        # will cause the screen to scroll to 0.
        self.screen.scroll_to_region(
            Region(
                x=self.coordinate.x,
                y=self.coordinate.y,
                width=self.virtual_size.width,
                height=self.virtual_size.height,
            )
        )


class Content(Widget):
    can_focus = False

    def __init__(self, config: Config, ebook: Ebook):
        super().__init__()
        self.config = config

        self._segments: list[SegmentWidget | PrettyBody] = []
        for segment in ebook.iter_parsed_contents():
            if segment.type == SegmentType.BODY:
                component_cls = Body if not config.pretty else PrettyBody
            else:
                component_cls = Image
            self._segments.append(component_cls(self.config, segment.content, segment.nav_point))

    def get_navigables(self):
        return [s for s in self._segments if s.nav_point is not None]

    def scroll_to_section(self, nav_point: str) -> None:
        # TODO: add attr TocEntry.uuid so we can query("#{uuid}")
        for s in self.get_navigables():
            if s.nav_point == nav_point:
                s.scroll_visible(top=True)
                break

    def on_mouse_scroll_down(self, _: events.MouseScrollDown) -> None:
        self.screen.scroll_down()

    def on_mouse_scroll_up(self, _: events.MouseScrollUp) -> None:
        self.screen.scroll_up()

    # NOTE: override initial message
    def render(self):
        return ""

    def compose(self) -> ComposeResult:
        yield from iter(self._segments)

    def get_text_at(self, y: int) -> str | None:
        accumulated_height = 0
        for segment in self._segments:
            if accumulated_height + segment.virtual_region_with_margin.height > y:
                return segment.get_text_at(y - accumulated_height)
            accumulated_height += segment.virtual_region_with_margin.height

    async def search_next(
        self, pattern_str: str, current_coord: Coordinate = Coordinate(-1, 0), forward: bool = True
    ) -> Coordinate | None:
        pattern = re.compile(pattern_str, re.IGNORECASE)
        current_x = current_coord.x
        line_range = (
            range(current_coord.y, self.virtual_size.height) if forward else reversed(range(0, current_coord.y + 1))
        )
        for linenr in line_range:
            line_text = self.get_text_at(linenr)
            if line_text is not None:
                for match in pattern.finditer(line_text):
                    is_next_match = (match.start() > current_x) if forward else (match.start() < current_x)
                    if is_next_match:
                        await self.clear_search()

                        match_str = match.group()
                        match_coord = Coordinate(match.start(), linenr)
                        match_widget = SearchMatch(match_str, match_coord)
                        await self.mount(match_widget)
                        match_widget.scroll_visible()
                        return match_coord
            current_x = -1 if forward else self.size.width  # maybe virtual_size?

    async def clear_search(self) -> None:
        await self.query(SearchMatch.__name__).remove()

    def scroll_to_widget(self, *args, **kwargs) -> bool:
        return self.screen.scroll_to_widget(*args, **kwargs)

    # Already handled by self.styles.max_width
    # async def on_resize(self, event: events.Resize) -> None:
    #     self.styles.width = min(WIDTH, event.size.width - 2)
