# apksearch

`apksearch` is a Python library designed to search for APK files on different APK websites, such as APKPure and APKMirror. It allows users to find APKs, check for available versions, and retrieve download links.

**The Inspiration:**
There were countless occasions when I needed a specific APK for a package name, only to find it unavailable on popular platforms. This led to the tedious task of manually visiting multiple websites and searching one by one.

# Features

- **Search APKs:** The library provides methods to search for APKs using package names.
- **Retrieve APK Versions and Download Links:** It can fetch available versions and their download links for a given APK from APKPure and APKMirror.
- **Command-Line Interface:** A CLI is available for users to search for APKs directly from the command line.

## Installation

To install the `apksearch` library, use the following command:

```sh
pip install git+https://github.com/AbhiTheModder/apksearch.git
```

OR, through pip:

```sh
pip install apksearch
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

#### `APKPure`

- **`__init__(self, pkg_name: str)`**: Initializes with the package name.
- **`search_apk(self) -> None | tuple[str, str]`**: Searches for the APK on APKPure and returns the title and link if found.
- **`find_versions(self, apk_link: str) -> list[tuple[str, str]]`**: Finds and returns a list of versions and their download links for the given APK link.

#### `APKMirror`

- **`__init__(self, pkg_name: str)`**: Initializes with the package name.
- **`search_apk(self) -> None | tuple[str, str]`**: Searches for the APK on APKMirror and returns the title and link if found.
- **`find_version(self, apk_link: str, version: str) -> str`**: Finds and returns the download link for the given APK link and version.

#### `AppTeka`

- **`__init__(self, pkg_name: str)`**: Initializes with the package name.
- **`search_apk(self, version: str = None) -> None | tuple[str, str]`**: Searches for the APK on AppTeka and returns the title and link if found. If a version is provided, it checks if that version is available and returns the corresponding download link, None otherwise. If no version is provided, it returns the link for the latest version available.

### Testing

The project includes tests for the `sites` classes. To run the tests, use the following command:

```sh
pytest
```

## TODO

- [ ] Add more websites to search for APKs.

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/AbhiTheModder/apksearch/blob/main/LICENSE) file for more details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on [GitHub](https://github.com/AbhiTheModder/apksearch).
