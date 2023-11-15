    def delete_key(self, match=None, match_dict=None):
        '''
        Delete public keys. If "match" is passed, it is evaluated as a glob.
        Pre-gathered matches can also be passed via "match_dict".
        '''
        if match is not None:
            matches = self.name_match(match)
        elif match_dict is not None and isinstance(match_dict, dict):
            matches = match_dict
        else:
            matches = {}
        for status, keys in matches.items():
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
        return (
            self.name_match(match) if match is not None
            else self.dict_match(matches)
        )