try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse
