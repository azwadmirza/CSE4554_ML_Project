def normpath(path):
    '''
    Returns Normalize path, eliminating double slashes, etc.

    .. versionadded:: 2015.5.0

    This can be useful at the CLI but is frequently useful when scripting.

    .. code-block:: jinja

        {%- from salt['file.normpath'](tpldir + '/../vars.jinja') import parent_vars %}

    CLI Example:

    .. code-block:: bash

        salt '*' file.normpath 'a/b/c/..'
    '''
    return os.path.normpath(path)