def _is_hidden_osx(path):
    """Return whether or not a file is hidden on OS X.

    This uses os.lstat to work out if a file has the "hidden" flag.
    """
    file_stat = os.lstat(path)

    if hasattr(file_stat, 'st_flags') and hasattr(stat, 'UF_HIDDEN'):
        return bool(file_stat.st_flags & stat.UF_HIDDEN)
    else:
        return False