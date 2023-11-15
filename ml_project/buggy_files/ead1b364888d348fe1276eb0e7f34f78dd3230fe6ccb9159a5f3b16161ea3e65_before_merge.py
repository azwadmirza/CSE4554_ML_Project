    def server_list_min(self):
        '''
        List minimal information about servers
        '''
        nt_ks = self.compute_conn
        ret = {}
        for item in nt_ks.servers.list(detailed=False):
            try:
                ret[item.name] = {
                    'id': item.id,
                    'status': 'Running'
                }
            except TypeError:
                pass
        return ret