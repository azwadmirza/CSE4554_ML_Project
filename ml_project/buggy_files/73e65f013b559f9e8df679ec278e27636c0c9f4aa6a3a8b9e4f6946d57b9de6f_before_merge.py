def dirname(path):
    '''
    Returns the directory component of a pathname

    .. versionadded:: 2015.5.0

    This can be useful at the CLI but is frequently useful when scripting.

    .. code-block:: jinja

        {%- from salt['file.dirname'](tpldir) + '/vars.jinja' import parent_vars %}

    CLI Example:

    .. code-block:: bash

        salt '*' file.dirname 'test/path/filename.config'
    '''
    return os.path.dirname(path)