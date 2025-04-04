import re
from bs4 import BeautifulSoup
import requests


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
        self.search_url = self.base_url + "/list/?query="
        self.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9,en-IN;q=0.8",
            "cache-control": "no-cache",
            "dnt": "1",
            "connection": "keep-alive",
            "pragma": "no-cache",
            "referer": "https://appteka.store/list/",
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

    def search_apk(self, version: str = None) -> None | tuple[str, str]:
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
        search_results = soup.find("div", {"class": "list-group"})
        if search_results:
            apk_items = search_results.find_all(
                "a",
                {"class": "list-group-item list-group-item-action d-flex gap-3 py-3"},
            )
            if apk_items:
                for apk_item in apk_items:
                    apk_link = self.base_url + apk_item["href"]
                    apk_title = apk_item.find(
                        "strong", {"class": "text-gray-dark"}
                    ).text.strip()
                    # Unfortunately, AppTeka does not provide a package name in the search results.
                    # So, we can't compare the package names here.
                    # We can instead do a workaround by doing a request to the apk_link and check the package name there.
                    new_url = apk_link
                    new_response: requests.Response = self.session.get(
                        new_url, headers=self.headers
                    )
                    new_soup = BeautifulSoup(new_response.text, "html.parser")
                    rows = new_soup.find_all("dl", {"class": "row"})
                    for row in rows:
                        dt_tags = row.find_all("dt")
                        dd_tags = row.find_all("dd")
                        for dt, dd in zip(dt_tags, dd_tags):
                            if dt.text.strip() == "Package":
                                package_name = dd.text.strip()
                                if package_name == pkg_name:
                                    # Appteka also stores the list of all the versions on same page
                                    # So, if the version param is given then we can check if the version is available or not
                                    if version:
                                        version_modal = new_soup.find(
                                            "div", {"id": "versionsModal"}
                                        )
                                        if version_modal:
                                            version_links = version_modal.find_all(
                                                "a",
                                                {
                                                    "class": re.compile(
                                                        "^list-group-item list-group-item-action*"
                                                    )
                                                },
                                            )
                                            for link in version_links:
                                                version_text = (
                                                    link.find("p", {"class": "m-1"})
                                                    .text.strip()
                                                    .split("\xa0")[0]
                                                )
                                                if version_text == version:
                                                    apk_link = (
                                                        self.base_url + link["href"]
                                                    )
                                                    return apk_title, apk_link
                                            return apk_title, None
                                    else:
                                        return apk_title, apk_link

        return None
