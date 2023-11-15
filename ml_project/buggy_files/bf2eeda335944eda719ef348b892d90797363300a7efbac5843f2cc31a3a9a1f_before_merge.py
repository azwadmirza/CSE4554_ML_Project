    def hash_file(self, path, saltenv='base', env=None):
        '''
        Return the hash of a file, to get the hash of a file in the file_roots
        prepend the path with salt://<file on server> otherwise, prepend the
        file with / for a local file.
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

        ret = {}
        try:
            path = self._check_proto(path)
        except MinionError:
            if not os.path.isfile(path):
                err = 'Specified file {0} is not present to generate hash'
                log.warning(err.format(path))
                return ret
            else:
                with salt.utils.fopen(path, 'rb') as ifile:
                    ret['hsum'] = hashlib.md5(ifile.read()).hexdigest()
                ret['hash_type'] = 'md5'
                return ret
        path = self._find_file(path, saltenv)['path']
        if not path:
            return {}
        ret = {}
        with salt.utils.fopen(path, 'rb') as ifile:
            ret['hsum'] = getattr(hashlib, self.opts['hash_type'])(
                ifile.read()).hexdigest()
        ret['hash_type'] = self.opts['hash_type']
        return ret