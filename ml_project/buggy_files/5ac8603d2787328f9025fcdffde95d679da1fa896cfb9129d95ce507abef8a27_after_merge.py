    def parseBamPEFDistributionFile(self, f):
        d = dict()
        lastsample = []
        for line in f['f'].splitlines():
            cols = line.rstrip().split("\t")
            if cols[0] == "#bamPEFragmentSize":
                continue
            elif cols[0] == "Size":
                continue
            else:
                s_name = self.clean_s_name(cols[2].rstrip().split("/")[-1], f['root'])
                if s_name != lastsample:
                    d[s_name] = dict()
                    lastsample = s_name
                d[s_name].update({self._int(cols[0]):self._int(cols[1])})

        return d