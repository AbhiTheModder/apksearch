import argparse

from apksearch import APKPure
from requests.exceptions import ConnectionError, ConnectTimeout

# Color codes
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
NC = "\033[0m"


def search_apkpure(pkg_name: str, version: str | None) -> None:
    apkpure = APKPure(pkg_name)
    try:
        result_apkpure: tuple[str, str] | None = apkpure.search_apk()
    except (ConnectionError, ConnectTimeout):
        result_apkpure = None
        print(f"{RED}Failed to resolve 'apkpure.net'!{NC}")
    if result_apkpure:
        title, apk_link = result_apkpure
        print(
            f"{BOLD}Found {GREEN}{title}{NC} on {YELLOW}APKPure{NC}"
        ) if title else None
        print(f"      ╰─> {BOLD}Link: {YELLOW}{apk_link}{NC}") if not version else None
        versions: list[tuple[str, str]] = apkpure.find_versions(apk_link)
        if version:
            for version_tuple in versions:
                if version_tuple[0] == version:
                    print(
                        f"{BOLD}Found version {GREEN}{version}{NC} at {YELLOW}{version_tuple[1]}{NC}"
                    )
                    break
            else:
                print(f"{BOLD}Version {RED}{version}{NC} not found")
    else:
        print(f"{BOLD}No Results for {RED}{pkg_name}{NC} on APKPure!")


def main():
    parser = argparse.ArgumentParser(description="Search for APKs on various websites")
    parser.add_argument("pkg_name", help="The package name of the APK")
    parser.add_argument("--version", help="The version of the APK", required=False)
    args = parser.parse_args()

    pkg_name = args.pkg_name
    version = args.version
    print(f"{BOLD}Searching for {YELLOW}{pkg_name}{NC}...")
    # Initiate search on apkpure
    search_apkpure(pkg_name, version)


if __name__ == "__main__":
    main()
