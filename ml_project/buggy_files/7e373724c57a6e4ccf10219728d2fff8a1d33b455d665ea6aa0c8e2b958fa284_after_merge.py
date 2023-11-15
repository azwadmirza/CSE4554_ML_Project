def peered(name):
    '''
    Check if node is peered.

    name
        The remote host with which to peer.

    .. code-block:: yaml

        peer-cluster:
          glusterfs.peered:
            - name: two

        peer-clusters:
          glusterfs.peered:
            - names:
              - one
              - two
              - three
              - four
    '''
    ret = {'name': name,
           'changes': {},
           'comment': '',
           'result': False}

    try:
        suc.check_name(name, 'a-zA-Z0-9._-')
    except SaltCloudException as e:
        ret['comment'] = 'Invalid characters in peer name.'
        ret['result'] = False
        return ret

    peers = __salt__['glusterfs.list_peers']()

    if peers:
        if name in peers or any([name in peers[x] for x in peers]):
            ret['result'] = True
            ret['comment'] = 'Host {0} already peered'.format(name)
            return ret

    result = __salt__['glusterfs.peer'](name)
    ret['comment'] = ''
    if 'exitval' in result:
        if int(result['exitval']) <= len(RESULT_CODES):
            ret['comment'] = RESULT_CODES[int(result['exitval'])].format(name)
        else:
            if 'comment' in result:
                ret['comment'] = result['comment']

    newpeers = __salt__['glusterfs.list_peers']()
    # if newpeers was null, we know something didn't work.
    if newpeers and name in newpeers or any([name in newpeers[x] for x in newpeers]):
        ret['result'] = True
        ret['changes'] = {'new': newpeers, 'old': peers}
    # In case the hostname doesn't have any periods in it
    elif name == socket.gethostname():
        ret['result'] = True
        return ret
    # In case they have a hostname like "example.com"
    elif name == socket.gethostname().split('.')[0]:
        ret['result'] = True
        return ret
    elif 'on localhost not needed' in ret['comment']:
        ret['result'] = True
        ret['comment'] = 'Peering with localhost is not needed'
    else:
        ret['result'] = False
    return ret