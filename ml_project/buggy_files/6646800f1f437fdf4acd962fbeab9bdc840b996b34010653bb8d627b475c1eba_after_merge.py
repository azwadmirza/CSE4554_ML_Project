    def envs(self, back=None, sources=False):
        '''
        Return the environments for the named backend or all back-ends
        '''
        back = self._gen_back(back)
        ret = set()
        if sources:
            ret = {}
        for fsb in back:
            fstr = '{0}.envs'.format(fsb)
            if sources:
                ret[fsb] = self.servers[fstr]()
            else:
                ret.update(self.servers[fstr]())
        if sources:
            return ret
        return list(ret)