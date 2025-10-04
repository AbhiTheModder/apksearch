try:
    from curl_cffi import requests
except ImportError:
    import requests

__all__ = [requests]
