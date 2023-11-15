    def peddy_pca_plot(self):
        ancestry_colors = {
            'SAS': 'rgb(68,1,81,1)',
            'EAS': 'rgb(59,81,139,1)',
            'AMR': 'rgb(33,144,141,1)',
            'AFR': 'rgb(92,200,99,1)',
            'EUR': 'rgb(253,231,37,1)'
        }
        background_ancestry_colors = {
            'SAS': 'rgb(68,1,81,0.1)',
            'EAS': 'rgb(59,81,139,0.1)',
            'AMR': 'rgb(33,144,141,0.1)',
            'AFR': 'rgb(92,200,99,0.1)',
            'EUR': 'rgb(253,231,37,0.1)'
        }
        default_color = '#000000'
        default_background_color = 'rgb(211,211,211,0.05)'
        data = OrderedDict()

        # plot the background data first, so it doesn't hide the actual data points
        d = self.peddy_data.pop("background_pca", {})
        if d:
            background = [{'x': pc1,
                        'y': pc2,
                        'color': default_background_color,
                        'name': ancestry,
                        'marker_size': 1}
                        for pc1, pc2, ancestry in zip(d['PC1'], d['PC2'], d['ancestry'])]
            data["background"] = background

        for s_name, d in self.peddy_data.items():
            if 'PC1_het_check' in d and 'PC2_het_check' in d:
                data[s_name] = {
                    'x': d['PC1_het_check'],
                    'y': d['PC2_het_check']
                }
                try:
                    data[s_name]['color'] = ancestry_colors.get(d['ancestry-prediction'], default_color)
                except KeyError:
                    pass

        pconfig = {
            'id': 'peddy_pca_plot',
            'title': 'Peddy: PCA Plot',
            'xlab': 'PC1',
            'ylab': 'PC2',
            'marker_size': 5,
            'marker_line_width': 0
        }

        if len(data) > 0:
            self.add_section (
                name = 'PCA Plot',
                anchor = 'peddy-pca-plot',
                plot = scatter.plot(data, pconfig)
            )