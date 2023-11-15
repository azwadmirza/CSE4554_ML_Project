    def delete_key(self, match):
        '''
        Delete a single key or keys by glob
        '''
        for status, keys in self.name_match(match).items():
            for key in keys:
                try:
                    os.remove(os.path.join(self.opts['pki_dir'], status, key))
                    eload = {'result': True,
                             'act': 'delete',
                             'id': key}
                    self.event.fire_event(eload, tagify(prefix='key'))
                except (OSError, IOError):
                    pass
        self.check_minion_cache()
        salt.crypt.dropfile(self.opts['cachedir'], self.opts['user'])
        return self.list_keys()