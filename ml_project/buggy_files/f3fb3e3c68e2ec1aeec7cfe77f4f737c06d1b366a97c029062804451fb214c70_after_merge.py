def tar(options, tarfile, sources=None, dest=None, cwd=None, template=None):
    '''
    .. note::

        This function has changed for version 0.17.0. In prior versions, the
        ``cwd`` and ``template`` arguments must be specified, with the source
        directories/files coming as a space-separated list at the end of the
        command. Beginning with 0.17.0, ``sources`` must be a comma-separated
        list, and the ``cwd`` and ``template`` arguments are optional.

    Uses the tar command to pack, unpack, etc tar files


    options:
        Options to pass to the ``tar`` binary.

    tarfile:
        The tar filename to pack/unpack.

    sources:
        Comma delimited list of files to **pack** into the tarfile.

    dest:
        The destination directory to **unpack** the tarfile to.

    cwd:
        The directory in which the tar command should be executed.

    template:
         Template engine name to render the command arguments before execution.

    CLI Example:

    .. code-block:: bash

        salt '*' archive.tar cjvf /tmp/tarfile.tar.bz2 /tmp/file_1,/tmp/file_2


    The template arg can be set to ``jinja`` or another supported template
    engine to render the command arguments before execution. For example:

    .. code-block:: bash

        salt '*' archive.tar template=jinja cjvf /tmp/salt.tar.bz2 {{grains.saltpath}}


    To unpack a tarfile, for example:

    ..code-block:: bash

        salt '*' archive.tar foo.tar xf dest=/target/directory

    '''
    if sources is not None and dest is not None:
        raise SaltInvocationError(
            'The \'sources\' and \'dest\' arguments are mutually exclusive'
        )

    if isinstance(sources, salt._compat.string_types):
        sources = [s.strip() for s in sources.split(',')]

    cmd = 'tar -{0} {1}'.format(options, tarfile)
    if sources:
        cmd += ' {0}'.format(' '.join(sources))
    elif dest:
        cmd += ' -C {0}'.format(dest)
    return __salt__['cmd.run'](cmd, cwd=cwd, template=template).splitlines()