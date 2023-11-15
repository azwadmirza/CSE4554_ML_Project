    def display_single_measurement(self, workspace, figure):
        '''Display an array of single measurements'''
        figure.set_subplots((3, len(self.single_measurements)))
        for i, group in enumerate(self.single_measurements):
            bin_hits = workspace.display_data.bins[i]
            labels = workspace.display_data.labels[i]
            values = workspace.display_data.values[i]
            if len(values) == 0:
                continue
            #
            # A histogram of the values
            #
            axes = figure.subplot(0, i)
            axes.hist(values[~np.isnan(values)])
            axes.set_xlabel(group.measurement.value)
            axes.set_ylabel("# of %s" % group.object_name.value)
            #
            # A histogram of the labels yielding the bins
            #
            axes = figure.subplot(1, i)
            axes.hist(bin_hits, bins=group.number_of_bins(),
                      range=(.5, group.number_of_bins() + .5))
            axes.set_xticks(np.arange(1, group.number_of_bins() + 1))
            if group.wants_custom_names:
                axes.set_xticklabels(group.bin_names.value.split(","))
            axes.set_xlabel(group.measurement.value)
            axes.set_ylabel("# of %s" % group.object_name.value)
            colors = self.get_colors(len(axes.patches))
            for j, patch in enumerate(axes.patches):
                patch.set_facecolor(colors[j + 1, :])
            #
            # The labels matrix
            #
            figure.subplot_imshow_labels(2, i, labels,
                                         title=group.object_name.value,
                                         sharexy=figure.subplot(2, 0))