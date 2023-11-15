    def graph_options(self, element, ranges):
        if 'steps' in self.interpolation:
            element = interpolate_curve(element, interpolation=self.interpolation)
        opts = super(CurvePlot, self).graph_options(element, ranges)
        opts['mode'] = 'lines'
        style = self.style[self.cyclic_index]
        if 'line_width' in style:
            style['width'] = style.pop('line_width')
        opts['line'] = style
        return opts