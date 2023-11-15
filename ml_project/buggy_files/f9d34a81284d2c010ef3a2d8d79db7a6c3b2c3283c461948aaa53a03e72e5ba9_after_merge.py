def fire_master(data, tag, preload=None):
    '''
    Fire an event off up to the master server

    CLI Example:

    .. code-block:: bash

        salt '*' event.fire_master 'stuff to be in the event' 'tag'
    '''
    load = {}
    if preload:
        load.update(preload)

    load.update({'id': __opts__['id'],
            'tag': tag,
            'data': data,
            'cmd': '_minion_event'})

    auth = salt.crypt.SAuth(__opts__)
    sreq = salt.payload.SREQ(__opts__['master_uri'])
    try:
        sreq.send('aes', auth.crypticle.dumps(load))
    except Exception:
        pass
    return True