    def log(self, log_file):
        mac_table = {}
        if not log_file:
            # default to FAUCET default
            log_file = '/var/log/ryu/faucet/faucet.log'
        # NOTE very fragile, prone to errors
        try:
            with open(log_file, 'r') as f:
                for line in f:
                    if 'L2 learned' in line:
                        learned_mac = line.split()
                        data = {'ip-address': learned_mac[16][0:-1],
                                'ip-state': 'L2 learned',
                                'mac': learned_mac[10],
                                'segment': learned_mac[7][1:-1],
                                'port': learned_mac[22],
                                'tenant': learned_mac[24] + learned_mac[25]}
                        if learned_mac[10] in mac_table:
                            dup = False
                            for d in mac_table[learned_mac[10]]:
                                if data == d:
                                    dup = True
                            if dup:
                                mac_table[learned_mac[10]].remove(data)
                            mac_table[learned_mac[10]].insert(0, data)
                        else:
                            mac_table[learned_mac[10]] = [data]
        except Exception as e:
            self.logger.debug("error {0}".format(str(e)))
        return mac_table