def reap_fileserver_cache_dir(cache_base, find_func):
    '''
    Remove unused cache items assuming the cache directory follows a directory
    convention:

    cache_base -> saltenv -> relpath
    '''
    for saltenv in os.listdir(cache_base):
        env_base = os.path.join(cache_base, saltenv)
        for root, dirs, files in os.walk(env_base):
            # if we have an empty directory, lets cleanup
            # This will only remove the directory on the second time
            # "_reap_cache" is called (which is intentional)
            if len(dirs) == 0 and len(files) == 0:
                # only remove if empty directory is older than 60s
                if time.time() - os.path.getctime(root) > 60:
                    os.rmdir(root)
                continue
            # if not, lets check the files in the directory
            for file_ in files:
                file_path = os.path.join(root, file_)
                file_rel_path = os.path.relpath(file_path, env_base)
                try:
                    filename, _, hash_type = file_rel_path.rsplit('.', 2)
                except ValueError:
                    log.warn((
                        'Found invalid hash file [{0}] when attempting to reap'
                        ' cache directory.'
                    ).format(file_))
                    continue
                # do we have the file?
                ret = find_func(filename, saltenv=saltenv)
                # if we don't actually have the file, lets clean up the cache
                # object
                if ret['path'] == '':
                    os.unlink(file_path)