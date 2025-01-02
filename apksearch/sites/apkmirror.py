import requests


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

    def find_version(self, apk_link: str, version: str) -> str:
        """
        Finds and returns the download link for the given APK link and version.

        Parameters:
            apk_link (str): The link to the APK on the APKMirror website.
            version (str): The version number of the APK to find.

        Returns:
            str: The download link for the specified version of the APK.
        """
        name = apk_link.split("/")[-2]
        version = version.replace(".", "-")
        url = apk_link + name + "-" + version + "-release"
        response = self.session.get(url, headers=self.headers)
        if response.status_code == 404:
            return None
        return url
