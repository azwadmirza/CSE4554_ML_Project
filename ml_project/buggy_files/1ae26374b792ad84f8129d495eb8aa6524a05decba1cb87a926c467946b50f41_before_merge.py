def match_url(url):
    try:
        query_url = urlparse(url)
        return all([query_url.scheme, query_url.netloc, query_url.path])
    except Exception:
        return False