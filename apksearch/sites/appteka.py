import re
import urllib.parse

from bs4 import BeautifulSoup

from apksearch.sites import requests


class AppTeka:
    """
    This class provides methods to search for an APK on AppTeka based on package name,
    and to find available versions and their download links for a given APK link.

    Parameters:
        pkg_name (str): The package name of the APK to search for.

    Attributes:
        pkg_name (str): The package name of the APK to search for.
        base_url (str): The base URL of the AppTeka website.
        search_url (str): The URL used to search for APKs on AppTeka.
        headers (dict): The headers used for making HTTP requests.
        session (requests.Session): The session object used for making HTTP requests.

    Methods:
        search_apk(version) -> None | tuple[str, str]:
            Searches for an APK on AppTeka based on the package name and version.
            Returns a tuple containing the APK name and download link if found, otherwise None.
    """

    def __init__(self, pkg_name: str):
        self.pkg_name = pkg_name
        self.base_url = "https://appteka.store"
        self.search_url = self.base_url + "/search?q="
        self.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9,en-IN;q=0.8",
            "cache-control": "no-cache",
            "dnt": "1",
            "connection": "keep-alive",
            "pragma": "no-cache",
            "referer": "https://appteka.store/",
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

    def search_apk(self, version: str | None = None) -> None | tuple[str, str | None]:
        """
        Searches for the APK on AppTeka and returns the title and link if found.

        Parameters:
           version (str, optional): The version of the APK to search for.

        Returns:
            None: If no matching APK is found.
            tuple[str, str]: A tuple containing the title and link of the matching APK if found.
        """
        pkg_name = self.pkg_name
        url = self.search_url + pkg_name
        response: requests.Response = self.session.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")

        seen_links = set()
        for a in soup.find_all("a", href=True):
            href = a["href"].split("?")[0]
            if href.startswith("/apps/") and href not in seen_links:
                seen_links.add(href)
                apk_link = urllib.parse.urljoin(self.base_url, href)
                new_response: requests.Response = self.session.get(
                    apk_link, headers=self.headers
                )
                new_soup = BeautifulSoup(new_response.text, "html.parser")

                package_name = None
                for dt in new_soup.find_all("dt"):
                    if dt.text.strip().lower() == "package":
                        dd = dt.find_next_sibling("dd")
                        if dd:
                            package_name = dd.text.strip()
                            break

                if package_name == pkg_name:
                    h1 = new_soup.find("h1")
                    apk_title = h1.text.strip() if h1 else pkg_name

                    if version:
                        # Check current version on page
                        for dt in new_soup.find_all("dt"):
                            if dt.text.strip().lower() == "version":
                                dd = dt.find_next_sibling("dd")
                                if dd and dd.text.strip().split()[0] == version:
                                    return apk_title, apk_link

                        # Check HTML version links in other versions section
                        for va in new_soup.find_all("a", href=True):
                            if va["href"].startswith("/apps/") and "v" in va.text:
                                ver_text = va.text.strip().lstrip("v").strip()
                                if ver_text == version:
                                    return (
                                        apk_title,
                                        urllib.parse.urljoin(
                                            self.base_url, va["href"].split("?")[0]
                                        ),
                                    )

                        # Check versions embedded in page JSON script
                        matches = re.findall(
                            r'app_id\\*":\\*"([^\\"]+)\\*",\\*"ver_name\\*":\\*"([^\\"]+)\\*"',
                            new_response.text,
                        )
                        for app_id, ver_name in matches:
                            if ver_name == version:
                                return apk_title, f"{self.base_url}/apps/{app_id}"

                        return apk_title, None
                    else:
                        return apk_title, apk_link

        return None
