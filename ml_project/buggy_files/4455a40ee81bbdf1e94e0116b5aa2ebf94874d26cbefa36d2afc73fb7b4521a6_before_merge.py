def search(path,
        pattern,
        flags=0,
        bufsize=1,
        ):
    '''
    Search for occurances of a pattern in a file

    .. versionadded:: 0.17

    Params are identical to :py:func:`~salt.modules.file.replace`.

    CLI Example:

    .. code-block:: bash

        salt '*' file.search /etc/crontab 'mymaintenance.sh'
    '''
    # This function wraps file.replace on purpose in order to enforce
    # consistent usage, compatible regex's, expected behavior, *and* bugs. :)
    # Any enhancements or fixes to one should affect the other.
    return replace(path,
            pattern,
            '',
            flags=flags,
            bufsize=bufsize,
            dry_run=True,
            search_only=True,
            show_changes=False)