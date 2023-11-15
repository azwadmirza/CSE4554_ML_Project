def _sync(form, saltenv=None):
    '''
    Sync the given directory in the given environment
    '''
    if saltenv is None:
        # No environment passed, detect them based on gathering the top files
        # from the master
        st_ = salt.state.HighState(__opts__)
        top = st_.get_top()
        if top:
            saltenv = st_.top_matches(top).keys()
        if not saltenv:
            saltenv = 'base'
    if isinstance(saltenv, string_types):
        saltenv = saltenv.split(',')
    ret = []
    remote = set()
    source = os.path.join('salt://_{0}'.format(form))
    mod_dir = os.path.join(__opts__['extension_modules'], '{0}'.format(form))
    if not os.path.isdir(mod_dir):
        log.info('Creating module dir {0!r}'.format(mod_dir))
        try:
            os.makedirs(mod_dir)
        except (IOError, OSError):
            msg = 'Cannot create cache module directory {0}. Check permissions.'
            log.error(msg.format(mod_dir))
    for sub_env in saltenv:
        log.info('Syncing {0} for environment {1!r}'.format(form, sub_env))
        cache = []
        log.info('Loading cache from {0}, for {1})'.format(source, sub_env))
        # Grab only the desired files (.py, .pyx, .so)
        cache.extend(
            __salt__['cp.cache_dir'](
                source, sub_env, include_pat=r'E@\.(pyx?|so)$'
            )
        )
        local_cache_dir = os.path.join(
                __opts__['cachedir'],
                'files',
                sub_env,
                '_{0}'.format(form)
                )
        log.debug('Local cache dir: {0!r}'.format(local_cache_dir))
        for fn_ in cache:
            if __opts__.get('file_client', '') == 'local':
                for fn_root in __opts__['file_roots'].get(sub_env, []):
                    if fn_.startswith(fn_root):
                        relpath = os.path.relpath(fn_, fn_root)
                        relpath = relpath[relpath.index('/') + 1:]
                        relname = os.path.splitext(relpath)[0].replace(
                                os.sep,
                                '.')
                        remote.add(relpath)
                        dest = os.path.join(mod_dir, relpath)
            else:
                relpath = os.path.relpath(fn_, local_cache_dir)
                relname = os.path.splitext(relpath)[0].replace(os.sep, '.')
                remote.add(relpath)
                dest = os.path.join(mod_dir, relpath)
            log.info('Copying {0!r} to {1!r}'.format(fn_, dest))
            if os.path.isfile(dest):
                # The file is present, if the sum differs replace it
                srch = hashlib.md5(
                    salt.utils.fopen(fn_, 'r').read()
                ).hexdigest()
                dsth = hashlib.md5(
                    salt.utils.fopen(dest, 'r').read()
                ).hexdigest()
                if srch != dsth:
                    # The downloaded file differs, replace!
                    shutil.copyfile(fn_, dest)
                    ret.append('{0}.{1}'.format(form, relname))
            else:
                dest_dir = os.path.dirname(dest)
                if not os.path.isdir(dest_dir):
                    os.makedirs(dest_dir)
                shutil.copyfile(fn_, dest)
                ret.append('{0}.{1}'.format(form, relname))

    touched = bool(ret)
    if __opts__.get('clean_dynamic_modules', True):
        current = set(_listdir_recursively(mod_dir))
        for fn_ in current - remote:
            full = os.path.join(mod_dir, fn_)
            if os.path.isfile(full):
                touched = True
                os.remove(full)
        #cleanup empty dirs
        while True:
            emptydirs = _list_emptydirs(mod_dir)
            if not emptydirs:
                break
            for emptydir in emptydirs:
                touched = True
                os.rmdir(emptydir)
    #dest mod_dir is touched? trigger reload if requested
    if touched:
        mod_file = os.path.join(__opts__['cachedir'], 'module_refresh')
        with salt.utils.fopen(mod_file, 'a+') as ofile:
            ofile.write('')
    return ret