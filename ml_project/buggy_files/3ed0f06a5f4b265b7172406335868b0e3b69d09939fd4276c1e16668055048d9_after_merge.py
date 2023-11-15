    def master_tops(self):
        '''
        Return the metadata derived from the master_tops system
        '''
        load = {'cmd': '_master_tops',
                'id': self.opts['id'],
                'opts': self.opts}
        if self.auth:
            load['tok'] = self.auth.gen_token(b'salt')
        return salt.utils.data.decode(self.channel.send(load)) if six.PY2 \
            else self.channel.send(load)