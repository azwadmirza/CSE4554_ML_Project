    def parsePlotEnrichment(self, f):
        d = {}
        firstLine = True
        for line in f['f'].splitlines():
            if firstLine:
                firstLine = False
                continue
            cols = line.strip().split("\t")

            if len(cols) != 5:
                log.warning("{} was initially flagged as the output from plotEnrichment, but that seems to not be the case. Skipping...".format(f['fn']))
                return dict()

            s_name = self.clean_s_name(cols[0], f['root'])
            if s_name not in d:
                d[s_name] = dict()
            cols[1] = str(cols[1])
            if cols[1] in d[s_name]:
                log.warning("Replacing duplicate sample:featureType {}:{}.".format(s_name, cols[1]))
            d[s_name][cols[1]] = dict()

            try:
                d[s_name][cols[1]]["percent"] = float(cols[2])
                d[s_name][cols[1]]["count"] = int(cols[3])
            except:
                log.warning("{} was initially flagged as the output from plotEnrichment, but that seems to not be the case. Skipping...".format(f['fn']))
                return dict()
        return d