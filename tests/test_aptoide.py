from apksearch.sites.aptoide import Aptoide


def test_search_apk():
    query = "com.roblox.client"
    aptoide = Aptoide(query)
    result = aptoide.search_apk()

    assert result is not None, "No APK found for the query."
    assert isinstance(result, tuple), "Result should be a tuple."
    assert len(result) == 2, "Tuple should contain two elements."
    assert isinstance(result[0], str), "First element of the tuple should be a string."
    assert isinstance(result[1], str), "Second element of the tuple should be a string."


def test_find_versions():
    query = "com.roblox.client"
    aptoide = Aptoide(query)
    result = aptoide.search_apk()

    if result:
        apk_link = result[1]
        versions = aptoide.find_versions(apk_link)

        assert isinstance(versions, list), "Versions should be a list."
        assert len(versions) > 0, "No versions found."
        assert all(
            isinstance(version, str) for version in versions
        ), "Each version should be a string."
