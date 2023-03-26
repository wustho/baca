class TableDoesNotExist(Exception):
    pass


class ImageOpenerDoesNotExist(Exception):
    def __init__(self):
        # TODO:
        super().__init__("")
