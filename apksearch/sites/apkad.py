import json
from bs4 import BeautifulSoup
import requests


class APKad:
    """
    This class provides methods to search for an APK on APKAD based on package name,
    and to find available versions and their download links for a given APK link.

    Parameters:
        pkg_name (str): The package name of the APK to search for.

    Attributes:
        pkg_name (str): The package name of the APK to search for.
        base_url (str): The base URL of the APKAD website.
        search_url (str): The URL used to search for APKs on APKAD.
        headers (dict): The headers used for making HTTP requests.
        session (requests.Session): The session object used for making HTTP requests.

    Methods:
        search_apk() -> None | tuple[str, str]:
            Searches for the APK on APKAD and returns the title and link if found.
    """

    def __init__(self, pkg_name: str):
        self.pkg_name = pkg_name
        self.base_url = "https://downloader.apk.ad"
        self.api_url = "https://api.apk.ad"
        self.search_url = (
            self.api_url
            + f"/get?hl=en&package={self.pkg_name}&device=phone&arch=arm64-v8a&vc=&device_id="
        )
        self.headers = {
            "accept": "text/event-stream",
            "accept-language": "en-US,en;q=0.9,en-IN;q=0.8",
            "cache-control": "no-cache",
            "dnt": "1",
            "origin": "https://downloader.apk.ad",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "referer": "https://downloader.apk.ad/",
            "sec-ch-ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        }
        self.session = requests.Session()

    def search_apk(self) -> None | tuple[str, str]:
        """
        Searches for the APK on APKAD and returns the title and link if found.

        Returns:
            None: If no matching APK is found.
            tuple[str, str]: A tuple containing the title and link of the matching APK if found.
        """
        url = self.search_url
        response = self.session.get(url, headers=self.headers, stream=True)
        stream_response = ""
        for line in response.iter_lines():
            if line:
                line_response = line.decode("utf-8")
                if '"progress":100' in line_response:
                    line_response = line_response[6:]
                    stream_response += line_response
                    break
        if stream_response:
            data = json.loads(stream_response)
            html_body = data["html"]
            soup = BeautifulSoup(html_body, "html.parser")
            if not soup:
                return None
            title = soup.find("li", {"class": "_title"})
            if title:
                title = title.text.strip()
                button = soup.find(
                    "button", {"onclick": True, "id": "downloadButtonapk"}
                )["onclick"]
                if button:
                    zip_args = [
                        arg.strip("'")
                        for arg in button.split("zip(")[1].split(")")[0].split(",")
                    ]
                    h = zip_args[0]  # hash
                    p = zip_args[-1]  # type
                    token = zip_args[1]  # token
                    ip = zip_args[2]  # ip
                    google_id = zip_args[3]  # package_name
                    t = zip_args[4]  # time
                    apk_url = f"https://zip.apk.ad/compress?h={h}&p={p}&token={token}&ip={ip}&google_id={google_id}&t={t}"
                    apk_url_response = self.session.get(
                        url=apk_url, headers=self.headers, stream=True
                    )
                    for line in apk_url_response.iter_lines():
                        if line:
                            line_response = line.decode("utf-8")
                            if "File is ready for download." in line_response:
                                line_response = json.loads(line_response)
                                line_html = line_response["html"]
                                line_soup = BeautifulSoup(line_html, "html.parser")
                                download_link = line_soup.find("a")["href"]
                                if download_link.endswith("\n"):
                                    download_link = download_link[:-1]
                                return title, download_link
        return None
