def _parse_uri_file(input_path):
    # '~/tmp' may be expanded to '/Users/username/tmp'
    uri_path = os.path.expanduser(input_path)

    if not uri_path:
        raise RuntimeError("invalid file URI: %s" % input_path)

    return Uri(scheme='file', uri_path=uri_path)