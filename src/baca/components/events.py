from textual.message import Message


class DoneLoading(Message):
    def __init__(self, content):
        super().__init__()
        self.content = content


class FollowThis(Message):
    def __init__(self, nav_point: str):
        super().__init__()
        self.nav_point = nav_point


class OpenThisImage(Message):
    def __init__(self, value: str):
        super().__init__()
        self.value = value


class SearchSubmitted(Message):
    def __init__(self, value: str, forward: bool):
        super().__init__()
        self.value = value
        self.forward = forward


class Screenshot(Message):
    pass
