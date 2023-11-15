def _yes():
    '''
    Returns ['--yes'] if on v0.9.9.0 or later, otherwise returns an empty list
    Confirm all prompts (--yes_ is available on v0.9.9.0 or later
    '''
    if 'chocolatey._yes' in __context__:
        return __context__['chocolatey._yes']
    if _LooseVersion(chocolatey_version()) >= _LooseVersion('0.9.9'):
        answer = ['--yes']
    else:
        answer = []
    __context__['chocolatey._yes'] = answer
    return __context__['chocolatey._yes']