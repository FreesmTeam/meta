from typing import List

from . import MetaBase

class GitHubReleaseAsset(MetaBase):
    name: str
    browser_download_url: str
    size: int


class GitHubReleaseEntry(MetaBase):
    tag_name: str
    published_at: str
    assets: List[GitHubReleaseAsset]
    prerelease: bool


class GitHubReleaseIndex(MetaBase):
    __root__: List[GitHubReleaseEntry]