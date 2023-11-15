def save_load(jid, clear_load):
    '''
    Save the load to the specified jid
    '''
    jid_dir = _jid_dir(clear_load['jid'])

    serial = salt.payload.Serial(__opts__)

    # if you have a tgt, save that for the UI etc
    if 'tgt' in clear_load:
        ckminions = salt.utils.minions.CkMinions(__opts__)
        # Retrieve the minions list
        minions = ckminions.check_minions(
                clear_load['tgt'],
                clear_load.get('tgt_type', 'glob')
                )
        # save the minions to a cache so we can see in the UI
        serial.dump(
            minions,
            salt.utils.fopen(os.path.join(jid_dir, MINIONS_P), 'w+b')
            )

    # Save the invocation information
    serial.dump(
        clear_load,
        salt.utils.fopen(os.path.join(jid_dir, LOAD_P), 'w+b')
        )