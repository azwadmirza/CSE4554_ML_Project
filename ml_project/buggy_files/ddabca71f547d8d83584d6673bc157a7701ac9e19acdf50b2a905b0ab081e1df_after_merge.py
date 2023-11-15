    def peddy_het_check_plot(self):
        """plot the het_check scatter plot"""
        # empty dictionary to add sample names, and dictionary of values
        data = {}

        # for each sample, and list in self.peddy_data
        for s_name, d in self.peddy_data.items():
            # check the sample contains the required columns
            if 'median_depth_het_check' in d and 'het_ratio_het_check' in d:
                # add sample to dictionary with value as a dictionary of points to plot
                data[s_name] = {
                    'x': d['median_depth_het_check'],
                    'y': d['het_ratio_het_check']
                }

        pconfig = {
            'id': 'peddy_het_check_plot',
            'title': 'Peddy: Het Check',
            'xlab': 'median depth',
            'ylab': 'proportion het calls',
        }

        if len(data) > 0:
            self.add_section (
                name = 'Het Check',
                description = "Proportion of sites that were heterozygous against median depth.",
                helptext = """
                A high proportion of heterozygous sites suggests contamination, a low proportion suggests consanguinity.

                See [the main peddy documentation](https://peddy.readthedocs.io/en/latest/output.html#het-check) for more details about the `het_check` command.
                """,
                anchor = 'peddy-hetcheck-plot',
                plot = scatter.plot(data, pconfig)
            )