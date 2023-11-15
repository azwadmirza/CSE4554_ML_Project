    def hash_and_stat_file(self, path, saltenv='base'):
        '''
        The same as hash_file, but also return the file's mode, or None if no
        mode data is present.
        '''
        hash_result = self.hash_file(path, saltenv)
        try:
            path = self._check_proto(path)
        except MinionError as err:
            if not os.path.isfile(path):
                return hash_result, None
            else:
                try:
                    return hash_result, list(os.stat(path))
                except Exception:
                    return hash_result, None
        load = {'path': path,
                'saltenv': saltenv,
                'cmd': '_file_find'}
        fnd = self.channel.send(load)
        try:
            stat_result = fnd.get('stat')
        except AttributeError:
            stat_result = None
        return hash_result, stat_result