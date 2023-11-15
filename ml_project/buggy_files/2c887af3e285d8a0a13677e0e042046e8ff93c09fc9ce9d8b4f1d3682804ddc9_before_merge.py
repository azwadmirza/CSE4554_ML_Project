def _build_sqlite_uri(filename, options):
    # Convert filename to uri according to https://www.sqlite.org/uri.html, 3.1
    uri_path = filename.replace("?", "%3f").replace("#", "%23")
    if os.name == "nt":
        uri_path = uri_path.replace("\\", "/")
        uri_path = re.sub(r"^([a-z]:)", "/\\1", uri_path, flags=re.I)
    uri_path = re.sub(r"/+", "/", uri_path)

    # Empty netloc, params and fragment
    return urlunparse(("file", "", uri_path, "", urlencode(options), ""))