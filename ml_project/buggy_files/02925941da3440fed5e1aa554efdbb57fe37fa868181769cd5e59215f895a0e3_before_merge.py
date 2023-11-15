    def hash_and_stat_file(self, path, saltenv='base'):
        '''
        Return the hash of a file, to get the hash of a file in the file_roots
        prepend the path with salt://<file on server> otherwise, prepend the
        file with / for a local file.

        Additionally, return the stat result of the file, or None if no stat
        results were found.
        '''
        ret = {}
        fnd = self.__get_file_path(path, saltenv)
        if fnd is None:
            return ret, None

        try:
            # Remote file path (self._find_file() invoked)
            fnd_path = fnd['path']
            fnd_stat = fnd.get('stat')
        except TypeError:
            # Local file path
            fnd_path = fnd
            try:
                fnd_stat = list(os.stat(fnd_path))
            except Exception:
                fnd_stat = None

        hash_type = self.opts.get('hash_type', 'md5')
        ret['hsum'] = salt.utils.get_hash(fnd_path, form=hash_type)
        ret['hash_type'] = hash_type
        return ret