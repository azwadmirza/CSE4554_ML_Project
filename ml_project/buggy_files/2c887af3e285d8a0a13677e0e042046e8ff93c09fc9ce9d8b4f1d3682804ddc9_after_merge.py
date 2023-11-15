def _build_sqlite_uri(filename, options):
    # In the doc mentioned below we only need to replace ? -> %3f and
    # # -> %23, but, if present, we also need to replace % -> %25 first
    # (happens when we are on a weird FS that shows urlencoded filenames
    # instead of proper ones) to not confuse sqlite.
    uri_path = filename.replace("%", "%25")

    # Convert filename to uri according to https://www.sqlite.org/uri.html, 3.1
    uri_path = uri_path.replace("?", "%3f").replace("#", "%23")
    if os.name == "nt":
        uri_path = uri_path.replace("\\", "/")
        uri_path = re.sub(r"^([a-z]:)", "/\\1", uri_path, flags=re.I)
    uri_path = re.sub(r"/+", "/", uri_path)

    # Empty netloc, params and fragment
    return urlunparse(("file", "", uri_path, "", urlencode(options), ""))