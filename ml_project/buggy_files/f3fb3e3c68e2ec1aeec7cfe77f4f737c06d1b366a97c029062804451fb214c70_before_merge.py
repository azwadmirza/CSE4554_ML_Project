def tar(options, tarfile, sources, cwd=None, template=None):
    '''
    .. note::

        This function has changed for version 0.17.0. In prior versions, the
        ``cwd`` and ``template`` arguments must be specified, with the source
        directories/files coming as a space-separated list at the end of the
        command. Beginning with 0.17.0, ``sources`` must be a comma-separated
        list, and the ``cwd`` and ``template`` arguments are optional.

    Uses the tar command to pack, unpack, etc tar files

    CLI Example:

    .. code-block:: bash

        salt '*' archive.tar cjvf /tmp/tarfile.tar.bz2 /tmp/file_1,/tmp/file_2

    The template arg can be set to ``jinja`` or another supported template
    engine to render the command arguments before execution. For example:

    .. code-block:: bash

        salt '*' archive.tar template=jinja cjvf /tmp/salt.tar.bz2 {{grains.saltpath}}

    '''
    if isinstance(sources, salt._compat.string_types):
        sources = [s.strip() for s in sources.split(',')]

    cmd = 'tar -{0} {1} {2}'.format(options, tarfile, ' '.join(sources))
    return __salt__['cmd.run'](cmd, cwd=cwd, template=template).splitlines()