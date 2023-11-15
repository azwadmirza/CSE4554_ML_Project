def absent(name, bridge=None):
    '''
    Ensures that the named port exists on bridge, eventually deletes it.
    If bridge is not set, port is removed from  whatever bridge contains it.

    Args:
        name: The name of the port.
        bridge: The name of the bridge.

    '''
    ret = {'name': name, 'changes': {}, 'result': False, 'comment': ''}
    bridge_exists = False
    if bridge:
        bridge_exists = __salt__['openvswitch.bridge_exists'](bridge)
        if bridge_exists:
            port_list = __salt__['openvswitch.port_list'](bridge)
        else:
            port_list = ()
    else:
        port_list = [name]

    # Comment and change messages
    comments = {}
    comments['comment_bridge_notexists'] = 'Bridge {0} does not exist.'.format(bridge)
    comments['comment_port_notexists'] = 'Port {0} does not exist on bridge {1}.'.format(name, bridge)
    comments['comment_port_deleted'] = 'Port {0} deleted.'.format(name)
    comments['comment_port_notdeleted'] = 'Unable to delete port {0}.'.format(name)
    comments['changes_port_deleted'] = {name: {'old': 'Port named {0} may exist.'.format(name),
                                   'new': 'Deleted port {0}.'.format(name),
                                   }
                            }

    # Dry run, test=true mode
    if __opts__['test']:
        if bridge and not bridge_exists:
            ret['result'] = None
            ret['comment'] = comments['comment_bridge_notexists']
        elif name not in port_list:
            ret['result'] = True
            ret['comment'] = comments['comment_port_notexists']
        else:
            ret['result'] = None
            ret['comment'] = comments['comment_port_deleted']
        return ret

    if bridge and not bridge_exists:
        ret['result'] = False
        ret['comment'] = comments['comment_bridge_notexists']
    elif name not in port_list:
        ret['result'] = True
        ret['comment'] = comments['comment_port_notexists']
    else:
        if bridge:
            port_remove = __salt__['openvswitch.port_remove'](br=bridge, port=name)
        else:
            port_remove = __salt__['openvswitch.port_remove'](br=None, port=name)

        if port_remove:
            ret['result'] = True
            ret['comment'] = comments['comment_port_deleted']
            ret['changes'] = comments['changes_port_deleted']
        else:
            ret['result'] = False
            ret['comment'] = comments['comment_port_notdeleted']

    return ret