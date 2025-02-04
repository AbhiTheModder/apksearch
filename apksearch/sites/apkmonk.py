import re
from bs4 import BeautifulSoup
from curl_cffi import requests


class APKMonk:
    """
    This class provides methods to search for an APK on APKMonk based on package name,
    and to find available versions and their download links for a given APK link.

    Parameters:
        pkg_name (str): The package name of the APK to search for.

    Attributes:
        pkg_name (str): The package name of the APK to search for.
        base_url (str): The base URL of the APKMonk website.
        search_url (str): The URL used to search for APKs on APKMonk.
        headers (dict): The headers used for making HTTP requests.
        session (requests.Session): The session object used for making HTTP requests.

    Methods:
        search_apk() -> None | tuple[str, str]:
            Searches for the APK on APKMonk and returns the title and link if found.

        find_versions(apk_link: str) -> list[tuple[str, str]]:
            Finds and returns a list of versions and their download links for the given APK link.
    """

    def __init__(self, pkg_name: str):
        self.pkg_name = pkg_name
        self.base_url = "https://www.apkmonk.com"
        self.search_url = self.base_url + "/ssearch?q="
        self.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9,en-IN;q=0.8",
            "cache-control": "no-cache",
            "dnt": "1",
            "pragma": "no-cache",
            "priority": "u=0, i",
            "referer": "https://www.apkmonk.com/",
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
        Searches for the APK on APKMonk and returns the title and link if found.

        Returns:
            None: If no matching APK is found.
            tuple[str, str]: A tuple containing the title and link of the matching APK if found.
        """
        pkg_name = self.pkg_name
        url = self.search_url + pkg_name
        response: requests.Response = self.session.get(
            url, headers=self.headers, impersonate="chrome"
        )
        soup = BeautifulSoup(response.text, "html.parser")
        search_results = soup.find("a", {"title": re.compile(".*apk$")})
        if search_results:
            link = search_results["href"]
            title = search_results.find("span", {"class": "af-title truncate"}).text
            if link == f"/app/{pkg_name}/":
                return title, f"{self.base_url}{link}"
        return None

    def find_versions(self, apk_link: str) -> list[tuple[str, str]]:
        """
        Finds and returns a list of versions and their download links for the given APK link.

        Parameters:
            apk_link (str): The link to the APK on the APKMonk website.

        Returns:
            list[tuple[str, str]]: A list of tuples, where each tuple contains the version number
            and its corresponding download link. If no versions are found, an empty list is returned.
        """
        versions_info = []
        if apk_link.startswith(self.base_url):
            url = apk_link
            response: requests.Response = self.session.get(
                url, headers=self.headers, impersonate="chrome"
            )
            soup = BeautifulSoup(response.text, "html.parser")

            version_header = soup.find(
                "div",
                {"class": "box-title"},
                text=re.compile("All Versions", re.IGNORECASE),
            )

            if version_header:
                versions_table = version_header.find_next("table", {"class": "striped"})

                if versions_table:
                    rows = versions_table.find_all("tr")
                    for row in rows:
                        version_link = row.find("a", href=True)
                        if version_link:
                            version_number = version_link.text.strip()
                            download_url = self.base_url + version_link["href"]
                            versions_info.append((version_number, download_url))

        return versions_info
