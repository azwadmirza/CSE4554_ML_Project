    def update(self, back=None):
        '''
        Update all of the file-servers that support the update function or the
        named fileserver only.
        '''
        back = self._gen_back(back)
        for fsb in back:
            fstr = '{0}.update'.format(fsb)
            if fstr in self.servers:
                self.servers[fstr]()