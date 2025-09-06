<h1 align="center">apksearch</h1>

`apksearch` is a Python library designed to search for APK files on different APK websites, such as APKPure and APKMirror. It allows users to find APKs, check for available versions, and retrieve download links.

**The Inspiration:**
There were countless occasions when I needed a specific APK for a package name, only to find it unavailable on popular platforms. This led to the tedious task of manually visiting multiple websites and searching one by one.
<details>
    <summary>screenshot</summary>
    <p align="center">
        <img width="500" src="https://github.com/user-attachments/assets/cd54eaeb-a56b-40b3-835f-b48b1e7772f3"></img><br>
        As you can see, Roblox version <code>2.647.716</code> is not available on APKPure and APKCombo, this helped me avoid going through these sites.
    </p>
</details>

**P.S:** If you're looking for an APK downloader, I highly recommend using [apkeep](https://github.com/EFForg/apkeep).

# Features

- **Search APKs:** The library provides methods to search for APKs using package names.
- **Retrieve APK Versions and Download Links:** It can fetch available versions and their download links for a given APK from various websites.
- **Command-Line Interface:** A CLI is available for users to search for APKs directly from the command line.

## Supported Websites

- [APKPure](https://apkpure.net/)
- [APKMirror](https://www.apkmirror.com/)
- [Aptoide](https://en.aptoide.com/)
- [APKCombo](https://apkcombo.app/)
- [APKFab](https://apkfab.com/)
- [Appteka](https://appteka.store/)
- [APKAD](https://apk.ad/)

> [!NOTE]
> **For site owners:**
> If you're the owner of a website that's not listed here and you'd like to add support for it, feel free to open an issue or submit a pull request. I'm open to adding more websites to the library.
> I respect the _value of user engagement and the revenue_ it generates for your site. To honor this, I have deliberately avoided including a download feature in the library, ensuring users will still need to visit your website, maintaining its traffic and engagement.
> Additionally, I kindly ask that you **refrain from enforcing strict blocking measures**, such as aggressive Cloudflare rules, as the library is designed to work collaboratively rather than disruptively. Thank you!

## Installation

To install/upgrade the `apksearch` library, use the following command:

```sh
pip install -U git+https://github.com/AbhiTheModder/apksearch.git
```

OR, through pip:

```sh
pip install -U apksearch
```

OR, if you've cloned the repository locally you can do so via:

```sh
pip install -U . # or path to the local clone
```

## Usage

### Command-Line Interface

To use the CLI, run the following command:

```sh
apksearch <package_name> [--version <version>]
```

Example:

```sh
apksearch com.roblox.client --version 2.652.765
```

### Library Usage

You can also use the library programmatically in your Python code:

```python
from apksearch import APKPure, APKMirror

# Searching on APKPure
apkpure = APKPure("com.roblox.client")
result = apkpure.search_apk()
if result:
    title, link = result
    print(f"Found on APKPure: {title} - {link}")

# Searching on APKMirror
apkmirror = APKMirror("com.roblox.client")
result = apkmirror.search_apk()
if result:
    title, link = result
    print(f"Found on APKMirror: {title} - {link}")
```

### Classes and Methods

#### `APKPure` | `APKCombo` | `APKFab`

- **`__init__(self, pkg_name: str)`**: Initializes with the package name.
- **`search_apk(self) -> None | tuple[str, str]`**: Searches for the APK and returns the title and link if found.
- **`find_versions(self, apk_link: str) -> list[tuple[str, str]]`**: Finds and returns a list of versions and their download links for the given APK link.

#### `APKMirror`

- **`__init__(self, pkg_name: str)`**: Initializes with the package name.
- **`search_apk(self) -> None | tuple[str, str]`**: Searches for the APK and returns the title and link if found.
- **`find_version(self, apk_link: str, version: str) -> str`**: Finds and returns the download link for the given APK link and version.

#### `AppTeka` | `APKAD`

- **`__init__(self, pkg_name: str)`**: Initializes with the package name.
- **`search_apk(self, version: str = None) -> None | tuple[str, str]`**: Searches for the APK and returns the title and link if found. If a version is provided, it checks if that version is available and returns the corresponding download link, None otherwise. If no version is provided, it returns the link for the latest version available.

#### `Aptoide`

- **`__init__(self, pkg_name: str)`**: Initializes with the package name.
- **`search_apk(self) -> None | tuple[str, str]`**: Searches for the APK and returns the title and link if found.
- **`find_versions(self, apk_link: str, version: str) -> list[str]`**: Finds and returns the download links for the given APK link and versions list.

### Testing

The project includes tests for the `sites` classes. To run the tests, use the following command:

```sh
pytest
```

## TODO

- [ ] Add more websites to search for APKs.

## Acknowledgements

- [APKUpdater](https://github.com/rumboalla/apkupdater) for APKMirror API.
~~- [apkeep](https://github.com/EFForg/apkeep) for APKPure API.~~ (not used anymore)

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/AbhiTheModder/apksearch/blob/main/LICENSE) file for more details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on [GitHub](https://github.com/AbhiTheModder/apksearch).

If you find this project helpful, please consider giving it a ⭐. Your support is greatly appreciated!
