from apksearch.sites.appteka import AppTeka


def test_search_apk():
    query = "com.roblox.client"
    appteka = AppTeka(query)
    result = appteka.search_apk()

    assert result is not None, "No APK found for the query."
    assert isinstance(result, tuple), "Result should be a tuple."
    assert len(result) == 2, "Tuple should contain two elements."
    assert isinstance(result[0], str), "First element of the tuple should be a string."
    assert isinstance(result[1], str), "Second element of the tuple should be a string."


def test_search_apk_version():
    from bs4 import BeautifulSoup

    query = "com.roblox.client"
    version = "2.647.716"
    appteka = AppTeka(query)
    result = appteka.search_apk(version)
    if not result or not result[1]:
        base_result = appteka.search_apk()
        if base_result and base_result[1]:
            resp = appteka.session.get(base_result[1], headers=appteka.headers)
            soup = BeautifulSoup(resp.text, "html.parser")
            for dt in soup.find_all("dt"):
                if dt.text.strip().lower() == "version":
                    dd = dt.find_next_sibling("dd")
                    if dd:
                        version = dd.text.strip().split()[0]
                        result = appteka.search_apk(version)
                        break

    assert result is not None, "No APK found for the query."
    assert isinstance(result, tuple), "Result should be a tuple."
    assert len(result) == 2, "Tuple should contain two elements."
    assert isinstance(result[0], str), "First element of the tuple should be a string."
    assert isinstance(result[1], str), "Second element of the tuple should be a string."


def test_search_apk_not_version():
    query = "com.roblox.client"
    version = "nonexistent"
    appteka = AppTeka(query)
    result = appteka.search_apk(version)

    assert result is not None, "No APK found for the query."
    assert isinstance(result, tuple), "Result should be a tuple."
    assert len(result) == 2, "Tuple should contain two elements."
    assert isinstance(result[0], str), "First element of the tuple should be a string."
    assert result[1] == None, "Second element of the tuple should be None."
