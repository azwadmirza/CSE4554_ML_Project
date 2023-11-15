    def route(self):
        fld, dst = self.getfield_and_val("pdst")
        fld, dst = fld._find_fld_pkt_val(self, dst)
        if isinstance(dst, Gen):
            dst = next(iter(dst))
        if isinstance(fld, IP6Field):
            return conf.route6.route(dst)
        elif isinstance(fld, IPField):
            return conf.route.route(dst)
        else:
            return None