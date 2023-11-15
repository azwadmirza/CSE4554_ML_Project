    def write(self, e):
        peerIP = e['src_ip']
        ts = e['timestamp']
        system = e['system']

        if system not in ['cowrie.ssh.factory.CowrieSSHFactory', 'cowrie.telnet.transport.HoneyPotTelnetFactory']:
            return

        today = str(datetime.now().date())

        if not self.context.get(today):
            self.context = {}
            self.context[today] = set()

        key = ','.join([peerIP, system])

        if key in self.context[today]:
            return

        self.context[today].add(key)

        tags = 'scanner,ssh'
        port = 22
        if e['system'] == 'cowrie.telnet.transport.HoneyPotTelnetFactory':
            tags = 'scanner,telnet'
            port = 23

        i = {
            'user': self.user,
            'feed': self.feed,
            'indicator': peerIP,
            'portlist': port,
            'protocol': 'tcp',
            'tags': tags,
            'firsttime': ts,
            'lasttime': ts,
            'description': self.description
        }

        ret = Indicator(self.client, i).submit()
        log.msg('logged to csirtg %s ' % ret['location'])