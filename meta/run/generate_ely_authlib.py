import os
from datetime import datetime
from typing import List

from meta.common import launcher_path, upstream_path
from meta.common.ely_authlib import VERSIONS_FILE, ELY_AUTHLIB_COMPONENT
from meta.model import MetaPackage, MetaVersion, GradleSpecifier, MojangLibraryDownloads, MojangArtifact, Library
from meta.model.ely_authlib import ElyAuthlibIndex

LAUNCHER_DIR = launcher_path()
UPSTREAM_DIR = upstream_path()

def process_versions(index: ElyAuthlibIndex) -> List[MetaVersion]:
    versions: List[MetaVersion] = []
    last_updated = datetime.strptime(index.last_updated, "%Y%m%d%H%M%S")

    for entry in index.versions:
        downloads = MojangLibraryDownloads(
            artifact=MojangArtifact(
                url=entry.download_url,
                size=entry.file_size,
                sha1=entry.file_sha1
            )
        )
        library = Library(
            name=GradleSpecifier("by.ely", "authlib", entry.true_version),
            downloads=downloads
        )

        meta_version = MetaVersion(
            name="Ely.by Authlib",
            uid=ELY_AUTHLIB_COMPONENT,
            version=entry.target_version,
            release_time=last_updated,
            libraries=[library]
        )
        versions.append(meta_version)

    return versions


def main():
    index = ElyAuthlibIndex.parse_file(os.path.join(UPSTREAM_DIR, VERSIONS_FILE))

    versions = process_versions(index)

    for version in versions:
        version.write(
            os.path.join(LAUNCHER_DIR, ELY_AUTHLIB_COMPONENT, f"{version.version}.json")
        )

    package = MetaPackage(
        name="Ely.by Authlib",
        uid=ELY_AUTHLIB_COMPONENT
    )
    package.write(os.path.join(LAUNCHER_DIR, ELY_AUTHLIB_COMPONENT, "package.json"))


if __name__ == "__main__":
    main()
