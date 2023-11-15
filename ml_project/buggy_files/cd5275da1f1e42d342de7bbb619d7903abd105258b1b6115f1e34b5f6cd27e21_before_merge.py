    def quast_predicted_genes_barplot(self):
        """
        Make a bar plot showing the number and length of predicted genes
        for each assembly
        """

        # Prep the data
        # extract the ranges given to quast with "--gene-thresholds"
        prefix = '# predicted genes (>= '
        suffix = ' bp)'
        all_thresholds = sorted(list(set([
            int(key[len(prefix):-len(suffix)])
            for _, d in self.quast_data.items()
            for key in d.keys()
            if key.startswith(prefix)
            ])))

        data = {}
        ourpat = '>= {}{} bp'
        theirpat = prefix+"{}"+suffix
        for s_name, d in self.quast_data.items():
            thresholds = sorted(list(set([
                int(key[len(prefix):-len(suffix)])
                for _, x in self.quast_data.items()
                for key in x.keys()
                if key.startswith(prefix)
            ])))
            if len(thresholds)<2: continue

            p = dict()
            try:
                p = { ourpat.format(thresholds[-1],""): d[theirpat.format(thresholds[-1])] }
                for low,high in zip(thresholds[:-1], thresholds[1:]):
                    p[ourpat.format(low,-high)] = d[theirpat.format(low)] - d[theirpat.format(high)]

                assert sum(p.values()) == d[theirpat.format(0)]
            except AssertionError:
                log.warning("Predicted gene counts didn't add up properly for \"{}\"".format(s_name))
            except KeyError:
                log.warning("Not all predicted gene thresholds available for \"{}\"".format(s_name))
            data[s_name] = p

        cats = [ ourpat.format(low,-high if high else "")
                 for low,high in zip(all_thresholds, all_thresholds[1:]+[None]) ]

        if len(cats) > 0:
            return bargraph.plot(data, cats, {'id': 'quast_predicted_genes', 'title': 'QUAST: Number of predicted genes', 'ylab': 'Number of predicted genes'})
        else:
            return None