import re
from bs4 import BeautifulSoup
import requests


class Aptoide:
    """
    This class provides methods to search for an APK on Aptoide based on package name,
    and to find available versions and their download links for a given APK link.

    Parameters:
        pkg_name (str): The package name of the APK to search for.

    Attributes:
        pkg_name (str): The package name of the APK to search for.
        api_url (str): The base URL for the Aptoide API.
        search_url (str): The URL used to search for APKs on Aptoide.
        headers (dict): The headers used for making HTTP requests.
        session (requests.Session): The session object used for making HTTP requests.

    Methods:
        search_apk() -> None | tuple[str, str]:
            Searches for the APK on Aptoide and returns the title and link if found.

        find_versions(apk_link: str) -> list[str | None]:
            Finds and returns a list of versions for the given APK link.
    """

    def __init__(self, pkg_name: str):
        self.pkg_name = pkg_name
        self.api_url = "https://ws75.aptoide.com/api/7"
        self.search_url = f"{self.api_url}/apps/search"
        self.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9,en-IN;q=0.8",
            "cache-control": "no-cache",
            "dnt": "1",
            "pragma": "no-cache",
            "priority": "u=0, i",
            "referer": "https://en.aptoide.com/",
            "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Microsoft Edge";v="132"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        }
        self.params = {
            "cdn": "web",
            "q": "bXlDUFU9YXJtNjQtdjhhLGFybWVhYmktdjdhLGFybWVhYmkmbGVhbmJhY2s9MA",
            "aab": "1",
            "mature": "false",
            "language": "en_US",
            "country": "US",
            "not_apk_tags": "",
            "query": self.pkg_name,
            "limit": "1",
            "offset": "0",
            "origin": "SITE",
            "store_name": "aptoide-web",
        }
        self.session = requests.Session()

    def search_apk(self) -> None | tuple[str, str]:
        """
        Searches for the APK on Aptoide and returns the title and link if found.

        Returns:
            None: If no matching APK is found.
            tuple[str, str]: A tuple containing the title and link of the matching APK if found.
        """
        pkg_name = self.pkg_name
        url = self.search_url
        response: requests.Response = self.session.get(
            url, headers=self.headers, params=self.params
        )
        data = response.json()
        if data and data["info"]["status"] == "OK":
            lis = data["datalist"]["list"]
            if lis:
                package = data["datalist"]["list"][0]["package"]
                apk_title = data["datalist"]["list"][0]["name"]
                if package == pkg_name:
                    app_id: int = data["datalist"]["list"][0]["id"]
                    meta_url = self.api_url + f"/app/getMeta?app_id={app_id}"
                    meta_response: requests.Response = self.session.get(
                        meta_url, headers=self.headers
                    )
                    meta_data = meta_response.json()
                    if meta_data and meta_data["info"]["status"] == "OK":
                        url = meta_data["data"]["urls"]["w"].split("?")[0]
                        return apk_title, url
        return None

    def find_versions(self, apk_link: str) -> list[str | None]:
        """
        Finds and returns a list of versions for the given APK link.

        Parameters:
            apk_link (str): The link to the APK on the Aptoide website.

        Returns:
           list[str | None]: A list of version strings for the given APK link.
        """
        versions_info = []

        url = apk_link + "/versions"
        response: requests.Response = self.session.get(url, headers=self.headers)
        soup = BeautifulSoup(response.content, "html.parser")
        version_spans = soup.find_all("span", string=re.compile(r"^\d+\.\d+\.\d+$"))
        for span in version_spans:
            version = span.text
            versions_info.append(version)

        return versions_info
