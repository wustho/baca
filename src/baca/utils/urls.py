from urllib.parse import urlparse


def is_url(url: str) -> bool:
    return urlparse(url).scheme != ""
