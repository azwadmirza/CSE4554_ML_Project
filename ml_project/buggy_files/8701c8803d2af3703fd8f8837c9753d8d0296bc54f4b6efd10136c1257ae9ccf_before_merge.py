    def display_two_measurements(self, workspace, figure):
        figure.set_subplots((2, 2))
        object_name = self.object_name.value
        for i, feature_name in ((0, self.first_measurement.value),
                                (1, self.second_measurement.value)):
            axes = figure.subplot(i,0)
            saved_values = workspace.display_data.saved_values[i]
            axes.hist(saved_values[~np.isnan(saved_values)])
            axes.set_xlabel(feature_name)
            axes.set_ylabel("# of %s"%object_name)
        class_1, class_2 = workspace.display_data.in_high_class
        object_codes = class_1.astype(int)+class_2.astype(int)*2 + 1
        object_codes = np.hstack(([0], object_codes))
        nobjects = len(class_1)
        mapping = np.zeros(nobjects+1, int)
        mapping[1:] = np.arange(1, nobjects+1)
        for i in range(2): 
            saved_values = workspace.display_data.saved_values[i]
            mapping[np.isnan(saved_values)] = 0
        labels = object_codes[mapping[workspace.display_data.labels]]
        figure.subplot_imshow_labels(0,1, labels, title = object_name,
                                     renumber=False)
        #
        # Draw a 4-bar histogram
        #
        axes = figure.subplot(1,1)
        values = object_codes[1:]
        axes.hist(values[~np.isnan(values)],bins=4, range=(.5,4.5))
        axes.set_xticks((1,2,3,4))
        if self.wants_custom_names:
            axes.set_xticklabels((self.low_low_custom_name.value,
                                  self.high_low_custom_name.value,
                                  self.low_high_custom_name.value,
                                  self.high_high_custom_name.value))
        else:
            axes.set_xticklabels(("low\nlow","high\nlow","low\nhigh","high\nhigh"))
        axes.set_ylabel("# of %s"%object_name)
        colors = self.get_colors(len(axes.patches))
        #
        # The patches are the rectangles in the histogram
        #
        for i, patch in enumerate(axes.patches):
            patch.set_facecolor(colors[i+1,:])