    def _gen_back(self, back):
        '''
        Return the backend list
        '''
        ret = []
        if not back:
            back = self.opts['fileserver_backend']
        if isinstance(back, six.string_types):
            back = back.split(',')
        if all((x.startswith('-') for x in back)):
            # Only subtracting backends from enabled ones
            ret = self.opts['fileserver_backend']
            for sub in back:
                if '{0}.envs'.format(sub[1:]) in self.servers:
                    ret.remove(sub[1:])
                elif '{0}.envs'.format(sub[1:-2]) in self.servers:
                    ret.remove(sub[1:-2])
        else:
            for sub in back:
                if '{0}.envs'.format(sub) in self.servers:
                    ret.append(sub)
                elif '{0}.envs'.format(sub[:-2]) in self.servers:
                    ret.append(sub[:-2])
        return ret