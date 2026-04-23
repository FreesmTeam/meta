import concurrent.futures
import hashlib
import os

from meta.common import upstream_path, ensure_upstream_dir, default_session
from meta.common.authlib_injector import BASE_DIR, RELEASES_API_URL, VERSIONS_FILE
from meta.model.authlib_injector import GitHubReleaseIndex, AuthlibInjectorVersion, AuthlibInjectorIndex, \
    GitHubReleaseEntry

UPSTREAM_DIR = upstream_path()

ensure_upstream_dir(BASE_DIR)

sess = default_session()

def convert_to_authlib_injector(entry: GitHubReleaseEntry, is_recommended: bool) -> AuthlibInjectorVersion:
    asset = entry.assets[0]
    download_url = asset.browser_download_url

    print(f"Downloading {download_url}")
    r = sess.get(download_url)
    r.raise_for_status()

    return AuthlibInjectorVersion(
        version = entry.tag_name.replace("v", ""),
        published_at = entry.published_at,
        download_url = download_url,
        file_size = asset.size,
        file_sha1 = hashlib.sha1(r.content).hexdigest(),
        prerelease = entry.prerelease,
        recommended=is_recommended
    )


def main():
    print("Getting authlib-injector release manifests")
    r = sess.get(RELEASES_API_URL)
    r.raise_for_status()

    main_json = r.json()
    github_index = GitHubReleaseIndex.parse_obj(main_json)

    futures = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        has_recommended = False
        for entry in github_index.__root__:
            recommended = (not entry.prerelease and not has_recommended)
            futures.append(executor.submit(convert_to_authlib_injector, entry, recommended))
            if recommended:
                has_recommended = True

    versions = []
    for future in futures:
        versions.append(future.result())

    injector_index = AuthlibInjectorIndex(
        versions=versions,
    )
    injector_index.write(os.path.join(UPSTREAM_DIR, VERSIONS_FILE))


if __name__ == "__main__":
    main()