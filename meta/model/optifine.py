from typing import List, Optional
from pydantic import Field

from . import MetaBase


# {
#   "_id"      : string;
#   "mcversion": string;
#   "patch"    : string;
#   "type"     : string;
#   "__v"      : number;
#   "filename" : string;
#   "forge"   ?: string;
# }
class OptiFineIndexEntry(MetaBase):
    id: str = Field(alias="_id")
    mcversion: str
    patch: str
    type: str
    revision: int = Field(alias="__v")
    filename: str
    forge: Optional[str] = None


class OptiFineIndex(MetaBase):
    __root__: List[OptiFineIndexEntry]
