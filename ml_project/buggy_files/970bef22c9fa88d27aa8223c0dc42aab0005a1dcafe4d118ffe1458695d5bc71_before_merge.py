def save_load(jid, clear_load):
    '''
    Save the load to the specified jid
    '''
    jid_dir = _jid_dir(jid)

    serial = salt.payload.Serial(__opts__)

    # Save the invocation information
    try:
        if not os.path.exists(jid_dir):
            os.makedirs(jid_dir)
        serial.dump(
            clear_load,
            salt.utils.fopen(os.path.join(jid_dir, LOAD_P), 'w+b')
            )
    except IOError as exc:
        log.warning('Could not write job invocation cache file: {0}'.format(exc))

    # if you have a tgt, save that for the UI etc
    if 'tgt' in clear_load:
        ckminions = salt.utils.minions.CkMinions(__opts__)
        # Retrieve the minions list
        minions = ckminions.check_minions(
                clear_load['tgt'],
                clear_load.get('tgt_type', 'glob')
                )
        # save the minions to a cache so we can see in the UI
        try:
            serial.dump(
                minions,
                salt.utils.fopen(os.path.join(jid_dir, MINIONS_P), 'w+b')
                )
        except IOError as exc:
            log.warning('Could not write job cache file for minions: {0}'.format(minions))
            log.debug('Job cache write failure: {0}'.format(exc))