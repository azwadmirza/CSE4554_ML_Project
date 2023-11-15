def cachedir_index_del(minion_id, base=None):
    '''
    Delete an entry from the cachedir index. This generally only needs to happen
    when an instance is deleted.
    '''
    base = init_cachedir(base)
    index_file = os.path.join(base, 'index.p')
    lock_file(index_file)

    if os.path.exists(index_file):
        with salt.utils.fopen(index_file, 'r') as fh_:
            index = msgpack.load(fh_)
    else:
        return

    if minion_id in index:
        del index[minion_id]

    with salt.utils.fopen(index_file, 'w') as fh_:
        msgpack.dump(index, fh_)

    unlock_file(index_file)