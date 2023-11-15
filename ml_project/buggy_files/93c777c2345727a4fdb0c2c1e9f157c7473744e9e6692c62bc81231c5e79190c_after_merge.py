    def send(self, x):
        iff = x.route()[0]
        if iff is None:
            iff = conf.iface
        sdto = (iff, self.type)
        self.outs.bind(sdto)
        sn = self.outs.getsockname()
        ll = lambda x: x
        if type(x) in conf.l3types:
            sdto = (iff, conf.l3types[type(x)])
        if sn[3] in conf.l2types:
            ll = lambda x: conf.l2types[sn[3]]() / x
        sx = raw(ll(x))
        try:
            self.outs.sendto(sx, sdto)
        except socket.error as msg:
            if msg.errno == 22 and len(sx) < conf.min_pkt_size:
                self.outs.send(sx + b"\x00" * (conf.min_pkt_size - len(sx)))
            elif conf.auto_fragment and msg.errno == 90:
                for p in x.fragment():
                    self.outs.sendto(raw(ll(p)), sdto)
            else:
                raise
        x.sent_time = time.time()