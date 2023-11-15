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
        return ret

    # Check if the name resolves to localhost
    if socket.gethostbyname(name) in __salt__['network.ip_addrs']():
        ret['result'] = True
        ret['comment'] = 'Peering with localhost is not needed'
        return ret

    peers = __salt__['glusterfs.peer_status']()

    if peers and any(name in v['hostnames'] for v in peers.values()):
        ret['result'] = True
        ret['comment'] = 'Host {0} already peered'.format(name)
        return ret

    if __opts__['test']:
        ret['comment'] = 'Peer {0} will be added.'.format(name)
        ret['result'] = None
        return ret

    peered = __salt__['glusterfs.peer'](name)
    if not peered:
        ret['comment'] = 'Failed to peer with {0}, please check logs for errors'.format(name)
        return ret

    # Double check that the action succeeded
    newpeers = __salt__['glusterfs.peer_status']()
    if newpeers and any(name in v['hostnames'] for v in newpeers.values()):
        ret['result'] = True
        ret['comment'] = 'Host {0} successfully peered'.format(name)
        ret['changes'] = {'new': newpeers, 'old': peers}
    else:
        ret['comment'] = 'Host {0} was successfully peered but did not appear in the list of peers'.format(name)
    return ret