def set_(package, question, type, value, *extra):
    '''
    Set answers to debconf questions for a package.

    CLI Example:

    .. code-block:: bash

        salt '*' debconf.set <package> <question> <type> <value> [<value> ...]
    '''

    if extra:
        value = ' '.join((value,) + tuple(extra))

    fd_, fname = salt.utils.files.mkstemp(prefix="salt-", close_fd=False)

    line = "{0} {1} {2} {3}".format(package, question, type, value)
    os.write(fd_, salt.utils.stringutils.to_bytes(line))
    os.close(fd_)

    _set_file(fname)

    os.unlink(fname)

    return True