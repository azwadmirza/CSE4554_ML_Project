def clear():
    '''Empty the cache - don't use unless you really have to'''
    global cache
    cache = {}
    with open(os.path.join(rootfs.mount_dir, cache_file), 'w') as f:
        yaml.dump(cache, f, default_flow_style=False)