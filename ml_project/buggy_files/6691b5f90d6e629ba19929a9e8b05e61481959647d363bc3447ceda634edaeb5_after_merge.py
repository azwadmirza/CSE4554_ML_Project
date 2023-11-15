    def parseBamPEFile(self, f):
        d = {}
        headers = None
        for line in f['f'].splitlines():
            cols = line.rstrip().split("\t")
            if headers is None:
                headers = cols
            else:
                s_name = None
                for idx, h in enumerate(headers):
                    if idx == 0:
                        s_name = self.clean_s_name(cols[0], f['root'])
                        if s_name in d:
                            log.debug("Replacing duplicate sample {}.".format(s_name))
                        d[s_name] = OrderedDict()
                    else:
                        if idx < 19 and cols[1] == "0":
                            # Don't store fragment metrics for SE datasets, they're just 0.
                            continue
                        try:
                            # Most values are ac
                            d[s_name][h] = self._int(cols[idx])
                        except ValueError:
                            d[s_name][h] = float(cols[idx])

        return d