def save():
    '''Save the cache to the cache file'''
    with open(os.path.join(rootfs.mount_dir, cache_file), 'w') as f:
        yaml.dump(cache, f, default_flow_style=False)