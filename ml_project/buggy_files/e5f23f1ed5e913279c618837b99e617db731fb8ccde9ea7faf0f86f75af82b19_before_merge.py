def _normalize_path(path):
    if is_remote_uri(path):
        return path
    else:
        return os.path.abspath(os.path.expanduser(path))