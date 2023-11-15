    def reject(self, match, include_accepted=False):
        '''
        Reject a specified host's public key or keys based on a glob
        '''
        matches = self.name_match(match)
        keydirs = ['minions_pre']
        if include_accepted:
            keydirs.append('minions')
        for keydir in keydirs:
            for key in matches.get(keydir, []):
                try:
                    shutil.move(
                            os.path.join(
                                self.opts['pki_dir'],
                                keydir,
                                key),
                            os.path.join(
                                self.opts['pki_dir'],
                                'minions_rejected',
                                key)
                            )
                    eload = {'result': True,
                            'act': 'reject',
                            'id': key}
                    self.event.fire_event(eload, tagify(prefix='key'))
                except (IOError, OSError):
                    pass
        self.check_minion_cache()
        salt.crypt.dropfile(self.opts['cachedir'], self.opts['user'])
        return self.name_match(match)