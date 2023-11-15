def output(ret, bar, **kwargs):  # pylint: disable=unused-argument
    '''
    Update the progress bar
    '''
    if 'return_count' in ret:
        bar.update(ret['return_count'])
    return ''