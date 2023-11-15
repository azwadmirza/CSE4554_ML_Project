def get_load(jid):
    '''
    Return the load data that marks a specified jid
    '''
    jid_dir = salt.utils.jid.jid_dir(jid, _job_dir(), __opts__['hash_type'])
    load_fn = os.path.join(jid_dir, LOAD_P)
    if not os.path.exists(jid_dir) or not os.path.exists(load_fn):
        return {}
    serial = salt.payload.Serial(__opts__)
    ret = {}
    with salt.utils.files.fopen(os.path.join(jid_dir, LOAD_P), 'rb') as rfh:
        ret = serial.load(rfh)
    if ret is None:
        ret = {}
    minions_cache = [os.path.join(jid_dir, MINIONS_P)]
    minions_cache.extend(
        glob.glob(os.path.join(jid_dir, SYNDIC_MINIONS_P.format('*')))
    )
    all_minions = set()
    for minions_path in minions_cache:
        log.debug('Reading minion list from %s', minions_path)
        try:
            with salt.utils.files.fopen(minions_path, 'rb') as rfh:
                all_minions.update(serial.load(rfh))
        except IOError as exc:
            salt.utils.files.process_read_exception(exc, minions_path)

    if all_minions:
        ret['Minions'] = sorted(all_minions)

    return ret