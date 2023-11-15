def _parse_uri_file(parsed_uri):
    assert parsed_uri.scheme in (None, '', 'file')
    uri_path = parsed_uri.netloc + parsed_uri.path
    # '~/tmp' may be expanded to '/Users/username/tmp'
    uri_path = os.path.expanduser(uri_path)

    if not uri_path:
        raise RuntimeError("invalid file URI: %s" % str(parsed_uri))

    return Uri(scheme='file', uri_path=uri_path)