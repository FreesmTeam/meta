from typing import List

from . import MetaBase

class GitHubReleaseAsset(MetaBase):
    browser_download_url: str
    size: int


class GitHubReleaseEntry(MetaBase):
    tag_name: str
    published_at: str
    assets: List[GitHubReleaseAsset]
    prerelease: bool


class GitHubReleaseIndex(MetaBase):
    __root__: List[GitHubReleaseEntry]


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