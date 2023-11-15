    def parsePlotPCAData(self, f):
        d = dict()
        samples = []
        for line in f['f'].splitlines():
            cols = line.strip().split('\t')
            if cols[0] == "#plotPCA --outFileNameData":
                continue
            elif cols[0] == "Component":
                for c in cols[1:(len(cols)-1)]:
                    c = str(c).strip("'")
                    s_name = self.clean_s_name(c, f['root'])
                    d[s_name] = {}
                    samples.append(s_name)
            else:
                idx = 0
                compo = cols[0]
                for c in cols[1:(len(cols)-1)]:
                    d[samples[idx]][self._int(compo)] = float(c)
                    idx += 1
        return d