    def hash_file(self, path, env='base'):
        '''
        Return the hash of a file, to get the hash of a file on the salt
        master file server prepend the path with salt://<file on server>
        otherwise, prepend the file with / for a local file.
        '''
        try:
            path = self._check_proto(path)
        except MinionError:
            if not os.path.isfile(path):
                err = 'Specified file {0} is not present to generate hash'
                log.warning(err.format(path))
                return {}
            else:
                ret = {}
                ret['hsum'] = salt.utils.get_hash(
                    path, form='md5', chunk_size=4096)
                ret['hash_type'] = 'md5'
                return ret
        load = {'path': path,
                'env': env,
                'cmd': '_file_hash'}
        try:
            return self._crypted_transfer(load)
        except SaltReqTimeoutError:
            return ''