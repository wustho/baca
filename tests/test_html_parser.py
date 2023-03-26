from baca.utils.html_parser import split_html_to_segments, parse_html_to_segmented_md

HTML_TEST = """
<html><head><title>The Dormouse's story</title></head>
<body>
<p class="title"><b>The Dormouse's story</b></p>

<p class="story">Once upon a time there were three little sisters; and their names were
<a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
  <a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
and they lived at the bottom of a well.</p>
<img src="img_girl.jpg" alt="Girl in a jacket" width="500" height="600">

<p class="story">...</p>
"""


# TODO:
def test_html_splitters():
    segments = split_html_to_segments(HTML_TEST, "test.html")
    assert True
