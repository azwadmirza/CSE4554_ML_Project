    def _expand_target(self):
        '''
        Figures out if the target is a reachable host without wildcards, expands if any.
        :return:
        '''
        # TODO: Support -L
        target = self.opts['tgt']
        if isinstance(target, list):
            return

        hostname = self.opts['tgt'].split('@')[-1]
        needs_expansion = '*' not in hostname and salt.utils.network.is_reachable_host(hostname)
        if needs_expansion:
            hostname = salt.utils.network.ip_to_host(hostname)
            self._get_roster()
            for roster_filename in self.__parsed_rosters:
                roster_data = self.__parsed_rosters[roster_filename]
                if not isinstance(roster_data, bool):
                    for host_id in roster_data:
                        if hostname in [host_id, roster_data.get('host')]:
                            if hostname != self.opts['tgt']:
                                self.opts['tgt'] = hostname
                            self.__parsed_rosters[self.ROSTER_UPDATE_FLAG] = False
                            return