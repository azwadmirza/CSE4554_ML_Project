    def connected_ids(self, subset=None, show_ipv4=False, include_localhost=False):
        '''
        Return a set of all connected minion ids, optionally within a subset
        '''
        minions = set()
        if self.opts.get('minion_data_cache', False):
            search = self.cache.list('minions')
            if search is None:
                return minions
            addrs = salt.utils.network.local_port_tcp(int(self.opts['publish_port']))
            if '127.0.0.1' in addrs or '0.0.0.0' in addrs:
                # Add in possible ip addresses of a locally connected minion
                addrs.discard('127.0.0.1')
                addrs.discard('0.0.0.0')
                addrs.update(set(salt.utils.network.ip_addrs(include_loopback=include_localhost)))
            if subset:
                search = subset
            for id_ in search:
                try:
                    mdata = self.cache.fetch('minions/{0}'.format(id_), 'data')
                except SaltCacheError:
                    # If a SaltCacheError is explicitly raised during the fetch operation,
                    # permission was denied to open the cached data.p file. Continue on as
                    # in the releases <= 2016.3. (An explicit error raise was added in PR
                    # #35388. See issue #36867 for more information.
                    continue
                if mdata is None:
                    continue
                grains = mdata.get('grains', {})
                for ipv4 in grains.get('ipv4', []):
                    if ipv4 == '127.0.0.1' and not include_localhost:
                        continue
                    if ipv4 == '0.0.0.0':
                        continue
                    if ipv4 in addrs:
                        if show_ipv4:
                            minions.add((id_, ipv4))
                        else:
                            minions.add(id_)
                        break
        return minions