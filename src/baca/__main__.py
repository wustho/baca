from .app import Baca
from .ebooks import Epub


def main():
    file = "/home/ss/Projects/baca.draft/tmp/pg11-images.epub"
    # file = "/home/ss/Projects/baca/tmp/andyweir.epub"
    ebook = Epub(file)
    # for s in ebook.iter_parsed_contents():
    #     print(s)
    #     print("==========")
    # print(ebook.get_parsed_contents())
    # print(list(ebook.iter_parsed_contents()))
    # for c in ebook.iter_parsed_contents():
    #     if c.type.value == "section":
    #         print(c)
    # list(ebook.iter_parsed_contents())[0]
    # print(ebook.get_toc())
    Baca(ebook).run()


if __name__ == "__main__":
    main()
