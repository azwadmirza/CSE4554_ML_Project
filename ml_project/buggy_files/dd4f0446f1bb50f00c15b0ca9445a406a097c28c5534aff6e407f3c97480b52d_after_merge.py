    def hash_file(self, path, saltenv='base', env=None):
        '''
        Return the hash of a file, to get the hash of a file on the salt
        master file server prepend the path with salt://<file on server>
        otherwise, prepend the file with / for a local file.
        '''
        if env is not None:
            salt.utils.warn_until(
                'Boron',
                'Passing a salt environment should be done using \'saltenv\' '
                'not \'env\'. This functionality will be removed in Salt '
                'Boron.'
            )
            # Backwards compatibility
            saltenv = env

        try:
            path = self._check_proto(path)
        except MinionError:
            if not os.path.isfile(path):
                err = 'Specified file {0} is not present to generate hash'
                log.warning(err.format(path))
                return {}
            else:
                ret = {}
                hash_type = self.opts.get('hash_type', 'md5')
                ret['hsum'] = salt.utils.get_hash(
                    path, form=hash_type, chunk_size=4096)
                ret['hash_type'] = hash_type
                return ret
        load = {'path': path,
                'saltenv': saltenv,
                'cmd': '_file_hash'}
        try:
            channel = salt.transport.Channel.factory(
                    self.opts,
                    auth=self.auth)
            return channel.send(load)
        except SaltReqTimeoutError:
            return ''