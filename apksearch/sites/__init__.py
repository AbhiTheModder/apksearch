try:
    from curl_cffi import requests

    curl = True
except ImportError:
    import requests

    curl = False

__all__ = ["requests", "curl"]
