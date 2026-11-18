import os

import requests

DOWNLOAD_ATTEMPTS = 3


def get_github_releases(sess, repo: str) -> list[dict]:
    releases = []
    page = 1
    while True:
        r = sess.get(
            f"https://api.github.com/repos/{repo}/releases",
            params={"per_page": 100, "page": page},
        )
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        releases.extend(batch)
        page += 1
    return releases


def download_binary_file(sess, path, url):
    for attempt in range(DOWNLOAD_ATTEMPTS):
        try:
            with sess.get(url, stream=True) as r:
                r.raise_for_status()
                with open(path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=128):
                        f.write(chunk)
            return
        except (requests.ConnectionError, requests.exceptions.ChunkedEncodingError):
            if attempt == DOWNLOAD_ATTEMPTS - 1:
                raise
