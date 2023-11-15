    def _init_plot(self, key, plots, ranges=None):
        """
        Initializes Bokeh figure to draw Element into and sets basic
        figure and axis attributes including axes types, labels,
        titles and plot height and width.
        """
        element = self._get_frame(key)
        subplots = list(self.subplots.values()) if self.subplots else []

        axis_types, labels, plot_ranges = self._axes_props(plots, subplots, element, ranges)
        xlabel, ylabel, zlabel = labels
        x_axis_type, y_axis_type = axis_types
        tools = self._init_tools(element)
        properties = dict(plot_ranges)
        properties['x_axis_label'] = xlabel if 'x' in self.show_labels else ' '
        properties['y_axis_label'] = ylabel if 'y' in self.show_labels else ' '

        major, minor = [int(v) for v  in bokeh.__version__.split('.')][0:2]
        if major > 0 or minor > '10':
            properties['webgl'] = True
        return bokeh.plotting.figure(x_axis_type=x_axis_type,
                                     y_axis_type=y_axis_type,
                                     tools=tools, **properties)