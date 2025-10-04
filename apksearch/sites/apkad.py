import base64
import json

from bs4 import BeautifulSoup

from apksearch.sites import requests


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
        self.base_url = "https://apkdownloader.pages.dev"
        self.api_url = "https://api.mi9.com"
        self.token_url = "https://token.mi9.com/"
        self.search_url = self.api_url + "/get"
        self.headers = {
            "accept": "text/event-stream",
            "accept-language": "en-US,en;q=0.9,en-IN;q=0.8",
            "cache-control": "no-cache",
            "dnt": "1",
            "origin": "https://apkdownloader.pages.dev",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "referer": "https://apkdownloader.pages.dev/",
            "sec-ch-ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        }
        self.session = requests.Session()

    def get_token(self) -> tuple[str, int] | None:
        """
        Retrieves a token from the token endpoint.

        Returns:
            tuple[str, int]: A tuple containing the token and timestamp if successful.
            None: If the token retrieval fails.
        """
        data = {
            "package": self.pkg_name,
            "device": "phone",
            "arch": "arm64-v8a",
            "vc": "",
            "device_id": "",
            "sdk": "default",
        }
        response = self.session.post(self.token_url, headers=self.headers, json=data)
        if response.status_code == 200:
            token_data = response.json()
            if token_data.get("success"):
                return token_data.get("token"), token_data.get("timestamp")
        return None

    def search_apk(self) -> None | tuple[str, list[tuple[str, str]]]:
        token_tuple = self.get_token()
        if not token_tuple:
            return None

        token, ts = token_tuple
        data_json = json.dumps(
            {
                "hl": "en",
                "package": self.pkg_name,
                "device": "phone",
                "arch": "arm64-v8a",
                "vc": "",
                "device_id": "",
                "sdk": "default",
                "timestamp": ts,
            },
            separators=(",", ":"),
        )

        data_b64 = base64.b64encode(data_json.encode("utf-8")).decode("utf-8")

        params = {"token": token, "data": data_b64}

        response = self.session.get(
            self.search_url, headers=self.headers, params=params, stream=True
        )

        stream_response = None
        for line in response.iter_lines():
            if not line:
                continue
            line_response = line.decode("utf-8")
            if line_response.startswith("data: "):
                payload = line_response[6:]
                try:
                    j = json.loads(payload)
                    if j.get("progress") == 100 and j.get("html"):
                        stream_response = j
                        break
                except json.JSONDecodeError:
                    continue

        if stream_response:
            html_body = stream_response["html"]
            soup = BeautifulSoup(html_body, "html.parser")
            if not soup:
                return None

            title = soup.find("li", {"class": "_title"})
            title = title.text.strip() if title else self.pkg_name

            apk_files_div = soup.find("div", {"id": "apkslist"})
            if not apk_files_div:
                return None

            apk_links: list[tuple[str, str]] = []
            for a in apk_files_div.find_all("a", href=True):
                link = a["href"].strip()
                filename = a.find("span", {"class": "der_name"})
                filename = filename.text.strip() if filename else link.split("/")[-1]
                apk_links.append((filename, link))

            return title, apk_links

        return None
