from rich.markdown import Markdown
from rich.text import Text
from textual import events
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import DataTable, LoadingIndicator, Static
from textual.widgets.markdown import Markdown as PrettyMarkdown

from ..config import Config
from ..ebooks import Ebook
from ..models import Layers, SegmentType
from .events import OpenThisImage


class Table(DataTable):
    can_focus = False

    def __init__(self, headers: list[str], rows: list[tuple]):
        super().__init__(show_header=True, zebra_stripes=True, show_cursor=False)
        self.add_columns(*headers)
        self.add_rows(rows)

    def on_mount(self) -> None:
        # NOTE: height & width important so table will overflow Metadata
        # instead of its ScrollView parent widget
        self.styles.height = "auto"
        self.styles.width = "auto"
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

    def on_mount(self) -> None:
        self.styles.height = "auto"

    def render(self):
        # return Text(" ".join([str(i) for i in range(1000)]), style="italic")
        return Markdown(self._src, justify=self.config.text_justification)


class Image(SegmentWidget):
    def __init__(self, config: Config, src: str):
        super().__init__(config)
        # TODO: maybe put it in Widget.id?
        self._src = src

    def on_mount(self) -> None:
        self.styles.height = "auto"
        self.styles.border = ("solid", "white")

    def render(self):
        return Text("🖼️  IMAGE", justify="center")

    # TODO: "Click ot Open" on mouse hover
    # def on_mouse_move(self, _: events.MouseMove) -> None:
    #     self.styles.background = "red"

    async def on_click(self) -> None:
        self.post_message(OpenThisImage(self._src))


class PrettyBody(PrettyMarkdown, SegmentWidget):
    def __init__(self, *args, **kwargs):
        super().__init__()


class Section(SegmentWidget):
    def __init__(self, config: Config, value: str):
        super().__init__(config=config, id=value)

    def render(self):
        return self.id

    def on_mount(self) -> None:
        self.styles.background = "red"
        self.styles.height = 1
        # NOTE: cannot use 'visibility=hidden' and 'display=none'
        # so use "opacity=0%" instead
        self.styles.opacity = "0%"
        # self.styles.visibility = "hidden"
        # self.styles.display = "none"


class Content(Widget):
    can_focus = False

    def __init__(self, config: Config, ebook: Ebook):
        super().__init__()
        self.config = config

        self._segment_widgets: list[SegmentWidget] = []
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
            if s.id == id:
                s.scroll_visible(top=True)
                break

    def on_mount(self) -> None:
        self.styles.layout = "vertical"
        self.styles.height = "auto"
        self.styles.layer = Layers.CONTENT.value
        self.styles.max_width = self.config.max_text_width
        self.styles.margin = (0, 2)

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
