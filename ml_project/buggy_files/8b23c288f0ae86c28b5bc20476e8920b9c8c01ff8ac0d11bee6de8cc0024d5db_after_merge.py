def is_url(url):
    if url:
        p = urlparse.urlparse(url)
        return p.netloc != "" or p.scheme == "file"