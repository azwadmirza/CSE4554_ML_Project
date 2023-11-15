def _yes(context):
    '''
    Returns ['--yes'] if on v0.9.9.0 or later, otherwise returns an empty list
    '''
    if 'chocolatey._yes' in __context__:
        return context['chocolatey._yes']
    if _LooseVersion(chocolatey_version()) >= _LooseVersion('0.9.9'):
        answer = ['--yes']
    else:
        answer = []
    context['chocolatey._yes'] = answer
    return answer