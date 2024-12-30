from apksearch.sites.apkpure import APKPure


def test_search_apk():
    query = "com.roblox.client"
    apkpure = APKPure(query)
    result = apkpure.search_apk()

    assert result is not None, "No APK found for the query."
    assert isinstance(result, tuple), "Result should be a tuple."
    assert len(result) == 2, "Tuple should contain two elements."
    assert isinstance(result[0], str), "First element of the tuple should be a string."
    assert isinstance(result[1], str), "Second element of the tuple should be a string."


def test_find_versions():
    query = "com.roblox.client"
    apkpure = APKPure(query)
    result = apkpure.search_apk()

    if result:
        apk_link = result[1]
        versions = apkpure.find_versions(apk_link)

        assert isinstance(versions, list), "Versions should be a list."
        assert len(versions) > 0, "No versions found."
        assert all(
            isinstance(version, tuple) for version in versions
        ), "Each version should be a tuple."
        assert all(
            len(version) == 2 for version in versions
        ), "Each version tuple should contain two elements."
        assert all(
            isinstance(version[0], str) for version in versions
        ), "First element of each version tuple should be a string."
        assert all(
            isinstance(version[1], str) for version in versions
        ), "Second element of each version tuple should be a string."
