    def quast_predicted_genes_barplot(self, partial=False):
        """
        Make a bar plot showing the number and length of predicted genes
        for each assembly
        """

        # Prep the data
        # extract the ranges given to quast with "--gene-thresholds"
        # keys look like:
        #   `# predicted genes (>= 300 bp)`
        #   `# predicted genes (>= 300 bp)_partial`
        pattern = re.compile(r'# predicted genes \(>= (\d+) bp\)' + ('_partial' if partial else ''))

        data = {}
        all_categories = []
        data_key = '# predicted genes (>= {} bp)' + ('_partial' if partial else '')
        for s_name, d in self.quast_data.items():
            thresholds = []
            for k in d.keys():
                m = re.match(pattern, k)
                if m:
                    thresholds.append(int(m.groups()[0]))
            thresholds = sorted(list(set(thresholds)))
            if len(thresholds) < 2:
                continue

            highest_threshold = thresholds[-1]
            highest_cat = (highest_threshold, '>= {} bp'.format(highest_threshold))  # tuple (key-for-sorting, label)
            all_categories.append(highest_cat)
            plot_data = { highest_cat[1]: d[data_key.format(highest_threshold)] }

            # converting >=T1, >=T2,.. into 0-T1, T1-T2,..
            for low, high in zip(thresholds[:-1], thresholds[1:]):
                cat = (low, '{}-{} bp'.format(low, high))
                all_categories.append(cat)
                plot_data[cat[1]] = d[data_key.format(low)] - d[data_key.format(high)]

            try:
                assert sum(plot_data.values()) == d[data_key.format(0)]
            except AssertionError:
                raise UserWarning("Predicted gene counts didn't add up properly for \"{}\"".format(s_name))

            data[s_name] = plot_data

        all_categories = [label for k, label in sorted(list(set(all_categories)))]

        if len(all_categories) > 0:
            return bargraph.plot(data, all_categories,
                                 {'id': 'quast_' + ('partially_' if partial else '') + 'predicted_genes',
                                  'title': 'QUAST: Number of ' + ('partially ' if partial else '') + 'predicted genes',
                                  'ylab': 'Number of ' + ('partially ' if partial else '') + 'predicted genes'})
        else:
            return None