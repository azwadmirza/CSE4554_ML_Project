    def compile_pillar(self):
        '''
        Return the pillar data from the master
        '''
        load = {'id': self.minion_id,
                'grains': self.grains,
                'saltenv': self.opts['environment'],
                'pillarenv': self.opts['pillarenv'],
                'pillar_override': self.pillar_override,
                'ver': '2',
                'cmd': '_pillar'}
        if self.ext:
            load['ext'] = self.ext
        ret_pillar = self.channel.crypted_transfer_decode_dictentry(load,
                                                                    dictkey='pillar',
                                                                    )

        if not isinstance(ret_pillar, dict):
            log.error(
                'Got a bad pillar from master, type {0}, expecting dict: '
                '{1}'.format(type(ret_pillar).__name__, ret_pillar)
            )
            return {}
        return decode_recursively(ret_pillar)