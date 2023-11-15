    def _gen_back(self, back):
        '''
        Return the backend list
        '''
        if not back:
            back = self.opts['fileserver_backend']
        else:
            try:
                back = back.split(',')
            except AttributeError:
                back = six.text_type(back).split(',')

        ret = []
        if not isinstance(back, list):
            return ret

        try:
            subtract_only = all((x.startswith('-') for x in back))
        except AttributeError:
            pass
        else:
            if subtract_only:
                # Only subtracting backends from enabled ones
                ret = self.opts['fileserver_backend']
                for sub in back:
                    if '{0}.envs'.format(sub[1:]) in self.servers:
                        ret.remove(sub[1:])
                    elif '{0}.envs'.format(sub[1:-2]) in self.servers:
                        ret.remove(sub[1:-2])
                return ret

        for sub in back:
            if '{0}.envs'.format(sub) in self.servers:
                ret.append(sub)
            elif '{0}.envs'.format(sub[:-2]) in self.servers:
                ret.append(sub[:-2])
        return ret