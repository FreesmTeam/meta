import os
import io
import zipfile
import hashlib

from pathlib import Path
from typing import List
from datetime import datetime, timezone

from meta.common import (
    ensure_component_dir,
    launcher_path,
    upstream_path,
    cache_path,
    default_session,
)
from meta.common.mojang import MINECRAFT_COMPONENT
from meta.common.optifine import (
    OPTIFINE_COMPONENT,
    DEFAULT_LAUNCHWRAPPER_VERSION,
    BASE_MULTIMC_MAVEN_URL,
    BASE_OPTIFINE_DOWNLOAD_URL,
    BASE_LAUNCHWRAPPER_DOWNLOAD_URL,
    VERSIONS_FILE,
)
from meta.model import (
    MetaVersion,
    GradleSpecifier,
    Library,
    MetaPackage,
    Dependency,
    MojangLibraryDownloads,
    MojangArtifact,
)
from meta.model.optifine import OptiFineIndex, OptiFineIndexEntry

LAUNCHER_DIR = launcher_path()
UPSTREAM_DIR = upstream_path()
CACHE_DIR = cache_path()

ensure_component_dir(OPTIFINE_COMPONENT)

sess = default_session()


def get_release_time(index: int):
    return datetime.fromtimestamp(index, tz=timezone.utc)


# Besides bundling the launchwrapper .jar file, OptiFine also
# almost certainly has a 'launchwrapper-of.txt' file with the
# necessary version of a custom launchwrapper inside the file
#
# MultiMC for some reason hosts these OptiFine-specific
# launchwrappers at https://files.multimc.org/maven
def get_launchwrapper_version(contents: bytes) -> str:
    with zipfile.ZipFile(io.BytesIO(contents)) as archive:
        try:
            version = archive.read("launchwrapper-of.txt")

            return version.decode("utf-8").strip()
        except KeyError:
            return DEFAULT_LAUNCHWRAPPER_VERSION


def download_version(url: str) -> bytes:
    encoded = url.encode("utf-8")
    key = hashlib.sha256(encoded).hexdigest()
    cache_file = Path(CACHE_DIR) / "optifine_cache" / f"{key}.jar"

    if cache_file.is_file():
        print(f"Found cache for {url}")

        return cache_file.read_bytes()

    print(f"Downloading {url}")

    r = sess.get(url)
    r.raise_for_status()

    contents = r.content

    # BMCLAPI literally provides zero valuable information for jars
    # so we just ensure this is an archive and not some corrupted file
    with zipfile.ZipFile(io.BytesIO(contents)) as archive:
        if archive.testzip():
            raise ValueError(f"Corrupted jar file for {url}")

    cache_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        cache_file.write_bytes(contents)
    except Exception:
        cache_file.unlink(missing_ok=True)
        raise

    return contents


def get_optifine_launchwrapper(version: str) -> bytes:
    url = BASE_LAUNCHWRAPPER_DOWNLOAD_URL % (version, version)
    r = sess.get(url)
    r.raise_for_status()

    return r.content


def produce_patch(entry: OptiFineIndexEntry, index: int) -> MetaVersion:
    url = BASE_OPTIFINE_DOWNLOAD_URL % (entry.mcversion, entry.type, entry.patch)
    contents = download_version(url)
    launchwrapper_version = get_launchwrapper_version(contents)
    launchwrapper_version_specifier = (
        # An official one
        launchwrapper_version
        if launchwrapper_version == DEFAULT_LAUNCHWRAPPER_VERSION
        # An OptiFine-specific one
        else f"of-{launchwrapper_version}"
    )

    launchwrapper = Library(
        name=GradleSpecifier(
            MINECRAFT_COMPONENT,
            "launchwrapper",
            launchwrapper_version_specifier,
        ),
    )

    if launchwrapper_version != DEFAULT_LAUNCHWRAPPER_VERSION:
        launchwrapper.url = BASE_MULTIMC_MAVEN_URL

    optifine_version = f"{entry.mcversion}_{entry.type}_{entry.patch}"
    optifine = Library(
        name=GradleSpecifier(OPTIFINE_COMPONENT, "optifine", optifine_version),
        downloads=MojangLibraryDownloads(
            artifact=MojangArtifact(
                url=url,
                sha1=hashlib.sha1(contents).hexdigest(),
                size=len(contents),
            ),
        ),
    )

    return MetaVersion(
        uid=OPTIFINE_COMPONENT,
        name="OptiFine",
        version=optifine_version,
        release_time=get_release_time(index),
        requires=[
            Dependency(
                uid=MINECRAFT_COMPONENT,
                equals=entry.mcversion,
            )
        ],
        main_class="net.minecraft.launchwrapper.Launch",
        additional_tweakers="optifine.OptiFineTweaker",
        libraries=[launchwrapper, optifine],
    )


def process_versions(index: OptiFineIndex) -> List[MetaVersion]:
    all_versions: List[MetaVersion] = []
    for index, entry in enumerate(index.__root__):
        patch = produce_patch(entry, index)

        if patch is not None:
            all_versions.append(patch)

    all_versions.sort(key=lambda x: x.release_time, reverse=True)

    return all_versions


def main():
    index = OptiFineIndex.parse_file(os.path.join(UPSTREAM_DIR, VERSIONS_FILE))

    all_versions = process_versions(index)

    for version in all_versions:
        version.write(
            os.path.join(
                LAUNCHER_DIR,
                OPTIFINE_COMPONENT,
                f"{version.mcversion}_{version.type}_{version.patch}.json",
            )
        )

    package = MetaPackage(
        uid=OPTIFINE_COMPONENT,
        name="OptiFine",
        # https://www.minecraftforum.net/forums/mapping-and-modding-java-edition/minecraft-mods/1272953-optifine-hd-fps-boost-dynamic-lights-shaders-and
        description="This mod adds support for HD textures and a lot of options for better looks and performance",
        project_url="https://optifine.net/home",
        authors=["sp614x"],
    )
    package.write(os.path.join(LAUNCHER_DIR, OPTIFINE_COMPONENT, "package.json"))


if __name__ == "__main__":
    main()
