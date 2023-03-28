from baca.utils.html_parser import split_html_to_segments
from baca.models import SegmentType

HTML_TEST = """
<html><head><title>The Dormouse's story</title></head>
<body>
<p class="title"><b>The Dormouse's
story</b></p>

<p class="story">Once upon a time there were three little sisters; and their names were
<a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
  <a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
and they lived at the bottom of a well.</p>
<img src="img_girl.jpg" alt="Girl in a jacket" width="500" height="600">

<p class="story">...</p>
"""


def test_html_splitters():
    segments_iterator = split_html_to_segments(HTML_TEST, "test.html")

    segment = next(segments_iterator)
    assert segment.type == SegmentType.BODY
    assert (
        segment.content
        == '<body> <p class="title"><b>The Dormouse\'s story</b></p> <p class="story">Once upon a time there were three little sisters; and their names were '
    )
    assert segment.nav_point == "test.html"

    segment = next(segments_iterator)
    assert segment.type == SegmentType.BODY
    assert segment.content == '<a class="sister" href="http://example.com/elsie" id="link1">Elsie</a>,   '
    assert segment.nav_point == "test.html#link1"

    segment = next(segments_iterator)
    assert segment.type == SegmentType.BODY
    assert (
        segment.content
        == '<a class="sister" href="http://example.com/lacie" id="link2">Lacie</a> and and they lived at the bottom of a well.</p> '
    )
    assert segment.nav_point == "test.html#link2"

    segment = next(segments_iterator)
    assert segment.type == SegmentType.IMAGE
    assert segment.content == "img_girl.jpg"
    assert segment.nav_point is None

    segment = next(segments_iterator)
    assert segment.type == SegmentType.BODY
    assert (
        segment.content
        == '<img alt="Girl in a jacket" height="600" src="img_girl.jpg" width="500"/> <p class="story">...</p> </body>'
    )
    assert segment.nav_point is None
