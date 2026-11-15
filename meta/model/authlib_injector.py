from typing import List

from . import MetaBase

class AuthlibInjectorVersion(MetaBase):
    version: str
    published_at: str
    download_url: str
    file_size: int
    file_sha1: str
    prerelease: bool
    recommended: bool


class AuthlibInjectorIndex(MetaBase):
    versions: List[AuthlibInjectorVersion]