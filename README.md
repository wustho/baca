# `baca`: TUI Ebook Reader

![baca_fit](https://user-images.githubusercontent.com/43810055/227891952-45df1c36-5113-4793-84b6-249725d3ba19.png)

Meet `baca`, [epy](https://github.com/wustho/epy)'s lovely sister who lets you indulge
in your favorite e-books in the comfort of your terminal.
But with a sleek and contemporary appearance that's sure to captivate you!

## Features

- Formats supported: Epub, Epub3, Mobi & Azw
- Remembers last reading position
- Scroll animations
- Clean & modern looks
- Lets you open images
- Text justification

## Requirements

- `python>=3.10`

## Installation

- Via pip: `pip install baca`
- Via git: `pip install git+https://github.com/wustho/baca`

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

To open an image, when you encounter some thing like this:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                                  🖼️  IMAGE                                   │
└──────────────────────────────────────────────────────────────────────────────┘
```

just click on it using mouse and it will open the image.
Yeah, I know you want to use keyboard for this, me too, but bear with this for now.

## Configurations

Configuration file available at `~/.config/baca/config.ini`.

## Current Limitations

Compared to [epy](https://github.com/wustho/epy), currently `baca` has some missing features.
But these are planned to be implemented to `baca` in the near future:

- [ ] **TODO** Search feature
- [ ] **TODO** Bookmarks
- [ ] **TODO** FictionBook support
- [ ] **TODO** URL reading support
- [ ] **TODO** Transparent background

## Credits

- Thanks to awesome [Textual Project](https://github.com/Textualize/textual)
- [Kindle Unpack](https://github.com/kevinhendricks/KindleUnpack)
- And many others!

## License

GPL-3
