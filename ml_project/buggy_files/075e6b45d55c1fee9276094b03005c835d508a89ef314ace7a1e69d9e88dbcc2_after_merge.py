def output(data):
    '''
    The HighState Outputter is only meant to be used with the state.highstate
    function, or a function that returns highstate return data.
    '''
    # If additional information is passed through via the "data" dictionary to
    # the highstate outputter, such as "outputter" or "retcode", discard it.
    # We only want the state data that was passed through, if it is wrapped up
    # in the "data" key, as the orchestrate runner does. See Issue #31330,
    # pull request #27838, and pull request #27175 for more information.
    if 'data' in data:
        data = data.pop('data')

    for host, hostdata in six.iteritems(data):
        if not isinstance(hostdata, dict):
            # Highstate return data must be a dict, if this is not the case
            # then this value is likely a retcode.
            continue
        return _format_host(host, hostdata)[0]
    log.error(
        'Data passed to highstate outputter is not a valid highstate return: %s',
        data
    )
    # We should not reach here, but if we do return empty string
    return ''