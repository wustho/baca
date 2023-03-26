from rich.markdown import Markdown
from rich.text import Text
from textual import events
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import DataTable
from textual.widgets.markdown import Markdown as PrettyMarkdown

from ..ebooks import Ebook
from ..models import Config, SegmentType
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

    def __init__(self, config: Config, id: str | None = None):
        super().__init__(id=id)
        self.config = config


class Body(SegmentWidget):
    def __init__(self, config: Config, src: str):
        super().__init__(config)
        self._src = src

    def render(self):
        # NOTE: Markdwon rich isn't widget, so we cannot set using css
        # hence this translation workaround
        return Markdown(
            self._src, justify=dict(center="center", left="left", right="right", justify="full")[self.styles.text_align]  # type: ignore
        )


class Image(SegmentWidget):
    def __init__(self, config: Config, src: str):
        super().__init__(config)
        # TODO: maybe put it in Widget.id?
        self._src = src

    def render(self):
        return Text("🖼️  IMAGE", justify="center")

    # TODO: "Click ot Open" on mouse hover
    # def on_mouse_move(self, _: events.MouseMove) -> None:
    #     self.styles.background = "red"

    async def on_click(self) -> None:
        self.post_message(OpenThisImage(self._src))


class PrettyBody(PrettyMarkdown):
    def __init__(self, config: Config, value: str):
        super().__init__(value)


class Section(SegmentWidget):
    def __init__(self, config: Config, value: str):
        super().__init__(config=config)
        self.value = value

    def render(self):
        return self.value


class Content(Widget):
    can_focus = False

    def __init__(self, config: Config, ebook: Ebook):
        super().__init__()
        self.config = config

        self._segment_widgets: list[SegmentWidget | PrettyMarkdown] = []
        for segment in ebook.iter_parsed_contents():
            if segment.type == SegmentType.SECTION:
                component_cls = Section
            elif segment.type == SegmentType.BODY:
                component_cls = Body if not config.pretty else PrettyBody
            else:
                component_cls = Image
            self._segment_widgets.append(component_cls(self.config, segment.content))

    @property
    def sections(self) -> list[Section]:
        return [comp for comp in self._segment_widgets if isinstance(comp, Section)]

    def scroll_to_section(self, id: str) -> None:
        # TODO: add attr TocEntry.uuid so we can query("#{uuid}")
        for s in self.sections:
            if s.value == id:
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
        yield from iter(self._segment_widgets)

    def scroll_to_widget(self, *args, **kwargs) -> bool:
        return self.screen.scroll_to_widget(*args, **kwargs)

    # Already handled by self.styles.max_width
    # async def on_resize(self, event: events.Resize) -> None:
    #     self.styles.width = min(WIDTH, event.size.width - 2)
