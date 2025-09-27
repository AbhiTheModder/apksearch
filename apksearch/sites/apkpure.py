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
        self.cdn_url = "https://d.cdnpure.com/b/APK/"
        self.cdn_version = "?version="
        self.search_url = self.base_url + "/search?q="
        self.api_url = "https://tapi.pureapk.com/v3/get_app_his_version"
        self.api_headers = {
            "User-Agent-WebView": "Mozilla/5.0 (Linux; Android 13; Pixel 5 Build/TQ3A.230901.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/132.0.6834.122 Safari/537.36",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 13; Pixel 5 Build/TQ3A.230901.001); APKPure/3.20.34 (Aegon)",
            "Ual-Access-Businessid": "projecta",
            "Ual-Access-ProjectA": """{"device_info":{"abis":["x86_64","arm64-v8a","x86","armeabi-v7a","armeabi"],"android_id":"50f838123d9a9c94","brand":"google","country":"United States","country_code":"US","imei":"","language":"en-US","manufacturer":"Google","mode":"Pixel 5","os_ver":"33","os_ver_name":"13","platform":1,"product":"redfin","screen_height":1080,"screen_width":1920},"host_app_info":{"build_no":"468","channel":"","md5":"6756e53158d6f6c013650a40d8f1147b","pkg_name":"com.apkpure.aegon","sdk_ver":"3.20.34","version_code":3203427,"version_name":"3.20.34"}}""",
            "Ual-Access-ExtInfo": """{"ext_info":"{\"gaid\":\"\",\"oaid\":\"\"}","lbs_info":{"accuracy":0.0,"city":"","city_code":0,"country":"","country_code":"","district":"","latitude":0.0,"longitude":0.0,"province":"","street":""}}""",
            "Ual-Access-Sequence": "",
            "Ual-Access-Nonce": "21448252",
            "Ual-Access-Timestamp": "1738560597165",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
        }
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

    def _api_search(self) -> None | tuple[str, list[tuple[str, str]]]:
        """
        Attempts to fetch app information using API.

        Returns:
            None: If API request fails or no data found
            tuple[str, list[tuple[str, str]]]: App title and list of (version, download_url) tuples
        """
        try:
            params = {"package_name": self.pkg_name, "hl": "en"}
            response = self.session.get(
                self.api_url, headers=self.api_headers, params=params
            )
            data = response.json()

            if not data.get("version_list"):
                return None

            versions_info = []
            title = None

            for version in data["version_list"]:
                version_name = version["version_name"]
                if not title:
                    title = version["title"]
                if version.get("asset", {}).get("urls"):
                    download_url = version["asset"]["urls"][0]
                    versions_info.append((version_name, download_url))

            return (title, versions_info) if title and versions_info else None

        except Exception:
            return None

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
        # If site search resulted 0 results, try cdn link
        # https://github.com/AbhiTheModder/apksearch/issues/2
        url = self.cdn_url + pkg_name + self.cdn_version + "latest"
        response: requests.Response = self.session.get(
            url, headers=self.headers, allow_redirects=False
        )
        try:
            location = response.headers.get("Location")
        except AttributeError:
            location = None
        if location:
            if location == "https://apkpure.com":
                return None
            response: requests.Response = self.session.head(
                location, allow_redirects=False
            )
            try:
                content = response.headers.get("Content-Disposition")
            except AttributeError:
                return None
            if content:
                apk_title = content.split("filename=")[1].strip('"').split("_")[0]
                return apk_title, location

        api_result = self._api_search()
        if api_result:
            title, versions = api_result
            if versions:
                return title, versions[0][1]
    
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
        api_result = self._api_search()
        if api_result:
            return api_result[1]

        versions_info = []
        if apk_link.startswith(self.base_url):
            url = apk_link + "/versions"
            response: requests.Response = self.session.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, "html.parser")
            versions_list = soup.find("ul", {"class": "version-list"})

            if versions_list:
                versions = versions_list.find_all(
                    "li", {"class": re.compile("^version dt-version-item.*")}
                )
                for ver in versions:
                    version_icon = ver.find("a", {"class": "dt-version-icon"})
                    version_info = ver.find("div", {"class": "version-info"})
                    if version_icon and version_info:
                        version_number = version_info.find(
                            "span", {"class": "name one-line"}
                        ).text
                        download_url = self.base_url + version_icon["href"]
                        versions_info.append((version_number, download_url))
        return versions_info
