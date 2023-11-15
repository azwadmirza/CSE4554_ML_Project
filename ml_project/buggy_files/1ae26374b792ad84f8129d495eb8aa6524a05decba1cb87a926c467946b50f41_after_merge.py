def match_url(url) -> bool:
    try:
        query_url = urlparse(url)
        return all([query_url.scheme, query_url.netloc, query_url.path])
    except Exception:
        return False