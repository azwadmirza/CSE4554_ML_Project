    def get_file(self,
                 path,
                 dest='',
                 makedirs=False,
                 saltenv='base',
                 gzip=None,
                 cachedir=None):
        '''
        Get a single file from the salt-master
        path must be a salt server location, aka, salt://path/to/file, if
        dest is omitted, then the downloaded file will be placed in the minion
        cache
        '''
        path, senv = salt.utils.url.split_env(path)
        if senv:
            saltenv = senv

        if not salt.utils.is_windows():
            hash_server, stat_server = self.hash_and_stat_file(path, saltenv)
            try:
                mode_server = stat_server[0]
            except (IndexError, TypeError):
                mode_server = None
        else:
            hash_server = self.hash_file(path, saltenv)
            mode_server = None

        # Check if file exists on server, before creating files and
        # directories
        if hash_server == '':
            log.debug(
                'Could not find file \'%s\' in saltenv \'%s\'',
                path, saltenv
            )
            return False

        # Hash compare local copy with master and skip download
        # if no difference found.
        dest2check = dest
        if not dest2check:
            rel_path = self._check_proto(path)

            log.debug(
                'In saltenv \'%s\', looking at rel_path \'%s\' to resolve '
                '\'%s\'', saltenv, rel_path, path
            )
            with self._cache_loc(
                    rel_path, saltenv, cachedir=cachedir) as cache_dest:
                dest2check = cache_dest

        log.debug(
            'In saltenv \'%s\', ** considering ** path \'%s\' to resolve '
            '\'%s\'', saltenv, dest2check, path
        )

        if dest2check and os.path.isfile(dest2check):
            if not salt.utils.is_windows():
                hash_local, stat_local = \
                    self.hash_and_stat_file(dest2check, saltenv)
                try:
                    mode_local = stat_local[0]
                except (IndexError, TypeError):
                    mode_local = None
            else:
                hash_local = self.hash_file(dest2check, saltenv)
                mode_local = None

            if hash_local == hash_server:
                if not salt.utils.is_windows():
                    if mode_server is None:
                        log.debug('No file mode available for \'%s\'', path)
                    elif mode_local is None:
                        log.debug(
                            'No file mode available for \'%s\'',
                            dest2check
                        )
                    else:
                        if mode_server == mode_local:
                            log.info(
                                'Fetching file from saltenv \'%s\', '
                                '** skipped ** latest already in cache '
                                '\'%s\', mode up-to-date', saltenv, path
                            )
                        else:
                            try:
                                os.chmod(dest2check, mode_server)
                                log.info(
                                    'Fetching file from saltenv \'%s\', '
                                    '** updated ** latest already in cache, '
                                    '\'%s\', mode updated from %s to %s',
                                    saltenv,
                                    path,
                                    salt.utils.st_mode_to_octal(mode_local),
                                    salt.utils.st_mode_to_octal(mode_server)
                                )
                            except OSError as exc:
                                log.warning(
                                    'Failed to chmod %s: %s', dest2check, exc
                                )
                    # We may not have been able to check/set the mode, but we
                    # don't want to re-download the file because of a failure
                    # in mode checking. Return the cached path.
                    return dest2check
                else:
                    log.info(
                        'Fetching file from saltenv \'%s\', ** skipped ** '
                        'latest already in cache \'%s\'', saltenv, path
                    )
                    return dest2check

        log.debug(
            'Fetching file from saltenv \'%s\', ** attempting ** \'%s\'',
            saltenv, path
        )
        d_tries = 0
        transport_tries = 0
        path = self._check_proto(path)
        load = {'path': path,
                'saltenv': saltenv,
                'cmd': '_serve_file'}
        if gzip:
            gzip = int(gzip)
            load['gzip'] = gzip

        fn_ = None
        if dest:
            destdir = os.path.dirname(dest)
            if not os.path.isdir(destdir):
                if makedirs:
                    os.makedirs(destdir)
                else:
                    return False
            fn_ = salt.utils.fopen(dest, 'wb+')
        else:
            log.debug('No dest file found')

        while True:
            if not fn_:
                load['loc'] = 0
            else:
                load['loc'] = fn_.tell()
            data = self.channel.send(load, raw=True)
            if six.PY3:
                # Sometimes the source is local (eg when using
                # 'salt.filesystem.FSChan'), in which case the keys are
                # already strings. Sometimes the source is remote, in which
                # case the keys are bytes due to raw mode. Standardize on
                # strings for the top-level keys to simplify things.
                data = decode_dict_keys_to_str(data)
            try:
                if not data['data']:
                    if not fn_ and data['dest']:
                        # This is a 0 byte file on the master
                        with self._cache_loc(
                                data['dest'],
                                saltenv,
                                cachedir=cachedir) as cache_dest:
                            dest = cache_dest
                            with salt.utils.fopen(cache_dest, 'wb+') as ofile:
                                ofile.write(data['data'])
                    if 'hsum' in data and d_tries < 3:
                        # Master has prompted a file verification, if the
                        # verification fails, re-download the file. Try 3 times
                        d_tries += 1
                        hsum = salt.utils.get_hash(dest, salt.utils.to_str(data.get('hash_type', b'md5')))
                        if hsum != data['hsum']:
                            log.warning(
                                'Bad download of file %s, attempt %d of 3',
                                path, d_tries
                            )
                            continue
                    break
                if not fn_:
                    with self._cache_loc(
                            data['dest'],
                            saltenv,
                            cachedir=cachedir) as cache_dest:
                        dest = cache_dest
                        # If a directory was formerly cached at this path, then
                        # remove it to avoid a traceback trying to write the file
                        if os.path.isdir(dest):
                            salt.utils.rm_rf(dest)
                        fn_ = salt.utils.fopen(dest, 'wb+')
                if data.get('gzip', None):
                    data = salt.utils.gzip_util.uncompress(data['data'])
                else:
                    data = data['data']
                fn_.write(data)
            except (TypeError, KeyError) as exc:
                try:
                    data_type = type(data).__name__
                except AttributeError:
                    # Shouldn't happen, but don't let this cause a traceback.
                    data_type = str(type(data))
                transport_tries += 1
                log.warning(
                    'Data transport is broken, got: %s, type: %s, '
                    'exception: %s, attempt %d of 3',
                    data, data_type, exc, transport_tries
                )
                self._refresh_channel()
                if transport_tries > 3:
                    log.error(
                        'Data transport is broken, got: %s, type: %s, '
                        'exception: %s, retry attempts exhausted',
                        data, data_type, exc
                    )
                    break

        if fn_:
            fn_.close()
            log.info(
                'Fetching file from saltenv \'%s\', ** done ** \'%s\'',
                saltenv, path
            )
        else:
            log.debug(
                'In saltenv \'%s\', we are ** missing ** the file \'%s\'',
                saltenv, path
            )

        if not salt.utils.is_windows():
            if mode_server is not None:
                try:
                    if os.stat(dest).st_mode != mode_server:
                        try:
                            os.chmod(dest, mode_server)
                            log.info(
                                'Fetching file from saltenv \'%s\', '
                                '** done ** \'%s\', mode set to %s',
                                saltenv,
                                path,
                                salt.utils.st_mode_to_octal(mode_server)
                            )
                        except OSError:
                            log.warning('Failed to chmod %s: %s', dest, exc)
                except OSError:
                    pass
        return dest