    def parseEstimateReadFilteringFile(self, f):
        d = {}
        firstLine = True
        for line in f['f'].splitlines():
            if firstLine:
                firstLine = False
                continue
            cols = line.strip().split("\t")

            if len(cols) != 12:
                # This is not really the output from estimateReadFiltering!
                log.warning("{} was initially flagged as the tabular output from estimateReadFiltering, but that seems to not be the case. Skipping...".format(f['fn']))
                return dict()

            s_name = self.clean_s_name(cols[0], f['root'])
            if s_name in d:
                log.debug("Replacing duplicate sample {}.".format(s_name))
            d[s_name] = dict()

            try:
                d[s_name]["total"] = self._int(cols[1])
                d[s_name]["mapped"] = self._int(cols[2])
                d[s_name]["blacklisted"] = self._int(cols[3])
                d[s_name]["filtered"] = float(cols[4])
                d[s_name]["mapq"] = float(cols[5])
                d[s_name]["required flags"] = float(cols[6])
                d[s_name]["excluded flags"] = float(cols[7])
                d[s_name]["internal dupes"] = float(cols[8])
                d[s_name]["dupes"] = float(cols[9])
                d[s_name]["singletons"] = float(cols[10])
                d[s_name]["strand"] = float(cols[11])
            except:
                # Obviously this isn't really the output from estimateReadFiltering
                log.warning("{} was initially flagged as the output from estimateReadFiltering, but that seems to not be the case. Skipping...".format(f['fn']))
                return dict()
        return d