def create(path, saltenv=None):
    '''
    join `path` and `saltenv` into a 'salt://' URL.
    '''
    if salt.utils.is_windows():
        path = salt.utils.sanitize_win_path_string(path)
    path = sdecode(path)

    query = u'saltenv={0}'.format(saltenv) if saltenv else ''
    url = sdecode(urlunparse(('file', '', path, '', query, '')))
    return u'salt://{0}'.format(url[len('file:///'):])