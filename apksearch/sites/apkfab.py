from bs4 import BeautifulSoup
import requests


class APKFab:
    """
    This class provides methods to search for an APK on APKFab based on package name,
    and to find available versions and their download links for a given APK link.

    Parameters:
        pkg_name (str): The package name of the APK to search for.

    Attributes:
        pkg_name (str): The package name of the APK to search for.
        base_url (str): The base URL of the APKFab website.
        search_url (str): The URL used to search for APKs on APKFab.
        headers (dict): The headers used for making HTTP requests.
        session (requests.Session): The session object used for making HTTP requests.

    Methods:
        search_apk() -> None | tuple[str, str]:
            Searches for the APK on APKFab and returns the title and link if found.

        find_versions(apk_link: str) -> list[tuple[str, str]]:
            Finds and returns a list of versions and their download links for the given APK link.
    """

    def __init__(self, pkg_name: str):
        self.pkg_name = pkg_name
        self.base_url = "https://apkfab.com"
        self.search_url = self.base_url + "/search?q="
        self.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9,en-IN;q=0.8",
            "cache-control": "no-cache",
            "dnt": "1",
            "pragma": "no-cache",
            "priority": "u=0, i",
            "referer": "https://apkfab.com/search",
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
        Searches for the APK on APKFab and returns the title and link if found.

        Returns:
            None: If no matching APK is found.
            tuple[str, str]: A tuple containing the title and link of the matching APK if found.
        """
        pkg_name = self.pkg_name
        url = self.search_url + pkg_name
        response: requests.Response = self.session.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")
        search_result = soup.find("div", {"class": "search-white"})
        if search_result:
            container = search_result.find("div", {"class": "container"})
            if container:
                lists = container.find("div", {"class": "list-template lists"})
                if lists:
                    items = lists.find_all("div", {"class": "list"})
                    if items:
                        item = items[0]
                        apk_title = item.find("div", {"class": "title"}).text
                        apk_link = item.find("a")["href"]
                        package_name = apk_link.split("/")[-1]
                        if package_name == pkg_name:
                            return apk_title, apk_link
        return None

    def find_versions(self, apk_link: str) -> list[tuple[str, str]]:
        """
        Finds and returns a list of versions and their download links for the given APK link.

        Parameters:
            apk_link (str): The link to the APK on the APKFab website.

        Returns:
            list[tuple[str, str]]: A list of tuples, where each tuple contains the version number
            and its corresponding download link. If no versions are found, an empty list is returned.
        """
        versions_info = []
        if apk_link.startswith(self.base_url):
            url = apk_link + "/versions"
            response: requests.Response = self.session.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, "html.parser")
            versions_list = soup.find("div", {"class": "version_history"})

            if versions_list:
                versions = versions_list.find_all("div", {"class": "list"})
                if versions:
                    for version in versions:
                        package_info = version.find(
                            "div", {"class": "package_info open_info"}
                        )
                        if package_info:
                            title = package_info.find("div", {"class": "title"})
                            apk_version = title.find(
                                "span", {"class": "version"}
                            ).text.strip()
                            dl = version.find(
                                "div", {"class": "v_h_button button_down"}
                            )
                            if dl:
                                download_link = dl.find("a")["href"]
                                versions_info.append((apk_version, download_link))
                            else:
                                # Some versions have multiple variants
                                versions_info.append((apk_version, url))

        return versions_info
