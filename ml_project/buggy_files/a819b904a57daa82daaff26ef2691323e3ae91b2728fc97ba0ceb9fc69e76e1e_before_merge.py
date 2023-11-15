def contains_glob(path, glob):
    '''
    .. deprecated:: 0.17
       Use :func:`search` instead.

    Return True if the given glob matches a string in the named file

    CLI Example:

    .. code-block:: bash

        salt '*' file.contains_glob /etc/foobar '*cheese*'
    '''
    if not os.path.exists(path):
        return False

    try:
        with salt.utils.filebuffer.BufferedReader(path) as breader:
            for chunk in breader:
                if fnmatch.fnmatch(chunk, glob):
                    return True
            return False
    except (IOError, OSError):
        return False