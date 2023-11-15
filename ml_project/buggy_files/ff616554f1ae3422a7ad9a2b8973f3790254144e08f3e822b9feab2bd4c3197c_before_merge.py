def load():
    '''Load the cache'''
    global cache

    # Do not try to populate the cache if there is no cache available
    if not os.path.exists(os.path.join(get_top_dir(), cache_file)):
        return

    with open(os.path.join(get_top_dir(), cache_file)) as f:
        cache = yaml.safe_load(f)