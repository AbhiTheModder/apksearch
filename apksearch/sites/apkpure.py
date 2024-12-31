import re
from bs4 import BeautifulSoup
import requests


class APKPure:
    """
    This class provides methods to search for an APK on APKPure based on package name,
    and to find available versions and their download links for a given APK link.

    Parameters:
        pkg_name (str): The package name of the APK to search for.

    Attributes:
        pkg_name (str): The package name of the APK to search for.
        base_url (str): The base URL of the APKPure website.
        search_url (str): The URL used to search for APKs on APKPure.
        headers (dict): The headers used for making HTTP requests.
        session (requests.Session): The session object used for making HTTP requests.

    Methods:
        search_apk() -> None | tuple[str, str]:
            Searches for the APK on APKPure and returns the title and link if found.

        find_versions(apk_link: str) -> list[tuple[str, str]]:
            Finds and returns a list of versions and their download links for the given APK link.
    """

    def __init__(self, pkg_name: str):
        self.pkg_name = pkg_name
        self.base_url = "https://apkpure.net"
        self.search_url = self.base_url + "/search?q="
        self.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9,en-IN;q=0.8",
            "cache-control": "no-cache",
            "dnt": "1",
            "pragma": "no-cache",
            "priority": "u=0, i",
            "referer": "https://apkpure.net/",
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
        Searches for the APK on APKPure and returns the title and link if found.

        Returns:
            None: If no matching APK is found.
            tuple[str, str]: A tuple containing the title and link of the matching APK if found.
        """
        pkg_name = self.pkg_name
        url = self.search_url + pkg_name
        response: requests.Response = self.session.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")
        search_results = soup.find("div", {"class": "apk-list"})
        if search_results:
            apk_items = search_results.find_all("a", {"class": "apk-item"})
            if apk_items:
                for apk_item in apk_items:
                    apk_link = self.base_url + apk_item["href"]
                    apk_title = apk_item["title"]
                    apk_package_name = apk_item["data-dt-pkg"]
                    if apk_package_name == pkg_name:
                        return apk_title, apk_link
        return None

    def find_versions(self, apk_link: str) -> list[tuple[str, str]]:
        """
        Finds and returns a list of versions and their download links for the given APK link.

        Parameters:
            apk_link (str): The link to the APK on the APKPure website.

        Returns:
            list[tuple[str, str]]: A list of tuples, where each tuple contains the version number
            and its corresponding download link. If no versions are found, an empty list is returned.
        """
        url = apk_link + "/versions"
        response: requests.Response = self.session.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")
        versions_list = soup.find("ul", {"class": "version-list"})
        versions_info = []

        if versions_list:
            versions = versions_list.find_all(
                "li", {"class": re.compile("^version dt-version-item.*")}
            )
            for version in versions:
                version_icon = version.find("a", {"class": "dt-version-icon"})
                version_info = version.find("div", {"class": "version-info"})
                if version_icon and version_info:
                    version_number = version_info.find(
                        "span", {"class": "name one-line"}
                    ).text
                    download_url = self.base_url + version_icon["href"]
                    versions_info.append((version_number, download_url))

        return versions_info
