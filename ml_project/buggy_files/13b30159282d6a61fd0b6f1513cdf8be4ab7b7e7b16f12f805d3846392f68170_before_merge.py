    def parsePlotProfileData(self, f):
        d = dict()
        bin_labels = []
        bins = []
        for line in f['f'].splitlines():
            cols = line.rstrip().split("\t")
            if cols[0] == "bin labels":
                for col in cols[2:len(cols)]:
                    if col not in list(filter(None,bin_labels)):
                        bin_labels.append(col)
                    else:
                        break
            elif cols[0] == "bins":
                for col in cols[2:len(cols)]:
                    if len(bins)!=len(bin_labels):
                        bins.append(int(col))
                    else:
                        break
            else:
                s_name = self.clean_s_name(cols[0], f['root'])
                d[s_name] = dict()

                factors = {'Kb': 1e3, 'Mb': 1e6, 'Gb': 1e9}
                convert_factor = 1
                for k, v in factors.items():
                    if k in bin_labels[0]:
                        convert_factor *= v
                        start = float(bin_labels[0].strip(k)) * convert_factor
                step = int(abs(start/bin_labels.index('TSS')))
                end = step*(len(bin_labels)-bin_labels.index('TSS')-1)
                converted_bin_labels = range((int(start)+step), (int(end)+step), step)

                for i in bins:
                    d[s_name].update({converted_bin_labels[i-1]:float(cols[i+1])})

        return d, bin_labels, converted_bin_labels