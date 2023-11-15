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

    peers = __salt__['glusterfs.list_peers']()

    if peers:
        if name in peers:
            ret['result'] = True
            ret['comment'] = 'Host {0} already peered'.format(name)
            return ret
        elif __opts__['test']:
            ret['comment'] = 'Peer {0} will be added.'.format(name)
            ret['result'] = None
            return ret

    if suc.check_name(name, 'a-zA-Z0-9._-'):
        ret['comment'] = 'Invalid characters in peer name.'
        ret['result'] = False
        return ret

    if 'output' in __salt__['glusterfs.peer'](name):
        ret['comment'] = __salt__['glusterfs.peer'](name)['output']
    else:
        ret['comment'] = ''

    newpeers = __salt__['glusterfs.list_peers']()
    #if newpeers was null, we know something didn't work.
    if newpeers and name in newpeers:
        ret['result'] = True
        ret['changes'] = {'new': newpeers, 'old': peers}
    #In case the hostname doesn't have any periods in it
    elif name == socket.gethostname():
        ret['result'] = True
        return ret
    #In case they have a hostname like "example.com"
    elif name == socket.gethostname().split('.')[0]:
        ret['result'] = True
        return ret
    elif 'on localhost not needed' in ret['comment']:
        ret['result'] = True
        ret['comment'] = 'Peering with localhost is not needed'
    else:
        ret['result'] = False
    return ret