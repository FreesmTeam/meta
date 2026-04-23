from typing import List

from . import MetaBase

class ElyAuthlibVersion(MetaBase):
    target_version: str
    true_version: str
    download_url: str
    file_size: int
    file_sha1: str


class ElyAuthlibIndex(MetaBase):
    versions: List[ElyAuthlibVersion]
    last_updated: str