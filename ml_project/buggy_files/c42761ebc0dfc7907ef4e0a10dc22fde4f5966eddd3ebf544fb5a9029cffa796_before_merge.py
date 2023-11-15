    def accept(self, match, include_rejected=False):
        '''
        Accept a specified host's public key based on name or keys based on
        glob
        '''
        matches = self.name_match(match)
        keydirs = ['minions_pre']
        if include_rejected:
            keydirs.append('minions_rejected')
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
                                'minions',
                                key)
                            )
                    eload = {'result': True,
                             'act': 'accept',
                             'id': key}
                    self.event.fire_event(eload, tagify(prefix='key'))
                except (IOError, OSError):
                    pass
        return self.name_match(match)