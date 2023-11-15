    def parse_qorts(self, f):
        s_names = None
        for l in f['f']:
            s = l.split("\t")
            if s_names is None:
                s_names = [ self.clean_s_name(s_name, f['root']) for s_name in s[1:] ]
                if len(s_names) <= 2 and s_names[0].endswith('COUNT'):
                    if f['fn'] == 'QC.summary.txt':
                        s_names = [ self.clean_s_name( os.path.basename(os.path.normpath(f['root'])), f['root']) ]
                    else:
                        s_names = [ f['s_name'] ]
                for s_name in s_names:
                    if s_name in self.qorts_data:
                        log.debug("Duplicate sample name found! Overwriting: {}".format(s_name))
                    self.qorts_data[s_name] = dict()
            else:
                for i, s_name in enumerate(s_names):
                    self.qorts_data[s_name][s[0]] = float(s[i+1])
        # Add some extra fields
        for i, s_name in enumerate(s_names):
            if 'Genes_Total' in self.qorts_data[s_name] and 'Genes_WithNonzeroCounts' in self.qorts_data[s_name]:
                self.qorts_data[s_name]['Genes_PercentWithNonzeroCounts'] = (
                    self.qorts_data[s_name]['Genes_WithNonzeroCounts'] / self.qorts_data[s_name]['Genes_Total']
                    ) * 100.0