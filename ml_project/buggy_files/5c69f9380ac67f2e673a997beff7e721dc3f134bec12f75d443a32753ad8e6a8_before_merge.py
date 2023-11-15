def contains_regex_multiline(path, regex):
    '''
    .. deprecated:: 0.17
       Use :func:`search` instead.

    Return True if the given regular expression matches anything in the text
    of a given file

    Traverses multiple lines at a time, via the salt BufferedReader (reads in
    chunks)

    CLI Example:

    .. code-block:: bash

        salt '*' file.contains_regex_multiline /etc/crontab '^maint'
    '''
    if not os.path.exists(path):
        return False

    try:
        with salt.utils.filebuffer.BufferedReader(path) as breader:
            for chunk in breader:
                if re.search(regex, chunk, re.MULTILINE):
                    return True
            return False
    except (IOError, OSError):
        return False