    def graph_options(self, element, ranges):
        if 'steps' in self.interpolation:
            element = interpolate_curve(element, interpolation=self.interpolation)
        opts = super(CurvePlot, self).graph_options(element, ranges)
        opts['mode'] = 'lines'
        style = self.style[self.cyclic_index]
        opts['line'] = style
        return opts