import concurrent.futures
import hashlib
import os

from packaging.version import Version
from xml.etree import ElementTree

from meta.common import upstream_path, ensure_upstream_dir, default_session
from meta.common.ely_authlib import BASE_DIR, MAVEN_METADATA_URL, BASE_AUTHLIB_DOWNLOAD_URL, VERSIONS_FILE
from meta.model.ely_authlib import ElyAuthlibVersion, ElyAuthlibIndex

UPSTREAM_DIR = upstream_path()

ensure_upstream_dir(BASE_DIR)

sess = default_session()

def fetch_library_data(target_version: str, true_version: str) -> ElyAuthlibVersion:
    download_url = BASE_AUTHLIB_DOWNLOAD_URL % (true_version, true_version)
    r = sess.get(download_url)
    r.raise_for_status()

    content: bytes = r.content

    return ElyAuthlibVersion(
        target_version=target_version,
        true_version=true_version,
        download_url=download_url,
        file_size=len(content),
        file_sha1=hashlib.sha1(content).hexdigest()
    )


def main():
    print("Getting Ely Authlib Maven metadata")
    r = sess.get(MAVEN_METADATA_URL)
    r.raise_for_status()

    root = ElementTree.fromstring(r.content)

    print("Mapping target versions to true versions")
    target_versions_to_true_versions = dict()
    for version_element in root.iter("version"):
        version = version_element.text
        target_version = version[:version.find("-")]
        ely_patch_version = int(version[(version.rfind(".") + 1):])

        existing_version = target_versions_to_true_versions.get(target_version, "0.0-ely.0")
        existing_ely_patch_version = int(existing_version[(existing_version.rfind(".") + 1):])

        if ely_patch_version > existing_ely_patch_version:
            target_versions_to_true_versions[target_version] = version

    futures = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for target_version, true_version in target_versions_to_true_versions.items():
            print(f"{target_version} -> {true_version}")
            futures.append(executor.submit(fetch_library_data, target_version, true_version))

    versions = []
    for future in futures:
        versions.append(future.result())

    versions.sort(key=lambda v: Version(v.target_version), reverse=True)

    last_updated = root.find("versioning").find("lastUpdated").text
    authlib_index = ElyAuthlibIndex(
        versions=versions,
        last_updated=last_updated
    )
    authlib_index.write(os.path.join(UPSTREAM_DIR, VERSIONS_FILE))

if __name__ == "__main__":
    main()