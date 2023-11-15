def exists(name):
    '''
    Verify that the named file or directory is present or exists.
    Ensures pre-requisites outside of Salt's purview
    (e.g., keytabs, private keys, etc.) have been previously satisfied before
    deployment.

    name
        Absolute path which must exist
    '''
    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': ''}
    if not os.path.exists(name):
        return _error(ret, ('Specified path {0} does not exist').format(name))

    ret['comment'] = 'Path {0} exists'.format(name)
    return ret