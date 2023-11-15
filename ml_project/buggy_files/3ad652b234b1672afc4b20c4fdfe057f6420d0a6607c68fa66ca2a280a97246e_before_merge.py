def destroy(name):
    '''
    Remove a node from Vultr
    '''
    node = show_instance(name, call='action')
    params = {'SUBID': node['SUBID']}
    result = _query('server/destroy', method='POST', decode=False, data=urllib.urlencode(params))
    if result['body'] == '' and result['text'] == '':
        return True
    return result