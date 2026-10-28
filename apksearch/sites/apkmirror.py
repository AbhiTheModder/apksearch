import re

from apksearch.sites import requests


class APKMirror:
    """
    This class provides methods to search for an APK on APKMirror based on package name,
    and to find available versions and their download links for a given APK link.

    Parameters:
        pkg_name (str): The package name of the APK to search for.

    Attributes:
        pkg_name (str): The package name of the APK to search for.
        base_url (str): The base URL of the APKMirror website.
        api_url (str): The base URL for the APKMirror API.
        headers (dict): The headers used for making HTTP requests.
        session (requests.Session): The session object used for making HTTP requests.

    Methods:
        search_apk() -> None | tuple[str, str]:
            Searches for the APK on APKMirror and returns the title and link if found.

        find_versions(apk_link: str) -> list[tuple[str, str]]:
            Finds and returns a list of versions and their download links for the given APK link.
    """

    def __init__(self, pkg_name: str):
        self.pkg_name = pkg_name
        self.base_url = "https://www.apkmirror.com"
        self.api_url = self.base_url + "/wp-json/apkm/v1"
        # https://github.com/rumboalla/apkupdater/blob/3.x/app/src/main/kotlin/com/apkupdater/service/ApkMirrorService.kt
        self.headers = {
            "User-Agent": "APKUpdater-v3.0.3",
            "Authorization": "Basic YXBpLWFwa3VwZGF0ZXI6cm01cmNmcnVVakt5MDRzTXB5TVBKWFc4",
            "Content-Type": "application/json",
        }
        self.session = requests.Session()

    def search_apk(self) -> None | tuple[str, str]:
        """
        Searches for the APK on APKMirror and returns the title and link if found.

        Returns:
            None: If no matching APK is found.
            tuple[str, str]: A tuple containing the title and link of the matching APK if found.
        """
        pkg_name = self.pkg_name
        url = self.api_url + "/app_exists"
        json = {"pnames": pkg_name}
        response: requests.Response = self.session.post(
            url, json=json, headers=self.headers
        )
        result = response.json()["data"][0]
        if result and result["exists"]:
            pname = result["pname"]
            if pname == pkg_name:
                title = result["app"]["name"]
                apk_link = self.base_url + result["app"]["link"]
                return title, apk_link
        return None

    @staticmethod
    def _parse_version_tuple(v: str) -> tuple[int, ...]:
        nums = re.findall(r"\d+", v)
        return tuple(int(x) for x in nums) if nums else (0,)

    def _find_version_in_feed(self, apk_link: str, version: str) -> str | None:
        """
        Searches for a version across the app's RSS feed pages using APKUpdater authentication.
        """
        target_tuple = self._parse_version_tuple(version)
        feed_base = apk_link.rstrip("/") + "/feed/"

        response = self.session.get(feed_base, headers=self.headers)
        if response.status_code != 200:
            return None

        def extract_items(xml_text: str):
            res = []
            for item in re.findall(r"<item>(.*?)</item>", xml_text, re.DOTALL):
                t_match = re.search(r"<title>(.*?)</title>", item)
                l_match = re.search(r"<link>(.*?)</link>", item)
                if t_match and l_match:
                    item_title = t_match.group(1).strip()
                    item_link = l_match.group(1).strip()
                    v_match = re.search(r"\b(\d+\.\d+[\.\d]*)\b", item_title)
                    v_tuple = (
                        self._parse_version_tuple(v_match.group(1))
                        if v_match
                        else None
                    )
                    res.append(
                        (
                            item_title,
                            item_link,
                            v_match.group(1) if v_match else "",
                            v_tuple,
                        )
                    )
            return res

        items = extract_items(response.text)
        if not items:
            return None

        for item_title, item_link, v_str, v_tuple in items:
            if v_str == version or version in item_title:
                return item_link

        first_ver = items[0][3]
        if first_ver and target_tuple > first_ver:
            return None

        low = 2
        high = 35
        while low <= high:
            mid = (low + high) // 2
            r_mid = self.session.get(f"{feed_base}?paged={mid}", headers=self.headers)
            if r_mid.status_code == 404:
                high = mid - 1
                continue
            if r_mid.status_code != 200:
                break

            mid_items = extract_items(r_mid.text)
            if not mid_items:
                high = mid - 1
                continue

            for item_title, item_link, v_str, v_tuple in mid_items:
                if v_str == version or version in item_title:
                    return item_link

            mid_first = mid_items[0][3]
            mid_last = mid_items[-1][3]
            if not mid_first or not mid_last:
                break

            if target_tuple > mid_first:
                high = mid - 1
            elif target_tuple < mid_last:
                low = mid + 1
            else:
                return None

        return None

    def find_version(self, apk_link: str, version: str, title: str) -> str | None:
        """
        Finds and returns the download link for the given APK link and version.

        Parameters:
            apk_link (str): The link to the APK on the APKMirror website.
            version (str): The version number of the APK to find.
            title (str): The title of the APK.

        Returns:
            str: The download link for the specified version of the APK.
        """
        name = re.sub(r"[(),]", "", title).lower().replace(" ", "-")
        name = re.sub(r"-+", "-", name)
        version_slug = version.replace(".", "-")
        url = apk_link + name + "-" + version_slug + "-release"
        response = self.session.get(url, headers=self.headers)
        if response.status_code == 200:
            return url
        if response.status_code == 404:
            return None
        # On Cloudflare challenge (403), check the app's RSS feed
        feed_link = self._find_version_in_feed(apk_link, version)
        if feed_link:
            return feed_link
        return None
