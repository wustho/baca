# `baca`: TUI E-book Reader

![baca_screenshots](https://github.com/wustho/baca/assets/43810055/82d5beb0-d061-4e4c-82ed-a3bd84074d2f)

Meet `baca`, [epy](https://github.com/wustho/epy)'s lovely sister who lets you indulge
in your favorite e-books in the comfort of your terminal.
But with a sleek and contemporary appearance that's sure to captivate you!

## Features

- Formats supported: Epub, Epub3, Mobi & Azw
- Remembers last reading position
- Show images as ANSI image & you can click it for more detail
- Scroll animations
- Clean & modern looks
- Text justification
- Dark & light color scheme
- Regex search
- Hyperlinks

## Requirements

- `python>=3.10`

## Installation

- Via pip: `pip install baca`
- Via git: `pip install git+https://github.com/wustho/baca`
- Via AUR: `yay -S baca-ereader-git`

## Usage

```sh
# to read an ebook
baca path/to/your/ebook.epub

# to read your last read ebook, just run baca without any argument
baca

# to see your reading history use -r as an argument
baca -r

# say you want to read an ebook from your reading history,
# but you forgot the path to your ebook
# just type any words you remember about your ebook
# and baca will try to match it to path or title+author
baca doc ebook.epub
baca alice wonder lewis carroll
```

## Opening an Image

To open an image, when you encounter an ANSI image (when `ShowImageAsANSI=yes`) or some thing like this
(if `ShowImageAsANSI=no`):

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                                    IMAGE                                     │
└──────────────────────────────────────────────────────────────────────────────┘
```

just click on it using mouse and it will open the image using system app.
Yeah, I know you want to use keyboard for this, me too, but bear with this for now.

> "Why show the images as ANSI images instead of render it directly on terminal like ranger does?"

1. The main reason is that currently, rendering images directly on the terminal
   doesn't allow for partial scrolling of the image.
   This means that we can't display only a portion (e.g., 30%) of the image when scrolling,
   resulting in a broken and non-seamless scrolling experience.

2. My primary intention in developing this app is for reading fiction e-books rather than technical ones,
   and most fiction e-books don't contain many images.

3. Displaying images on the terminal requires different implementations for various terminal emulators,
   which requires a lot of maintenance.

## Configurations

![pretty_yes_no_cap](https://user-images.githubusercontent.com/43810055/228417623-ac78fb84-0ee0-4930-a843-752ef693822d.png)

Configuration file available at `~/.config/baca/config.ini` for linux users. Here is the default:

```ini
[General]
# pick your favorite image viewer
PreferredImageViewer = auto

# int or css value string like 90%%
# (escape percent with double percent %%)
MaxTextWidth = 80

# 'justify', 'center', 'left', 'right'
TextJustification = justify

# currently using pretty=yes is slow
# and taking huge amount of memory
Pretty = no

PageScrollDuration = 0.2

# either show image as ansii image
# or text 'IMAGE' as a placehoder
# (showing ansii image will affect
# performance & resource usage)
ShowImageAsANSII = yes

[Color Dark]
Background = #1e1e1e
Foreground = #f5f5f5
Accent = #0178d4

[Color Light]
Background = #f5f5f5
Foreground = #1e1e1e
Accent = #0178d4

[Keymaps]
ToggleLightDark = c
ScrollDown = down,j
ScrollUp = up,k
PageDown = ctrl+f,pagedown,l,space
PageUp = ctrl+b,pageup,h
Home = home,g
End = end,G
OpenToc = tab
OpenMetadata = M
OpenHelp = f1
SearchForward = slash
SearchBackward = question_mark
NextMatch = n
PreviousMatch = N
Confirm = enter
CloseOrQuit = q,escape
Screenshot = f12
```

## Known Limitations

- When searching for specific phrases in `baca`,
  keep in mind that it may not be able to find them if they span across two lines,
  much like in the search behavior of editor vi(m).

  For example, `baca` won't be able to find the phrase `"for it"` because it is split into two lines
  in this example.

  ```
  ...
  she had forgotten the little golden key, and when she went back to the table for
  it, she found she could not possibly reach it: she could see  it  quite  plainly
  ...
  ```


  Additionally, `baca` may struggle to locate certain phrases due to adjustments made for text justification.
  See the example above, `"see_it"` may become `"see__it"` due to adjusted spacing between words.
  In this case, it may be more effective to use a regex search for `"see +it"` or simply search for the word `"see"` alone.

  Overall, `baca`'s search feature is most effective for locating individual words
  rather than phrases that may be split across multiple lines or impacted by text justification.

- Compared to [epy](https://github.com/wustho/epy), currently `baca` has some missing features.
  But these are planned to be implemented to `baca` in the near future:

  - [ ] **TODO** Bookmarks
  - [ ] **TODO** FictionBook support
  - [ ] **TODO** URL reading support

## Credits

- Thanks to awesome [Textual Project](https://github.com/Textualize/textual)
- [Kindle Unpack](https://github.com/kevinhendricks/KindleUnpack)
- And many others!

## License

GPL-3

