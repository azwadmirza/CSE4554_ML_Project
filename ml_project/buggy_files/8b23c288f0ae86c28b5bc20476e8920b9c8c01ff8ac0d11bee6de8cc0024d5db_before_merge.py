def is_url(url):
    return url and urlparse.urlparse(url).scheme != ""