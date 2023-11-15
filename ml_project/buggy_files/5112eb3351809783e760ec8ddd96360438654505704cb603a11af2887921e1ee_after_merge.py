def _is_hidden_dot(path):
    """Return whether or not a file starts with a dot.

    Files starting with a dot are seen as "hidden" files on Unix-based OSes.
    """
    return os.path.basename(path).startswith(b'.')