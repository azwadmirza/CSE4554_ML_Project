    def quast_contigs_barplot(self):
        """ Make a bar plot showing the number and length of contigs for each assembly """

        # Prep the data
        data = dict()
        categories = []
        for s_name, d in self.quast_data.items():
            nums_by_t = dict()
            for k, v in d.items():
                m = re.match(r'# contigs \(>= (\d+) bp\)', k)
                if m and v != '-':
                    nums_by_t[int(m.groups()[0])] = int(v)

            tresholds = sorted(nums_by_t.keys(), reverse=True)
            p = dict()
            cats = []
            for i, t in enumerate(tresholds):
                if i == 0:
                    c = '>= ' + str(t) + ' bp'
                    cats.append(c)
                    p[c] = nums_by_t[t]
                else:
                    c = str(t) + '-' + str(tresholds[i - 1]) + ' bp'
                    cats.append(c)
                    p[c] = nums_by_t[t] - nums_by_t[tresholds[i - 1]]
            if not categories:
                categories = cats
            data[s_name] = p

        pconfig = {
            'id': 'quast_num_contigs',
            'title': 'QUAST: Number of Contigs',
            'ylab': '# Contigs',
            'yDecimals': False
        }

        return bargraph.plot(data, categories, pconfig)