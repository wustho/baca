from textual.message import Message


class DoneLoading(Message):
    def __init__(self, content):
        super().__init__()
        self.content = content


class FollowThis(Message):
    def __init__(self, value: str):
        super().__init__()
        self.value = value


class OpenThisImage(Message):
    def __init__(self, value: str):
        super().__init__()
        self.value = value


class Screenshot(Message):
    pass
