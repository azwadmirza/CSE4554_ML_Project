    def fire_master(self, data, tag, preload=None):
        '''
        Fire an event off on the master server

        CLI Example::

            salt '*' event.fire_master 'stuff to be in the event' 'tag'
        '''
        load = {}
        if preload:
            load.update(preload)

        load.update({'id': self.opts['id'],
                    'tag': tag,
                    'data': data,
                    'cmd': '_minion_event'})

        sreq = salt.payload.SREQ(self.opts['master_uri'])
        try:
            sreq.send('aes', self.auth.crypticle.dumps(load))
        except Exception:
            pass
        return True