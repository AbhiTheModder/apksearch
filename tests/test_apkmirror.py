from apksearch import APKMirror


def test_search_apk():
    query = "com.roblox.client"
    apkmirror = APKMirror(query)
    result = apkmirror.search_apk()

    assert result is not None, "No APK found for the query."
    assert isinstance(result, tuple), "Result should be a tuple."
    assert len(result) == 2, "Tuple should contain two elements."
    assert isinstance(result[0], str), "First element of the tuple should be a string."
    assert isinstance(result[1], str), "Second element of the tuple should be a string."


def test_find_versions_nfound():
    query = "com.roblox.client"
    version = "1.2.3"
    apkmirror = APKMirror(query)
    result = apkmirror.search_apk()

    if result:
        apk_link = result[1]

        assert apk_link.startswith("https://"), "APK link should be a valid URL."

        download_link = apkmirror.find_version(apk_link, version)

        assert download_link is None, "Version not found."


def test_find_versions_found():
    query = "com.roblox.client"
    version = "2.652.765"
    apkmirror = APKMirror(query)
    result = apkmirror.search_apk()

    if result:
        apk_link = result[1]
        download_link = apkmirror.find_version(apk_link, version)

        assert isinstance(download_link, str), "Download link should be a string."
        assert download_link.startswith(
            "https://"
        ), "Download link should be a valid URL."
