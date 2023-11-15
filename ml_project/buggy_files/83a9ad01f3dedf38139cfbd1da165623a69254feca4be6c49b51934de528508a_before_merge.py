def _clear_context(context):
    '''
    Clear variables stored in __context__. Run this function when a new version
    of chocolatey is installed.
    '''
    for var in (x for x in __context__ if x.startswith('chocolatey.')):
        context.pop(var)