def destroy(name):
    '''
    Remove a node from Vultr
    '''
    node = show_instance(name, call='action')
    params = {'SUBID': node['SUBID']}
    result = _query('server/destroy', method='POST', decode=False, data=urllib.urlencode(params))

    # The return of a destroy call is empty in the case of a success.
    # Errors are only indicated via HTTP status code. Status code 200
    # effetively therefore means "success".
    if result.get('body') == '' and result.get('text') == '':
        return True
    return result