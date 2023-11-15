    def init_artists(self, ax, plot_args, plot_kwargs):
        box_color = plot_kwargs.pop('box_color', 'black')
        stats_color = plot_kwargs.pop('stats_color', 'black')
        facecolors = plot_kwargs.pop('facecolors', [])
        edgecolors = plot_kwargs.pop('edgecolors', 'black')
        labels = plot_kwargs.pop('labels')
        alpha = plot_kwargs.pop('alpha', 1.)
        showmedians = self.inner == 'medians'
        bw_method = self.bandwidth or 'scott'
        artists = ax.violinplot(*plot_args, bw_method=bw_method,
                               showmedians=showmedians, **plot_kwargs)
        if self.inner == 'box':
            box = ax.boxplot(*plot_args, positions=plot_kwargs['positions'],
                             showfliers=False, showcaps=False, patch_artist=True,
                             boxprops={'facecolor': box_color},
                             medianprops={'color': 'white'}, widths=0.1,
                             labels=labels)
            artists.update(box)
        for body, color in zip(artists['bodies'], facecolors):
            body.set_facecolors(color)
            body.set_edgecolors(edgecolors)
            body.set_alpha(alpha)
        for stat in ['cmedians', 'cmeans', 'cmaxes', 'cmins', 'cbars']:
            if stat in artists:
                artists[stat].set_edgecolors(stats_color)
        artists['bodies'] = artists['bodies']
        return artists