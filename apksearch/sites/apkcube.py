import re
import urllib.parse

from bs4 import BeautifulSoup

from apksearch.sites import curl, requests


class APKCube:
    """
    This class provides methods to search for an APK on APKCube based on package name,
    and to find available versions and their download links for a given APK link.

    Parameters:
        pkg_name (str): The package name of the APK to search for.

    Attributes:
        pkg_name (str): The package name of the APK to search for.
        base_url (str): The base URL of the APKCube website.
        search_url (str): The URL used to search for APKs on APKCube.
        headers (dict): The headers used for making HTTP requests.
        session (requests.Session): The session object used for making HTTP requests.

    Methods:
        search_apk() -> None | tuple[str, str]:
            Searches for the APK on APKCube and returns the title and link if found.

        find_versions(apk_link: str) -> list[tuple[str, str]]:
            Finds and returns a list of versions and their download links for the given APK link.
    """

    def __init__(self, pkg_name: str):
        self.pkg_name = pkg_name
        self.base_url = "https://apkcube.com"
        self.search_url = self.base_url + "/search?q="
        self.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9,en-IN;q=0.8",
            "cache-control": "no-cache",
            "dnt": "1",
            "pragma": "no-cache",
            "priority": "u=0, i",
            "referer": "https://apkcube.com/",
            "sec-ch-ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        }
        self.session = requests.Session()

    def search_apk(self) -> None | tuple[str, str]:
        """
        Searches for the APK on APKCube and returns the title and link if found.

        Returns:
            None: If no matching APK is found.
            tuple[str, str]: A tuple containing the title and link of the matching APK if found.
        """
        pkg_name = self.pkg_name
        url = self.search_url + pkg_name
        params = {"headers": self.headers}
        if curl:
            params["impersonate"] = "chrome"

        response: requests.Response = self.session.get(url, **params)
        app_path = None
        if (
            response.status_code in (301, 302, 307, 308)
            and "Location" in response.headers
        ):
            app_path = response.headers["Location"]
        elif response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            meta = soup.find("meta", {"id": "__next-page-redirect"}) or soup.find(
                "meta", attrs={"http-equiv": lambda x: x and x.lower() == "refresh"}
            )
            if meta and "url=" in meta.get("content", ""):
                app_path = meta["content"].split("url=")[-1].strip()
            elif "NEXT_REDIRECT" in response.text:
                match = re.search(r"NEXT_REDIRECT;[^;]*;([^;]+);", response.text)
                if match:
                    app_path = match.group(1)

            if not app_path:
                for a in soup.find_all("a", href=True):
                    href = a["href"].split("?")[0].rstrip("/")
                    if href.endswith("/" + pkg_name):
                        app_path = a["href"]
                        break
        else:
            return None

        if not app_path:
            return None

        apk_link = urllib.parse.urljoin(self.base_url, app_path)
        if apk_link.split("?")[0].rstrip("/").split("/")[-1] != pkg_name:
            return None

        app_response: requests.Response = self.session.get(apk_link, **params)
        if app_response.status_code != 200:
            return None

        app_soup = BeautifulSoup(app_response.text, "html.parser")
        h1 = app_soup.find("h1")
        if h1:
            apk_title = h1.text.strip()
        elif app_soup.title and app_soup.title.string:
            apk_title = app_soup.title.string.split(" APK")[0].strip()
        else:
            apk_title = pkg_name

        return apk_title, apk_link

    def find_versions(self, apk_link: str) -> list[tuple[str, str]]:
        """
        Finds and returns a list of versions and their download links for the given APK link.

        Parameters:
            apk_link (str): The link to the APK on the APKCube website.

        Returns:
            list[tuple[str, str]]: A list of tuples, where each tuple contains the version number
            and its corresponding download link. If no versions are found, an empty list is returned.
        """
        versions_info = []
        seen = set()
        params = {"headers": self.headers}
        if curl:
            params["impersonate"] = "chrome"

        if apk_link.startswith(self.base_url):
            clean_link = apk_link.split("?")[0].rstrip("/")
            url = (
                clean_link
                if clean_link.endswith("/old-versions")
                else clean_link + "/old-versions"
            )
            response: requests.Response = self.session.get(url, **params)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                base_dl_path = clean_link.replace("/old-versions", "") + "/download"
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if "/download" in href:
                        parsed = urllib.parse.urlparse(href)
                        # Exclude the general 'Latest version' button without query params
                        if (
                            href.split("?")[0].rstrip("/") == base_dl_path
                            and not parsed.query
                        ):
                            continue
                        qs = urllib.parse.parse_qs(parsed.query)
                        apk_version = qs.get("version", [None])[0]
                        if not apk_version:
                            aria = a.get("aria-label", "")
                            match = re.search(
                                r"Download\s+.*?\s+([0-9]+(?:\.[0-9a-zA-Z\-_]+)+)",
                                aria,
                            )
                            if match:
                                apk_version = match.group(1)
                        if apk_version and apk_version not in seen:
                            seen.add(apk_version)
                            download_url = urllib.parse.urljoin(self.base_url, href)
                            versions_info.append((apk_version, download_url))

            if not versions_info:
                # Fallback to main app page if old-versions was not available
                main_url = clean_link.replace("/old-versions", "")
                response = self.session.get(main_url, **params)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    apk_version = None
                    if soup.title and soup.title.string:
                        m = re.search(
                            r"APK\s+([0-9]+(?:\.[0-9a-zA-Z\-_]+)+)\s+Download",
                            soup.title.string,
                        )
                        if m:
                            apk_version = m.group(1)
                    if not apk_version:
                        p = soup.find("p", class_=lambda c: c and "font-mono" in c)
                        if p and re.match(
                            r"^[0-9]+(?:\.[0-9a-zA-Z\-_]+)+$", p.text.strip()
                        ):
                            apk_version = p.text.strip()
                    if apk_version:
                        download_url = main_url + "/download"
                        versions_info.append((apk_version, download_url))

        return versions_info
