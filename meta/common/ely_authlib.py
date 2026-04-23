from os.path import join

BASE_DIR = "ely_authlib"

MAVEN_METADATA_URL = "https://maven.ely.by/releases/by/ely/authlib/maven-metadata.xml"

BASE_AUTHLIB_DOWNLOAD_URL = "https://repo.llaun.ch/libraries/by/ely/authlib/%s/authlib-%s.jar"

VERSIONS_FILE = join(BASE_DIR, "versions.json")

ELY_AUTHLIB_COMPONENT = "by.ely.authlib"
