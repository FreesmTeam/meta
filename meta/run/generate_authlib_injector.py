import base64
import os
from datetime import datetime
from typing import Tuple, List

from meta.common import launcher_path, upstream_path, ensure_component_dir
from meta.common.authlib_injector import AUTHLIBINJECTOR_COMPONENT, VERSIONS_FILE
from meta.model import MetaPackage, MetaVersion, JavaAgent, GradleSpecifier, MojangLibraryDownloads, MojangArtifact
from meta.model.authlib_injector import AuthlibInjectorIndex

LAUNCHER_DIR = launcher_path()
UPSTREAM_DIR = upstream_path()

ensure_component_dir(AUTHLIBINJECTOR_COMPONENT)

def process_versions(index: AuthlibInjectorIndex) -> Tuple[List[MetaVersion], List[str]]:
    jvm_args = ["-Dauthlibinjector.noLogFile", "-Dauthlibinjector.noShowServerName"]

    all_versions: List[MetaVersion] = []
    recommended = []
    for entry in index.versions:
        downloads = MojangLibraryDownloads(
            artifact=MojangArtifact(
                url=entry.download_url,
                size=entry.file_size,
                sha1=entry.file_sha1
            )
        )
        agent = JavaAgent(
            name=GradleSpecifier("moe.yushi", "authlibinjector", entry.version),
            downloads=downloads,
            argument="${authlib_injector_auth_url}"
        )

        meta_version = MetaVersion(
            name="authlib-injector",
            uid=AUTHLIBINJECTOR_COMPONENT,
            version=entry.version,
            release_time=datetime.fromisoformat(entry.published_at),
            java_agents=[agent],
            additional_jvm_args=jvm_args,
            type="snapshot" if entry.prerelease else "release"
        )
        all_versions.append(meta_version)
        if entry.recommended:
            recommended.append(entry.version)

    recommended.sort()

    all_versions.sort(key=lambda x: x.release_time, reverse=True)
    return all_versions, recommended


def main():
    index = AuthlibInjectorIndex.parse_file(os.path.join(UPSTREAM_DIR, VERSIONS_FILE))

    all_versions, recommended = process_versions(index)

    for version in all_versions:
        version.write(
            os.path.join(LAUNCHER_DIR, AUTHLIBINJECTOR_COMPONENT, f"{version.version}.json")
        )

    package = MetaPackage(
        uid=AUTHLIBINJECTOR_COMPONENT,
        name="authlib-injector",
        recommended=recommended
    )
    package.write(os.path.join(LAUNCHER_DIR, AUTHLIBINJECTOR_COMPONENT, "package.json"))


if __name__ == "__main__":
    main()
