    def display(self, workspace, figure):
        pm_dict = workspace.display_data.pm_dict
        figure.set_subplots((1, 1))
        if self.title.value != '':
            title = '%s (cycle %s)'%(self.title.value, workspace.measurements.image_set_number)
        else:
            title = '%s(%s)'%(self.agg_method, self.plot_measurement.value)
        figure.subplot_platemap(0, 0, pm_dict, self.plate_type,
                                title=title)