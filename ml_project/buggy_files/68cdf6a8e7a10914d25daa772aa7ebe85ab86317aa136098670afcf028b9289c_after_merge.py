    def get_file(self, path, dest='', makedirs=False, env='base', gzip=None):
        '''
        Get a single file from the salt-master
        path must be a salt server location, aka, salt://path/to/file, if
        dest is omitted, then the downloaded file will be placed in the minion
        cache
        '''
        #--  Hash compare local copy with master and skip download
        #    if no diference found.
        dest2check = dest
        if not dest2check:
            rel_path = self._check_proto(path)
            with self._cache_loc(rel_path, env) as cache_dest:
                dest2check = cache_dest

        if dest2check and os.path.isfile(dest2check):
            hash_local = self.hash_file(dest2check, env)
            hash_server = self.hash_file(path, env)
            if hash_local == hash_server:
                log.info(
                    'Fetching file ** skipped **, '
                    'latest already in cache \'{0}\''.format(path))
                return dest2check

        log.debug('Fetching file ** attempting ** \'{0}\''.format(path))
        d_tries = 0
        path = self._check_proto(path)
        load = {'path': path,
                'env': env,
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
        while True:
            if not fn_:
                load['loc'] = 0
            else:
                load['loc'] = fn_.tell()
            try:
                data = self._crypted_transfer(load)
            except SaltReqTimeoutError:
                return ''

            if not data['data']:
                if not fn_ and data['dest']:
                    # This is a 0 byte file on the master
                    with self._cache_loc(data['dest'], env) as cache_dest:
                        dest = cache_dest
                        with salt.utils.fopen(cache_dest, 'wb+') as ofile:
                            ofile.write(data['data'])
                if 'hsum' in data and d_tries < 3:
                    # Master has prompted a file verification, if the
                    # verification fails, re-download the file. Try 3 times
                    d_tries += 1
                    with salt.utils.fopen(dest, 'rb') as fp_:
                        hsum = getattr(
                            hashlib,
                            data.get('hash_type', 'md5')
                        )(fp_.read()).hexdigest()
                        if hsum != data['hsum']:
                            log.warn('Bad download of file {0}, attempt {1} '
                                     'of 3'.format(path, d_tries))
                            continue
                break
            if not fn_:
                with self._cache_loc(data['dest'], env) as cache_dest:
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
        if fn_:
            fn_.close()
            log.info('Fetching file ** done ** \'{0}\''.format(path))
        return dest