import json
import os

from meta.common import upstream_path, ensure_upstream_dir, default_session
from meta.common.optifine import VERSIONS_FILE, BASE_DIR, OPTIFINE_INDEX_URL
from meta.model.optifine import OptiFineIndex

UPSTREAM_DIR = upstream_path()

ensure_upstream_dir(BASE_DIR)

sess = default_session()


def main():
    r = sess.get(OPTIFINE_INDEX_URL)
    r.raise_for_status()

    main_json = r.json()

    remote_versions = OptiFineIndex.parse_obj(main_json)
    parsed = remote_versions.json()
    original = json.dumps(main_json, sort_keys=True, indent=4)
    assert parsed == original

    print("Successfully parsed index")
    print(f"Total entries is {len(remote_versions.__root__)}")

    remote_versions.write(os.path.join(UPSTREAM_DIR, VERSIONS_FILE))


if __name__ == "__main__":
    main()
