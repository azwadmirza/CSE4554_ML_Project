    def reject(self, match=None, match_dict=None, include_accepted=False):
        '''
        Reject public keys. If "match" is passed, it is evaluated as a glob.
        Pre-gathered matches can also be passed via "match_dict".
        '''
        if match is not None:
            matches = self.name_match(match)
        elif match_dict is not None and isinstance(match_dict, dict):
            matches = match_dict
        else:
            matches = {}
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
        return (
            self.name_match(match) if match is not None
            else self.dict_match(matches)
        )