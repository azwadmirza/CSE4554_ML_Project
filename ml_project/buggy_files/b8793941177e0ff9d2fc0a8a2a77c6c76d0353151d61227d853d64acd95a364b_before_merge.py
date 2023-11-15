def contains_regex(path, regex, lchar=''):
    '''
    .. deprecated:: 0.17
       Use :func:`search` instead.

    Return True if the given regular expression matches on any line in the text
    of a given file.

    If the lchar argument (leading char) is specified, it
    will strip `lchar` from the left side of each line before trying to match

    CLI Example:

    .. code-block:: bash

        salt '*' file.contains_regex /etc/crontab
    '''
    if not os.path.exists(path):
        return False

    try:
        with salt.utils.fopen(path, 'r') as target:
            for line in target:
                if lchar:
                    line = line.lstrip(lchar)
                if re.search(regex, line):
                    return True
            return False
    except (IOError, OSError):
        return False