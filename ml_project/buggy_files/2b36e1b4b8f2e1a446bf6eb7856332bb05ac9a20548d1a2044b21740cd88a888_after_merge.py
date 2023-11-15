def makedirs_(path,
              user=None,
              group=None,
              mode=None):
    '''
    Ensure that the directory containing this path is available.

    .. note::

        The path must end with a trailing slash otherwise the directory/directories
        will be created up to the parent directory. For example if path is
        ``/opt/code``, then it would be treated as ``/opt/`` but if the path
        ends with a trailing slash like ``/opt/code/``, then it would be
        treated as ``/opt/code/``.

    CLI Example:

    .. code-block:: bash

        salt '*' file.makedirs /opt/code/
    '''
    path = os.path.expanduser(path)

    # walk up the directory structure until we find the first existing
    # directory
    dirname = os.path.normpath(os.path.dirname(path))

    if os.path.isdir(dirname):
        # There's nothing for us to do
        msg = 'Directory \'{0}\' already exists'.format(dirname)
        log.debug(msg)
        return msg

    if os.path.exists(dirname):
        msg = 'The path \'{0}\' already exists and is not a directory'.format(
            dirname
        )
        log.debug(msg)
        return msg

    directories_to_create = []
    while True:
        if os.path.isdir(dirname):
            break

        directories_to_create.append(dirname)
        current_dirname = dirname
        dirname = os.path.dirname(dirname)

        if current_dirname == dirname:
            raise SaltInvocationError(
                'Recursive creation for path \'{0}\' would result in an '
                'infinite loop. Please use an absolute path.'.format(dirname)
            )

    # create parent directories from the topmost to the most deeply nested one
    directories_to_create.reverse()
    for directory_to_create in directories_to_create:
        # all directories have the user, group and mode set!!
        log.debug('Creating directory: %s', directory_to_create)
        mkdir(directory_to_create, user=user, group=group, mode=mode)