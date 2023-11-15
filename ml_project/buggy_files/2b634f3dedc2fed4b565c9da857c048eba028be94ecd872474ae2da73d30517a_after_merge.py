    def ext_nodes(self):
        '''
        Return the metadata derived from the external nodes system on the
        master.
        '''
        load = {'cmd': '_ext_nodes',
                'id': self.opts['id'],
                'opts': self.opts,
                'tok': self.auth.gen_token('salt')}
        try:
            return self._crypted_transfer(load)
        except SaltReqTimeoutError:
            return ''