def output(ret, bar, **kwargs):  # pylint: disable=unused-argument
    '''
    Update the progress bar
    '''
    if 'return_count' in ret:
        val = ret['return_count']
        # Avoid to fail if targets are behind a syndic. In this case actual return count will be
        # higher than targeted by MoM itself.
        # TODO: implement a way to get the proper target minions count and remove this workaround.
        # Details are in #44239.
        if val > bar.maxval:
            bar.maxval = val
        bar.update(val)
    return ''