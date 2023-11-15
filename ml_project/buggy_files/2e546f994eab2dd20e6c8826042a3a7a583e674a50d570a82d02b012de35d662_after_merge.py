    def parsePlotFingerprintOutRawCounts(self, f):
        d = dict()
        samples = []
        firstLine = True
        for line in f['f'].splitlines():
            cols = line.strip().split('\t')
            if cols[0] == "#plotFingerprint --outRawCounts":
                continue

            if firstLine:
                for c in cols:
                    c = str(c).strip("'")
                    s_name = self.clean_s_name(c, f['root'])
                    d[s_name] = []
                    samples.append(s_name)
                firstLine = False
                continue

            for idx, c in enumerate(cols):
                d[samples[idx]].append(self._int(c))

        # Switch to numpy, get the normalized cumsum
        x = np.linspace(0, len(d[samples[0]]) - 1, endpoint=True, num=100, dtype=int)  # The indices into the vectors that we'll actually return for plotting
        xp = np.arange(len(d[samples[0]]) + 1) / float(len(d[samples[0]]) + 1)
        for k, v in d.items():
            v = np.array(v)
            v = np.sort(v)
            cs = np.cumsum(v)
            cs = cs / float(cs[-1])
            # Convert for plotting
            v2 = dict()
            v2[0.0] = 0.0
            for _ in x:
                v2[xp[_]] = cs[_]
            d[k] = v2
        return d